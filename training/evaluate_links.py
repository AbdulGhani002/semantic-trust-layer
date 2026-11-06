"""Measure the link model and QR handling. No link is ever opened."""
import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, precision_recall_fscore_support

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from stl.agents import ApplicationAgent  # noqa: E402
from stl.extract import read_qr  # noqa: E402
from stl.models import TextModel, UrlModel  # noqa: E402
from stl.reviewer import Reviewer  # noqa: E402
from stl.schema import Item  # noqa: E402

WORK = ROOT / "data" / "work"
FIXTURES = ROOT / "tests" / "fixtures"
RESULTS = ROOT / "results"
LINK_SAMPLE = 150


def measure(y: np.ndarray, score: np.ndarray, threshold: float) -> dict:
    predicted = (score >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(y, predicted, average="binary", zero_division=0)
    negative = y == 0
    return {
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "false_alarm_rate": round(float(predicted[negative].mean()), 4) if negative.any() else None,
        "average_precision": round(float(average_precision_score(y, score)), 4) if negative.any() and y.sum() else None,
        "rows": int(len(y)),
        "phishing": int(y.sum()),
    }


def scored(model: UrlModel, urls: list[str], batch: int = 2048) -> np.ndarray:
    return np.concatenate([model.score_many(urls[i : i + batch]) for i in range(0, len(urls), batch)])


def fresh_feed(known: set[str], model: UrlModel) -> dict:
    """Fetch the feed again now, and test links that appeared after training."""
    from prepare_urls import domain_of, normalise

    request = urllib.request.Request("https://openphish.com/feed.txt", headers={"User-Agent": "stl-research/0.1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        lines = response.read().decode("utf-8", "ignore").splitlines()
    urls = [line for line in lines if line.strip()]
    first = set((ROOT / "data" / "raw" / "feed_openphish" / "feed.txt").read_text(encoding="utf-8", errors="ignore").splitlines())
    new = [url for url in urls if url not in first and domain_of(normalise(url)) not in known]
    if not new:
        return {"rows": 0, "note": "no new links on unseen domains"}
    score = model.score_many(new)
    return {"rows": len(new), "recall": round(float((score >= model.threshold).mean()), 4), "retrieved": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())}


def fixture_links(text: TextModel | None, model: UrlModel, reviewer: Reviewer | None) -> dict:
    with (FIXTURES / "links.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    score = model.score_many([row["url"] for row in rows])
    flagged = score >= model.threshold
    y = np.array([row["label"] == "fraud" for row in rows])
    reviewed = {}
    if reviewer is not None:
        agent = ApplicationAgent(text, model, reviewer)
        final = []
        for row in rows:
            item = Item(kind="message", urls=[row["url"]])
            final.append(agent.second_look(item, agent.inspect(item), None).risk >= 0.5)
        final = np.array(final)
        reviewed = {
            "with_language_model_caught": f"{int((final & y).sum())}/{int(y.sum())}",
            "with_language_model_false_alarms": f"{int((final & ~y).sum())}/{int((~y).sum())}",
            "with_language_model_missed": [row["url"] for row, hit, bad in zip(rows, final, y) if bad and not hit][:20],
            "with_language_model_wrong": [row["url"] for row, hit, bad in zip(rows, final, y) if hit and not bad][:20],
        }
    by_kind = {}
    for kind in sorted({row["kind"] for row in rows}):
        chosen = np.array([row["kind"] == kind for row in rows])
        by_kind[kind] = f"{int(flagged[chosen].sum())}/{int(chosen.sum())}"
    return {
        "fraud_caught": f"{int((flagged & y).sum())}/{int(y.sum())}",
        "normal_false_alarms": f"{int((flagged & ~y).sum())}/{int((~y).sum())}",
        "flagged_by_kind": by_kind,
        "missed": [row["url"] for row, hit, bad in zip(rows, flagged, y) if bad and not hit][:20],
        "false_alarms": [row["url"] for row, hit, bad in zip(rows, flagged, y) if hit and not bad][:20],
        **reviewed,
    }


def held_out_sample(text: TextModel | None, model: UrlModel, reviewer: Reviewer, test: pd.DataFrame) -> dict:
    """Run the language model on real held-out links. They are read as text and never opened."""
    agent = ApplicationAgent(text, model, reviewer)
    counts = {"fast_caught": 0, "both_caught": 0, "fast_wrong": 0, "both_wrong": 0}
    missed, wrong = [], []
    started = time.time()
    for label, side in ((1, "caught"), (0, "wrong")):
        for url in test.loc[test["label"] == label, "url"].sample(n=LINK_SAMPLE, random_state=7):
            item = Item(kind="message", urls=[url])
            first = agent.inspect(item)
            fast = first.risk
            final = agent.second_look(item, first, None)
            counts[f"fast_{side}"] += bool(fast >= 0.5)
            counts[f"both_{side}"] += bool(final.risk >= 0.5)
            if label == 1 and final.risk < 0.5:
                missed.append(url)
            if label == 0 and final.risk >= 0.5:
                wrong.append(url)
    print("held-out sample", counts, flush=True)
    return {
        "size_each": LINK_SAMPLE, "seconds_each": round((time.time() - started) / (2 * LINK_SAMPLE), 2), **counts,
        "missed": [url[:80] for url in missed[:15]], "wrong": [url[:80] for url in wrong[:15]],
    }


def fixture_qr(text: TextModel | None, model: UrlModel, reviewer: Reviewer | None) -> dict:
    agent = ApplicationAgent(text, model, reviewer)
    settled: dict[tuple, float] = {}
    with (FIXTURES / "qr" / "manifest.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    read_ok, right = 0, 0
    by_variant: dict[str, list[int]] = {}
    wrong = []
    reading = 0.0
    for row in rows:
        data = (FIXTURES / "qr" / row["file"]).read_bytes()
        began = time.perf_counter()
        payloads = read_qr(data)
        reading += time.perf_counter() - began
        ok = payloads == [row["payload"]]
        read_ok += ok
        key = tuple(payloads)
        if key not in settled:
            item = Item(kind="qr", qr_payloads=payloads)
            settled[key] = agent.second_look(item, agent.inspect(item), None).risk
        risk = settled[key]
        correct = (risk >= 0.5) == (row["label"] == "fraud")
        right += correct
        stats = by_variant.setdefault(row["variant"], [0, 0])
        stats[0] += correct
        stats[1] += 1
        if not correct and row["variant"] == "clean":
            wrong.append({"name": row["name"], "kind": row["kind"], "risk": round(risk, 3)})
    return {
        "images": len(rows),
        "read_correctly": read_ok,
        "verdict_correct": right,
        "by_variant": {k: f"{v[0]}/{v[1]}" for k, v in by_variant.items()},
        "wrong_clean_codes": wrong,
        "ms_per_image": round(1000 * reading / len(rows), 1),
    }


def main() -> None:
    sys.path.insert(0, str(ROOT / "training"))
    RESULTS.mkdir(exist_ok=True)
    model = UrlModel()
    report = {"threshold": model.threshold}
    test = pd.read_parquet(WORK / "url_test.parquet")
    started = time.time()
    score = scored(model, test["url"].tolist())
    report["ms_per_1000_links"] = round(1000 * (time.time() - started) / len(test) * 1000, 1)
    report["held_out_domains"] = measure(test["label"].to_numpy(), score, model.threshold)
    report["by_source"] = {}
    for (source, label), part in test.groupby(["source", "label"]):
        rows = part.index.to_numpy()
        share = float((score[test.index.get_indexer(rows)] >= model.threshold).mean())
        report["by_source"][f"{source}_{'phishing' if label else 'normal'}"] = {"rows": len(part), "flagged": round(share, 4)}
    fresh = pd.read_parquet(WORK / "url_test_openphish_unseen.parquet")
    fresh_score = scored(model, fresh["url"].tolist())
    report["openphish_unseen_domains"] = {"rows": len(fresh), "recall": round(float((fresh_score >= model.threshold).mean()), 4)}
    known = set(pd.read_parquet(WORK / "url_train.parquet", columns=["domain"])["domain"])
    try:
        report["openphish_after_training"] = fresh_feed(known, model)
    except OSError as error:
        report["openphish_after_training"] = {"error": str(error)}
    text = TextModel() if (ROOT / "models" / "text" / "meta.json").exists() else None
    reviewer = Reviewer(timeout=120)
    reviewer = reviewer if reviewer.available() else None
    report["language_model"] = reviewer.model if reviewer else None
    if reviewer is not None:
        report["language_model_sample"] = held_out_sample(text, model, reviewer, test)
    report["fixture_links"] = fixture_links(text, model, reviewer)
    report["fixture_qr"] = fixture_qr(text, model, reviewer)
    (RESULTS / "links.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
