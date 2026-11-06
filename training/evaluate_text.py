"""Measure the Application Agent on data it never trained on.

Compares a keyword filter, a linear model and the transformer, then adds the
language model on the hand-written semantic test. The keyword filter exists
only as the baseline that STL is meant to beat.
"""
import csv
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_recall_fscore_support

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from stl.agents import ApplicationAgent  # noqa: E402
from stl.extract import looks_english  # noqa: E402
from stl.models import TextModel, UrlModel  # noqa: E402
from stl.reviewer import Reviewer  # noqa: E402
from stl.schema import Item  # noqa: E402

WORK = ROOT / "data" / "work"
RESULTS = ROOT / "results"
LABELS = ["threat", "hate", "abuse", "fraud"]
KEYWORDS = {
    "threat": r"\b(kill|murder|shoot|stab|bomb|burn|hurt|beat you|break your|attack you|destroy you|die)\b",
    "hate": r"\b(racist|terrorist|nazi|subhuman|vermin|savage|faggot|nigger|nigga|kike|chink|retard)\b",
    "abuse": r"\b(idiot|stupid|moron|loser|dumb|fool|pathetic|worthless|bastard|bitch|shit|fuck|asshole|crap)\b",
    "fraud": r"\b(verify|account|password|urgent|winner|prize|lottery|click|bank|login|otp|suspended|congratulations|free)\b",
}
GATES = (0.0, 0.005, 0.02, 0.08, 0.3)
SAMPLES = (
    ("Threat, Civil Comments", "abuse_civil", "threat"),
    ("Hate, Civil Comments", "abuse_civil", "hate"),
    ("Abuse, Civil Comments", "abuse_civil", "abuse"),
    ("Hate, unseen source", "hate_unseen_source", "hate"),
    ("Fraud email, unseen source", "fraud_email_unseen_source", "fraud"),
    ("SMS, unseen messages", "sms_unseen", "fraud"),
    ("Abuse, Roman Urdu", "roman_urdu", "abuse"),
)
SAMPLE_SIZE = 75
CLEAR_SIZE = 300
RATER_COLUMNS = ["toxicity", "severe_toxicity", "obscene", "threat", "insult", "identity_attack", "sexual_explicit"]
TESTS = {
    "abuse_civil": ["threat", "hate", "abuse"],
    "hate_unseen_source": ["hate"],
    "fraud_email_unseen_source": ["fraud"],
    "sms_unseen": ["fraud"],
    "roman_urdu": ["abuse"],
}


def scores_at(y, predicted, score):
    precision, recall, f1, _ = precision_recall_fscore_support(y, predicted, average="binary", zero_division=0)
    negatives = y == 0
    return {
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "false_alarm_rate": round(float(predicted[negatives].mean()) if negatives.any() else 0.0, 4),
        "average_precision": round(float(average_precision_score(y, score)), 4) if score is not None and y.sum() else None,
        "positives": int(y.sum()),
        "rows": int(len(y)),
    }


def keyword_flags(texts: list[str], label: str) -> np.ndarray:
    pattern = re.compile(KEYWORDS[label], re.IGNORECASE)
    return np.array([bool(pattern.search(text)) for text in texts], dtype=np.int32)


