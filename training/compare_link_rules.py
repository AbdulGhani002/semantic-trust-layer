"""Choose how a bare link is judged, on validation links only. No link is ever opened."""
import json
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from stl.agents import ONE_READER_CAP, REVIEW_SURE, WARN_FLOOR  # noqa: E402
from stl.models import UrlModel, risk_from_score  # noqa: E402
from stl.reviewer import Reviewer  # noqa: E402

WORK = ROOT / "data" / "work"
RUNS = WORK / "link_rule_runs.jsonl"
OUT = ROOT / "results" / "link_rule_choice.json"
EACH = 150
POPULAR = 80


def pick() -> pd.DataFrame:
    valid = pd.read_parquet(WORK / "url_valid.parquet")
    bad = valid[valid["label"] == 1].sample(n=EACH, random_state=7).assign(group="phishing")
    good = valid[valid["label"] == 0].sample(n=EACH, random_state=7)
    popular = valid[(valid["source"] == "tranco") & ~valid.index.isin(good.index)].sample(n=POPULAR, random_state=7).assign(group="popular_normal")
    return pd.concat([bad, good.assign(group="normal"), popular], ignore_index=True)


def read_all(rows: pd.DataFrame) -> list[dict]:
    done = {}
    if RUNS.exists():
        for line in RUNS.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            done[row["url"]] = row
    model = UrlModel()
    reviewer = Reviewer(timeout=120)
    started = time.time()
    with RUNS.open("a", encoding="utf-8") as handle:
        for index, row in enumerate(rows.itertuples()):
            if row.url in done:
                continue
            score = float(model.score_many([row.url])[0])
            message = f"\nLinks: {row.url}"
            outcome = reviewer.review(message) or reviewer.review(message) or {"labels": [], "confidence": 0.0, "reason": "no answer"}
            record = {"url": row.url, "group": row.group, "label": int(row.label), "source": row.source, "risk": risk_from_score(score, model.threshold), "labels": outcome["labels"], "confidence": outcome["confidence"], "reason": outcome["reason"]}
            done[row.url] = record
            handle.write(json.dumps(record) + "\n")
            handle.flush()
            if index % 25 == 0:
                print(index, "of", len(rows), round(time.time() - started), "s", flush=True)
    return [done[url] for url in rows["url"]]


def link_alone(row: dict) -> float:
    return row["risk"]


def present(row: dict) -> float:
    """The rule used for content."""
    own, confidence = row["risk"], row["confidence"]
    if row["labels"]:
        reviewed = 0.5 + 0.5 * confidence
        if own >= 0.5:
            return max(own, reviewed)
        return min(reviewed, ONE_READER_CAP) if confidence >= REVIEW_SURE else max(own, WARN_FLOOR)
    floor = WARN_FLOOR if own >= 0.5 else 0.0
    return max(floor, min(own, 0.5 * (1 - confidence)))


def must_agree(row: dict) -> float:
    """A bare link is flagged only when both readers agree. Either alone warns."""
    own = row["risk"]
    if row["labels"]:
        return max(own, 0.5 + 0.5 * row["confidence"]) if own >= 0.5 else max(own, WARN_FLOOR)
    return max(WARN_FLOOR, min(own, 0.5 * (1 - row["confidence"]))) if own >= 0.5 else own


def can_only_clear(row: dict) -> float:
    """The language model can lower a link flag to a warning, and it adds nothing alone."""
    own = row["risk"]
    if own >= 0.5 and not row["labels"]:
        return WARN_FLOOR
    return own


def can_only_add(row: dict) -> float:
    """The language model never lowers the link model. It can add a warning."""
    return max(row["risk"], WARN_FLOOR) if row["labels"] else row["risk"]


RULES = {
    "Link model alone": link_alone,
    "Same rule as content": present,
    "Both must agree": must_agree,
    "Language model only clears": can_only_clear,
    "Language model only warns": can_only_add,
}


def main() -> None:
    rows = read_all(pick())
    report = {"rows": {}, "rules": {}}
    groups = ("phishing", "normal", "popular_normal")
    for group in groups:
        report["rows"][group] = sum(row["group"] == group for row in rows)
    for name, rule in RULES.items():
        report["rules"][name] = {
            group: {
                "flagged": sum(rule(row) >= 0.5 for row in rows if row["group"] == group),
                "warned_or_more": sum(rule(row) >= 0.3 for row in rows if row["group"] == group),
            }
            for group in groups
        }
    OUT.write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
