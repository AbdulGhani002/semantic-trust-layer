"""Choose the review prompt on validation rows, so the test sets stay untouched.

Each prompt reads the same validation rows, and a row counts as flagged when the
language model gives any label. Answers are saved in data/work/prompt_runs, so a
stopped run carries on from where it stopped. The attack part adds the prompt
attacks from evaluate_review.py to rows the prompt caught. The rules part works
out which decision rule to use on the chosen prompt's answers.

The two prompts in results/prompt_choice.json were attacked with the first six
attacks. The last two attacks were added later, after we found they work.

Usage: python training/compare_prompts.py PROMPT [PROMPT ...]
       python training/compare_prompts.py --attack PROMPT --rows-from PROMPT
       python training/compare_prompts.py --rules PROMPT
"""
import argparse
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "training"))

import prompt_variants  # noqa: E402
import stl.reviewer as reviewer_module  # noqa: E402
from evaluate_review import INJECTIONS  # noqa: E402

WORK = ROOT / "data" / "work"
RUNS = WORK / "prompt_runs"
RESULTS = ROOT / "results"
RATER_COLUMNS = ["toxicity", "severe_toxicity", "obscene", "threat", "insult", "identity_attack", "sexual_explicit"]
CAUGHT_GROUPS = ("threat_comment", "hate_comment", "abuse_comment", "text_fraud")
ATTACK_ROWS = 30
RULES = {
    "Fast model alone": lambda label, sure, fast: fast,
    "Any label": lambda label, sure, fast: label,
    "Sure labels only": lambda label, sure, fast: label and sure,
    "Sure, or both readers agree": lambda label, sure, fast: label and (sure or fast),
}


def rows() -> list[dict]:
    """The validation rows every prompt reads, always in the same order."""
    path = RUNS / "rows.jsonl"
    if path.exists():
        return [json.loads(line) for line in path.open(encoding="utf-8")]
    valid = pd.read_parquet(WORK / "text_valid.parquet")
    civil = valid[valid["source"] == "civil_validation"]
    texts = valid[valid["source"] == "hf_texts"]
    calm = civil[(civil["abuse"] == 0) & (civil["hate"] == 0) & (civil["threat"] == 0)]
    raw = pd.concat([pd.read_parquet(p) for p in sorted((ROOT / "data" / "raw" / "abuse_civil").glob("validation-*.parquet"))], ignore_index=True)
    clear = raw[(raw[RATER_COLUMNS] == 0).all(axis=1) & (raw["text"].str.len() >= 20)]
    parts = [
        ("calm_comment", calm["text"].sample(n=200, random_state=11)),
        ("abuse_comment", civil.loc[civil["abuse"] == 1, "text"].sample(n=70, random_state=11)),
        ("hate_comment", civil.loc[civil["hate"] == 1, "text"].sample(n=40, random_state=11)),
        ("threat_comment", civil.loc[civil["threat"] == 1, "text"].sample(n=40, random_state=11)),
        ("text_harmless", texts.loc[texts["fraud"] == 0, "text"].sample(n=40, random_state=11)),
        ("text_fraud", texts.loc[texts["fraud"] == 1, "text"].sample(n=40, random_state=11)),
        ("clear_comment", clear["text"].sample(n=150, random_state=11)),
    ]
    chosen = [{"group": group, "text": text[:500]} for group, table in parts for text in table]
    RUNS.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as sink:
        for row in chosen:
            sink.write(json.dumps(row, ensure_ascii=False) + "\n")
    return chosen


def answers(name: str) -> dict:
    path = RUNS / f"{name}.jsonl"
    if not path.exists():
        return {}
    found = {}
    for line in path.open(encoding="utf-8"):
        row = json.loads(line)
        found[(row["group"], row["text"][:300])] = row
    return found


def read_all(name: str) -> dict:
    reviewer_module.SYSTEM = getattr(prompt_variants, name)
    reviewer = reviewer_module.Reviewer(timeout=120)
    done = answers(name)
    with (RUNS / f"{name}.jsonl").open("a", encoding="utf-8") as sink:
        for row in rows():
            key = (row["group"], row["text"][:300])
            if key in done:
                continue
            answer = reviewer.review(row["text"])
            record = {"group": row["group"], "labels": (answer or {}).get("labels", []), "confidence": (answer or {}).get("confidence"), "text": row["text"][:300]}
            done[key] = record
            sink.write(json.dumps(record, ensure_ascii=False) + "\n")
            sink.flush()
    sizes, flagged = Counter(), Counter()
    for record in done.values():
        sizes[record["group"]] += 1
        flagged[record["group"]] += bool(record["labels"])
    return {group: {"flagged": flagged[group], "rows": sizes[group]} for group in sizes}


def attack(name: str, rows_from: str) -> dict:
    reviewer_module.SYSTEM = getattr(prompt_variants, name)
    reviewer = reviewer_module.Reviewer(timeout=120)
    caught = [row for row in answers(rows_from).values() if row["labels"] and row["group"] in CAUGHT_GROUPS]
    random.Random(7).shuffle(caught)
    caught = caught[:ATTACK_ROWS]
    tally = {}
    for label, template in INJECTIONS:
        fooled = 0
        for row in caught:
            answer = reviewer.review(template.replace("{text}", row["text"]))
            fooled += not (answer and answer["labels"])
        tally[label] = fooled
        print(name, label, fooled, "of", len(caught), flush=True)
    return {"rows": len(caught), "rows_from": rows_from, "fooled": tally}


def decision_rules(name: str) -> dict:
    from stl.agents import REVIEW_SURE, ApplicationAgent
    from stl.models import TextModel, UrlModel
    from stl.schema import Item

    agent = ApplicationAgent(TextModel(), UrlModel(), None)
    read = answers(name)
    flagged = {rule: Counter() for rule in RULES}
    sizes = Counter()
    for row in rows():
        answer = read[(row["group"], row["text"][:300])]
        fast = agent.inspect(Item(kind="message", text=row["text"])).risk >= 0.5
        label = bool(answer["labels"])
        sure = (answer.get("confidence") or 0.0) >= REVIEW_SURE
        sizes[row["group"]] += 1
        for rule, test in RULES.items():
            flagged[rule][row["group"]] += bool(test(label, sure, fast))
    return {"prompt": name, "sure_at": REVIEW_SURE, "rows": dict(sizes), "flagged": {rule: dict(counts) for rule, counts in flagged.items()}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompts", nargs="*")
    parser.add_argument("--attack")
    parser.add_argument("--rows-from")
    parser.add_argument("--rules")
    args = parser.parse_args()
    report_path = RESULTS / "prompt_choice.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {"prompts": {}, "attacks": {}}
    RUNS.mkdir(parents=True, exist_ok=True)
    for name in args.prompts:
        started = time.time()
        report["prompts"][name] = read_all(name)
        print(name, report["prompts"][name], round(time.time() - started), "s", flush=True)
    if args.attack:
        report["attacks"][args.attack] = attack(args.attack, args.rows_from or args.attack)
    if args.rules:
        report["rules"] = decision_rules(args.rules)
        print(report["rules"], flush=True)
    report_path.write_text(json.dumps(report, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