def linear_baseline():
    train = pd.read_parquet(WORK / "text_train.parquet")
    print("training linear baseline", flush=True)
    vectorizer = TfidfVectorizer(max_features=200_000, ngram_range=(1, 2), min_df=3, sublinear_tf=True)
    matrix = vectorizer.fit_transform(train["text"])
    models = {}
    for label in LABELS:
        known = train[label].to_numpy() >= 0
        model = LogisticRegression(max_iter=300, class_weight="balanced", C=4.0)
        model.fit(matrix[known], train.loc[known, label].astype(int))
        models[label] = model
    return vectorizer, models


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    model = TextModel()
    vectorizer, linear = linear_baseline()
    report = {"thresholds": model.thresholds, "datasets": {}}
    for name, labels in TESTS.items():
        table = pd.read_parquet(WORK / f"text_test_{name}.parquet")
        if len(table) > 60_000:
            table = table.sample(n=60_000, random_state=7).reset_index(drop=True)
        started = time.time()
        scores = model.score_many(table["text"].tolist())
        seconds = time.time() - started
        matrix = vectorizer.transform(table["text"])
        report["datasets"][name] = {"rows": len(table), "ms_per_item": round(1000 * seconds / len(table), 2), "labels": {}}
        for label in labels:
            index = LABELS.index(label)
            known = table[label].to_numpy() >= 0
            y = table.loc[known, label].to_numpy().astype(int)
            texts = table.loc[known, "text"].tolist()
            score = scores[known, index]
            line = linear[label].predict_proba(matrix[known])[:, 1]
            report["datasets"][name]["labels"][label] = {
                "keyword_filter": scores_at(y, keyword_flags(texts, label), None),
                "linear_tfidf": scores_at(y, (line >= 0.5).astype(int), line),
                "transformer": scores_at(y, (score >= model.thresholds[label]).astype(int), score),
            }
        print(name, json.dumps(report["datasets"][name]["labels"]), flush=True)

    def save() -> None:
        (RESULTS / "text.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")

    save()
    report["semantic_test"] = semantic_test(model)
    save()
    report["held_out_sample"] = held_out_sample(model)
    save()
    report["clear_comments"] = clear_comments(model)
    save()
    print("saved results/text.json", flush=True)


def held_out_sample(model: TextModel) -> dict:
    """Run the language model on real held-out text.

    Harmful rows carry the label. Harmless rows carry no harmful label at all.
    A row counts when the system would flag it, for any label. The sample is
    balanced, so precision here means little.
    """
    reviewer = Reviewer(timeout=120)
    if not reviewer.available():
        return {}
    agent = ApplicationAgent(model, UrlModel(), reviewer)
    rows = []
    for name, source, label in SAMPLES:
        table = pd.read_parquet(WORK / f"text_test_{source}.parquet")
        bad = table[table[label] == 1]
        good = table[(table[label] == 0) & (table[LABELS] <= 0).all(axis=1)]
        size = min(SAMPLE_SIZE, len(bad), len(good))
        chosen = pd.concat([bad.sample(n=size, random_state=7), good.sample(n=size, random_state=7)])
        counts = {"fast_caught": 0, "both_caught": 0, "fast_wrong": 0, "both_wrong": 0}
        started = time.time()
        for text, truth in zip(chosen["text"], chosen[label]):
            item = Item(kind="message", text=text)
            first = agent.inspect(item)
            fast = first.risk
            final = agent.second_look(item, first, None)
            side = "caught" if truth == 1 else "wrong"
            counts[f"fast_{side}"] += bool(fast >= 0.5)
            counts[f"both_{side}"] += bool(final.risk >= 0.5)
        rows.append({"name": name, "size_each": size, "seconds_each": round((time.time() - started) / (2 * size), 2), **counts})
        print(rows[-1], flush=True)
    return {"rows": rows}


def clear_comments(model: TextModel) -> dict:
    """Comments no rater objected to, so a flag here is a real false alarm and not a borderline label."""
    reviewer = Reviewer(timeout=120)
    if not reviewer.available():
        return {}
    agent = ApplicationAgent(model, UrlModel(), reviewer)
    files = sorted((ROOT / "data" / "raw" / "abuse_civil").glob("test-*.parquet"))
    raw = pd.concat([pd.read_parquet(path) for path in files], ignore_index=True)
    clear = raw[(raw[RATER_COLUMNS] == 0).all(axis=1) & (raw["text"].str.len() >= 20)]
    fast_flagged = both_flagged = 0
    for text in clear["text"].sample(n=CLEAR_SIZE, random_state=7):
        item = Item(kind="message", text=text)
        first = agent.inspect(item)
        fast = first.risk
        final = agent.second_look(item, first, None)
        fast_flagged += bool(fast >= 0.5)
        both_flagged += bool(final.risk >= 0.5)
    print("clear comments", fast_flagged, both_flagged, "of", CLEAR_SIZE, flush=True)
    return {"size": CLEAR_SIZE, "share_of_test": round(len(clear) / len(raw), 3), "fast_flagged": fast_flagged, "both_flagged": both_flagged}


