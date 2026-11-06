"""Find training rows that repeat text from the unseen-source tests."""
import re
from pathlib import Path

import pandas as pd

WORK = Path(__file__).resolve().parent.parent / "data" / "work"
SIZE = 50
STEP = 25


def squash(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def main() -> None:
    train = pd.read_parquet(WORK / "text_train.parquet")
    test = pd.read_parquet(WORK / "text_test_fraud_email_unseen_source.parquet")
    print(test["source"].value_counts().to_dict())
    shingles = {}
    for source, part in test.groupby("source"):
        bag = set()
        for text in part["text"]:
            body = squash(text)
            bag.update(body[i : i + SIZE] for i in range(0, max(1, len(body) - SIZE), STEP))
        shingles[source] = bag
        print(source, len(bag), "shingles", flush=True)
    for source in ("hf_texts", "CEAS_08", "Enron", "TREC_06", "Ling", "SpamAssasin", "sms_uci"):
        part = train[train["source"] == source]
        hits = {name: 0 for name in shingles}
        for text in part["text"]:
            body = squash(text)
            windows = {body[i : i + SIZE] for i in range(0, max(1, len(body) - SIZE))}
            for name, bag in shingles.items():
                if windows & bag:
                    hits[name] += 1
        print(source, len(part), hits, flush=True)
    sample = train[train["source"] == "hf_texts"].sample(6, random_state=1)
    for _, row in sample.iterrows():
        print(int(row["fraud"]), repr(row["text"][:110]))


if __name__ == "__main__":
    main()
