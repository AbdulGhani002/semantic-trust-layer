"""Download the public datasets and live feeds used to train and test STL.

Every source goes into its own folder under data/raw. Nothing here opens a
listed URL: the phishing and malware feeds are saved as plain text only.
"""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "data" / "manifest.json"
AGENT = "stl-research/0.1"
ZENODO = "https://zenodo.org/api/records/8339691/files/{}/content"
HF = "https://huggingface.co/datasets/ealvaradob/phishing-dataset/resolve/main/{}"
UCI = "https://archive.ics.uci.edu/static/public/{}"
HF_PARQUET = "https://huggingface.co/api/datasets"

SOURCES = {
    "quick": [
        ("sms_uci", "sms_spam_collection.zip", UCI.format("228/sms+spam+collection.zip"), "CC BY 4.0"),
        ("feed_openphish", "feed.txt", "https://openphish.com/feed.txt", "OpenPhish community feed"),
        ("feed_feodo", "ipblocklist.csv", "https://feodotracker.abuse.ch/downloads/ipblocklist.csv", "CC0, abuse.ch"),
        ("feed_sslbl", "ja3_fingerprints.csv", "https://sslbl.abuse.ch/blacklist/ja3_fingerprints.csv", "CC0, abuse.ch"),
        ("legit_tranco", "top-1m.csv.zip", "https://tranco-list.eu/top-1m.csv.zip", "Tranco research list"),
        ("url_phiusiil", "phiusiil.zip", UCI.format("967/phiusiil+phishing+url+dataset.zip"), "CC BY 4.0"),
        (
            "feed_phishing_database",
            "phishing-links-ACTIVE.txt",
            "https://raw.githubusercontent.com/Phishing-Database/Phishing.Database/master/phishing-links-ACTIVE.txt",
            "MIT",
        ),
    ],
    "text": [
        ("email_curated", name, ZENODO.format(name), "CC BY 4.0")
        for name in (
            "Enron.csv",
            "SpamAssasin.csv",
            "CEAS_08.csv",
            "Nazario.csv",
            "Nigerian_Fraud.csv",
            "Ling.csv",
            "TREC_06.csv",
        )
    ]
    + [
        ("hf_phishing", "texts.json", HF.format("texts.json"), "Apache 2.0"),
        ("hf_phishing", "urls.json", HF.format("urls.json"), "Apache 2.0"),
    ],
    "traffic": [
        (
            "traffic_cicids2017",
            "CICIDS2017_improved.zip",
            "https://intrusion-detection.distrinet-research.be/CNS2022/Datasets/CICIDS2017_improved.zip",
            "Engelen et al. corrected CICIDS2017",
        ),
        (
            "traffic_ctu13",
            "CTU-13-Dataset.tar.bz2",
            "https://mcfp.felk.cvut.cz/publicDatasets/CTU-13-Dataset/CTU-13-Dataset.tar.bz2",
            "CTU-13, Stratosphere Lab",
        ),
    ],
    "commoncrawl": [
        (
            "legit_commoncrawl",
            "cluster.idx",
            "https://data.commoncrawl.org/cc-index/collections/CC-MAIN-2026-43/indexes/cluster.idx",
            "Common Crawl URL index",
        ),
    ],
    "abuse": [
        ("abuse_civil", f"{split}-{part}.parquet", f"{HF_PARQUET}/google/civil_comments/parquet/default/{split}/{part}.parquet", "CC0")
        for split, part in (("train", 0), ("train", 1), ("validation", 0), ("test", 0))
    ]
    + [
        (
            "abuse_roman_urdu",
            f"{split}.parquet",
            f"{HF_PARQUET}/community-datasets/roman_urdu_hate_speech/parquet/Coarse_Grained/{split}/0.parquet",
            "MIT",
        )
        for split in ("train", "validation")
    ]
    + [
        (
            "abuse_roman_urdu",
            "task_1_test.tsv",
            "https://raw.githubusercontent.com/haroonshakeel/roman_urdu_hate_speech/main/task_1_test.tsv",
            "MIT",
        ),
    ]
    + [
        (
            "abuse_measuring_hate",
            "train.parquet",
            f"{HF_PARQUET}/ucberkeley-dlab/measuring-hate-speech/parquet/default/train/0.parquet",
            "CC BY 4.0",
        ),
    ],
    "jdk": [
        (
            "tools_jdk",
            "temurin-17.zip",
            "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse",
            "Eclipse Temurin JDK 17",
        ),
    ],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch(folder: str, name: str, url: str, licence: str, manifest: dict) -> None:
    target = RAW / folder / name
    target.parent.mkdir(parents=True, exist_ok=True)
    key = f"{folder}/{name}"
    if key in manifest and target.exists() and target.stat().st_size == manifest[key]["bytes"]:
        print(f"have {key}", flush=True)
        return
    started = time.time()
    command = [
        "curl", "-sS", "-L", "--fail", "--retry", "6", "--retry-delay", "5", "--retry-all-errors",
        "--connect-timeout", "30", "-A", AGENT, "-C", "-", "-o", str(target), url,
    ]
    result = subprocess.run(command, check=False)
    if result.returncode != 0 or not target.exists():
        print(f"FAILED {key} (curl exit {result.returncode})", flush=True)
        return
    manifest[key] = record(target, url, licence)
    save(manifest)
    print(f"done {key}: {target.stat().st_size / 1e6:.1f} MB in {time.time() - started:.0f} s", flush=True)


def record(target: Path, url: str, licence: str) -> dict:
    return {
        "url": url,
        "licence": licence,
        "bytes": target.stat().st_size,
        "sha256": sha256(target),
        "retrieved": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(target.stat().st_mtime)),
    }


def save(manifest: dict) -> None:
    current = load()
    current.update(manifest)
    manifest.update(current)
    MANIFEST.write_text(json.dumps(current, indent=1, sort_keys=True), encoding="utf-8")


def load() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}


def rebuild() -> None:
    manifest = {}
    for group in SOURCES.values():
        for folder, name, url, licence in group:
            target = RAW / folder / name
            if target.exists():
                manifest[f"{folder}/{name}"] = record(target, url, licence)
    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True), encoding="utf-8")
    print(f"manifest has {len(manifest)} files", flush=True)


def main() -> None:
    if sys.argv[1:] == ["rebuild"]:
        rebuild()
        return
    groups = sys.argv[1:] or list(SOURCES)
    manifest = load()
    for group in groups:
        for folder, name, url, licence in SOURCES[group]:
            fetch(folder, name, url, licence, manifest)
    print("all done", flush=True)


if __name__ == "__main__":
    main()
