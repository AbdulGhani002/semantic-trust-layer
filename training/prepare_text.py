"""Build the labelled text sets for the Application Agent.

Labels are threat, hate, abuse and fraud. -1 means the source says nothing
about that label, so training ignores it. Whole sources are kept out of
training so the test scores show how the model handles unseen sources.
"""
import csv
import json
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
WORK = ROOT / "data" / "work"
LABELS = ["threat", "hate", "abuse", "fraud"]
SEED = 7
MAX_CHARS = 1800
SHINGLE = 50


def frame(text, threat, hate, abuse, fraud, source) -> pd.DataFrame:
    table = pd.DataFrame({"text": text, "threat": threat, "hate": hate, "abuse": abuse, "fraud": fraud})
    table["source"] = source
    table["text"] = table["text"].astype(str).str.strip().str.slice(0, MAX_CHARS)
    table = table[table["text"].str.len() >= 3]
    return table.drop_duplicates("text").reset_index(drop=True)


def civil(split: str) -> pd.DataFrame:
    files = sorted((RAW / "abuse_civil").glob(f"{split}-*.parquet"))
    data = pd.concat([pd.read_parquet(path) for path in files], ignore_index=True)
    abuse = (data[["toxicity", "severe_toxicity", "obscene", "insult"]] >= 0.5).any(axis=1).astype(int)
    return frame(
        data["text"],
        (data["threat"] >= 0.5).astype(int),
        (data["identity_attack"] >= 0.5).astype(int),
        abuse,
        0,
        f"civil_{split}",
    )


def thin_civil(table: pd.DataFrame, negatives: int, abuse_only: int) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    rare = table[(table["threat"] == 1) | (table["hate"] == 1)]
    insults = table[(table["abuse"] == 1) & (table["threat"] == 0) & (table["hate"] == 0)]
    clean = table[(table["abuse"] == 0) & (table["threat"] == 0) & (table["hate"] == 0)]
    pick = lambda part, size: part.iloc[rng.choice(len(part), min(size, len(part)), replace=False)]
    return pd.concat([rare, pick(insults, abuse_only), pick(clean, negatives)], ignore_index=True)


def roman_urdu(split: str) -> pd.DataFrame:
    if split == "test":
        data = pd.read_csv(RAW / "abuse_roman_urdu" / "task_1_test.tsv", sep="	", header=None, names=["tweet", "label"], quoting=csv.QUOTE_NONE, encoding="utf-8")
    else:
        data = pd.read_parquet(RAW / "abuse_roman_urdu" / f"{split}.parquet")
    offensive = (data["label"] == 0).astype(int)
    unknown = offensive.map({1: -1, 0: 0})
    return frame(data["tweet"], unknown, unknown, offensive, 0, f"roman_urdu_{split}")


def measuring_hate() -> pd.DataFrame:
    data = pd.read_parquet(RAW / "abuse_measuring_hate" / "train.parquet")
    keep = data[(data["hate_speech_score"] > 0.5) | (data["hate_speech_score"] < -1)].drop_duplicates("text")
    return frame(keep["text"], -1, (keep["hate_speech_score"] > 0.5).astype(int), -1, 0, "measuring_hate")


def email(name: str) -> pd.DataFrame:
    data = pd.read_csv(RAW / "email_curated" / f"{name}.csv", encoding_errors="replace", on_bad_lines="skip")
    data.columns = [c.strip().lower() for c in data.columns]
    subject = data["subject"].fillna("") if "subject" in data else ""
    body = data["body"].fillna("")
    text = "Subject: " + subject.astype(str) + "\n" + body.astype(str)
    label = pd.to_numeric(data["label"], errors="coerce").fillna(0).astype(int)
    unknown = label.map({1: -1, 0: 0})
    return frame(text, unknown, unknown, unknown, label, name)


def sms_uci() -> pd.DataFrame:
    with zipfile.ZipFile(RAW / "sms_uci" / "sms_spam_collection.zip") as archive:
        lines = archive.read("SMSSpamCollection").decode("utf-8", "replace").splitlines()
    pairs = [line.split("\t", 1) for line in lines if "\t" in line]
    data = pd.DataFrame(pairs, columns=["kind", "text"])
    label = (data["kind"] == "spam").astype(int)
    unknown = label.map({1: -1, 0: 0})
    return frame(data["text"], unknown, unknown, unknown, label, "sms_uci")