def gate_table(agent: ApplicationAgent, rows: list[dict]) -> list[dict]:
    """Work out what each review gate would have cost and saved."""
    mail = pd.read_parquet(WORK / "text_test_fraud_email_unseen_source.parquet")
    comments = pd.read_parquet(WORK / "text_test_abuse_civil.parquet")
    calm = comments[(comments["abuse"] == 0) & (comments["hate"] == 0) & (comments["threat"] == 0)]
    normal_mail = [agent.inspect(Item(kind="message", text=text)).risk for text in mail.loc[mail["fraud"] == 0, "text"].sample(n=400, random_state=7)]
    normal_comments = [agent.inspect(Item(kind="message", text=text)).risk for text in calm["text"].sample(n=400, random_state=7)]
    harmful = [row for row in rows if row["expected"] == "flag"]
    harmless = [row for row in rows if row["expected"] != "flag"]
    table = []
    for gate in GATES:
        def outcome(row):
            read = row["risk"] >= gate or not looks_english(row["text"])
            return row["combined"] if read else row["transformer"]

        table.append(
            {
                "gate": gate,
                "caught": f"{sum(outcome(row) for row in harmful)}/{len(harmful)}",
                "false_alarms": f"{sum(outcome(row) for row in harmless)}/{len(harmless)}",
                "normal_mail_read": round(float(np.mean([risk >= gate for risk in normal_mail])), 3),
                "normal_comments_read": round(float(np.mean([risk >= gate for risk in normal_comments])), 3),
            }
        )
    return table


def semantic_test(model: TextModel) -> dict:
    slur = "n" + "igga"
    hidden = "n" + "1gg@"
    rows = []
    with (ROOT / "tests" / "fixtures" / "messages.csv").open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            row["text"] = row["text"].replace("{SLUR}", slur).replace("{SLUR_OBFUSCATED}", hidden)
            rows.append(row)
    reviewer = Reviewer(timeout=120)
    use_review = reviewer.available()
    texts = [row["text"] for row in rows]
    agent = ApplicationAgent(model, UrlModel(), reviewer if use_review else None)
    keyword_any = np.max([keyword_flags(texts, label) for label in LABELS], axis=0)
    for index, row in enumerate(rows):
        item = Item(kind="message", text=row["text"])
        first = agent.inspect(item)
        row["keyword"] = bool(keyword_any[index])
        row["transformer"] = bool(first.risk >= 0.5)
        row["risk"] = round(first.risk, 3)
        row["combined"] = row["transformer"]
        if agent.needs_review(first, None, row["text"]):
            started = time.time()
            final = agent.second_look(item, first, None)
            row["review_seconds"] = round(time.time() - started, 2)
            row["review_labels"] = [key[7:] for key in final.scores if key.startswith("review_") and key != "review_confidence"]
            row["combined"] = bool(final.risk >= 0.5)
            row["final_risk"] = round(final.risk, 3)

    def tally(field, subset):
        expected = np.array([row["expected"] == "flag" for row in subset])
        got = np.array([row[field] for row in subset])
        tp = int((expected & got).sum())
        fn = int((expected & ~got).sum())
        fp = int((~expected & got).sum())
        tn = int((~expected & ~got).sum())
        return {
            "recall": round(tp / max(1, tp + fn), 3),
            "false_alarm_rate": round(fp / max(1, fp + tn), 3),
            "caught": f"{tp}/{tp + fn}",
            "false_alarms": f"{fp}/{fp + tn}",
        }

    methods = ("keyword", "transformer", "combined")
    summary = {"all": {m: tally(m, rows) for m in methods}}
    for language in ("en", "ru", "ur"):
        subset = [row for row in rows if row["language"] == language]
        summary[f"language_{language}"] = {m: tally(m, subset) for m in methods}
    subset = [row for row in rows if row["kind"] in ("veiled", "implicit", "polite", "no_link", "obfuscated")]
    summary["no_obvious_keyword"] = {m: tally(m, subset) for m in methods}
    summary["language_model_used"] = use_review
    summary["reviewed_items"] = sum("review_seconds" in row for row in rows)
    summary["median_review_seconds"] = round(float(np.median([row["review_seconds"] for row in rows if "review_seconds" in row] or [0])), 2)
    summary["gates"] = gate_table(ApplicationAgent(model, UrlModel(), None), rows)
    summary["rows"] = [
        {key: row.get(key) for key in ("id", "expected", "label", "language", "kind", "risk", "keyword", "transformer", "combined", "review_labels")}
        for row in rows
    ]
    return summary


if __name__ == "__main__":
    main()