def hf_texts() -> pd.DataFrame:
    path = RAW / "hf_phishing" / "texts.json"
    if not path.exists():
        return pd.DataFrame()
    data = pd.DataFrame(json.loads(path.read_text(encoding="utf-8")))
    label = pd.to_numeric(data["label"], errors="coerce").fillna(0).astype(int)
    unknown = label.map({1: -1, 0: 0})
    return frame(data["text"], unknown, unknown, unknown, label, "hf_texts")


def squash(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def shingles(texts: pd.Series) -> set[str]:
    bag: set[str] = set()
    for text in texts:
        body = squash(text)
        bag.update(body[i : i + SHINGLE] for i in range(0, max(1, len(body) - SHINGLE), SHINGLE // 2))
    return bag


def shares_text(texts: pd.Series, bag: set[str]) -> np.ndarray:
    hits = np.zeros(len(texts), dtype=bool)
    for index, text in enumerate(texts):
        body = squash(text)
        hits[index] = not bag.isdisjoint(body[i : i + SHINGLE] for i in range(0, max(1, len(body) - SHINGLE)))
    return hits


def drop_copies(table: pd.DataFrame, bag: set[str], sources: tuple[str, ...]) -> tuple[pd.DataFrame, int]:
    """Remove rows that repeat a passage from an unseen-source test."""
    chosen = table["source"].isin(sources).to_numpy()
    remove = np.zeros(len(table), dtype=bool)
    remove[chosen] = shares_text(table.loc[chosen, "text"], bag)
    return table[~remove].reset_index(drop=True), int(remove.sum())


def holdout(table: pd.DataFrame, share: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    mask = np.random.default_rng(SEED).random(len(table)) < share
    return table[~mask], table[mask]


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    assassin_train, assassin_test = holdout(email("SpamAssasin"), 0.3)
    sms_train, sms_test = holdout(sms_uci(), 0.3)
    hf_train, hf_valid = holdout(hf_texts(), 0.1) if not hf_texts().empty else (pd.DataFrame(), pd.DataFrame())

    train = pd.concat(
        [
            thin_civil(civil("train"), 260_000, 70_000),
            roman_urdu("train"),
            email("Enron"),
            email("CEAS_08"),
            email("Ling"),
            email("TREC_06"),
            assassin_train,
            sms_train,
            hf_train,
        ],
        ignore_index=True,
    )
    valid = pd.concat([thin_civil(civil("validation"), 30_000, 8_000), roman_urdu("validation"), hf_valid], ignore_index=True)
    unseen_fraud = pd.concat(
        [email("Nazario"), email("Nigerian_Fraud"), assassin_test[assassin_test["fraud"] == 0]], ignore_index=True
    )
    tests = {
        "abuse_civil": civil("test"),
        "hate_unseen_source": measuring_hate(),
        "fraud_email_unseen_source": unseen_fraud,
        "sms_unseen": sms_test,
        "roman_urdu": roman_urdu("test"),
    }
    train = train.sample(frac=1, random_state=SEED).drop_duplicates("text").reset_index(drop=True)
    mail_sources = ("hf_texts", "CEAS_08", "Enron", "TREC_06", "Ling", "SpamAssasin")
    fraud_bag = shingles(unseen_fraud.loc[unseen_fraud["source"] != "SpamAssasin", "text"])
    train, removed_fraud = drop_copies(train, fraud_bag, mail_sources)
    train, removed_normal = drop_copies(train, shingles(assassin_test["text"]), ("hf_texts",))
    valid, removed_valid = drop_copies(valid, fraud_bag, mail_sources)
    seen = set(train["text"])
    valid = valid[~valid["text"].isin(seen)].reset_index(drop=True)
    train.to_parquet(WORK / "text_train.parquet")
    valid.to_parquet(WORK / "text_valid.parquet")
    summary = {
        "train": len(train),
        "valid": len(valid),
        "removed_copies_of_test_text": {"fraud_train": removed_fraud, "normal_train": removed_normal, "valid": removed_valid},
    }
    for name, table in tests.items():
        table = table[~table["text"].isin(seen)].reset_index(drop=True)
        table.to_parquet(WORK / f"text_test_{name}.parquet")
        summary[name] = len(table)
    for label in LABELS:
        summary[f"train_{label}_positive"] = int((train[label] == 1).sum())
    summary["sources"] = train["source"].value_counts().to_dict()
    (WORK / "text_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
