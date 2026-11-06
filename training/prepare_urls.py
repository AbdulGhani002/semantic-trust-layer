"""Build the URL sets for the Application Agent's link model.

URLs are only read as text here. Nothing opens them. The split is by
registered domain, so a domain seen in training never appears in a test.
Everything is lowercased and stripped of scheme and "www" because the normal
URLs come from a canonicalised index, and those details would leak the label.
"""
import hashlib
import io
import json
import zipfile
from pathlib import Path

import pandas as pd
import tldextract

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
WORK = ROOT / "data" / "work"
EXTRACT = tldextract.TLDExtract(suffix_list_urls=(), include_psl_private_domains=True)
MAX_LEN = 300


def normalise(url: str) -> str:
    url = url.strip().lower()
    for prefix in ("https://", "http://", "ftp://"):
        if url.startswith(prefix):
            url = url[len(prefix) :]
            break
    if url.startswith("www."):
        url = url[4:]
    return url.rstrip("/")[:MAX_LEN]


def domain_of(url: str) -> str:
    host = url.split("/", 1)[0].split("?", 1)[0].split("@")[-1].split(":", 1)[0]
    part = EXTRACT(host)
    return part.top_domain_under_public_suffix or host


def bucket(domain: str) -> int:
    return hashlib.sha1(domain.encode("utf-8", "ignore")).digest()[0] % 10


def phishing_database() -> list[str]:
    path = RAW / "feed_phishing_database" / "phishing-links-ACTIVE.txt"
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()


def phiusiil() -> tuple[list[str], list[str]]:
    with zipfile.ZipFile(RAW / "url_phiusiil" / "phiusiil.zip") as archive:
        name = next(n for n in archive.namelist() if n.lower().endswith(".csv"))
        data = pd.read_csv(io.BytesIO(archive.read(name)), usecols=["URL", "label"], encoding_errors="replace")
    return data.loc[data["label"] == 0, "URL"].astype(str).tolist(), data.loc[data["label"] == 1, "URL"].astype(str).tolist()


def hf_urls() -> tuple[list[str], list[str]]:
    path = RAW / "hf_phishing" / "urls.json"
    if not path.exists():
        return [], []
    data = pd.DataFrame(json.loads(path.read_text(encoding="utf-8")))
    return data.loc[data["label"] == 1, "text"].astype(str).tolist(), data.loc[data["label"] == 0, "text"].astype(str).tolist()


def tranco(limit: int = 300_000) -> list[str]:
    with zipfile.ZipFile(RAW / "legit_tranco" / "top-1m.csv.zip") as archive:
        lines = archive.read(archive.namelist()[0]).decode().splitlines()
    return [line.split(",", 1)[1] for line in lines[:limit]]


def surt_to_url(key: str) -> str | None:
    if ")" not in key:
        return None
    host, path = key.split(")", 1)
    return ".".join(reversed(host.split(":")[0].split(","))) + path


def common_crawl() -> list[str]:
    path = RAW / "legit_commoncrawl" / "cluster.idx"
    if not path.exists():
        return []
    urls = []
    with path.open(encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            url = surt_to_url(line.split(" ", 1)[0])
            if url:
                urls.append(url)
    return urls


def table(urls: list[str], label: int, source: str) -> pd.DataFrame:
    data = pd.DataFrame({"url": [normalise(u) for u in urls if u.strip()]})
    data = data[data["url"].str.len() > 3].drop_duplicates("url")
    data["label"] = label
    data["source"] = source
    return data


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    phish_ui, legit_ui = phiusiil()
    phish_hf, legit_hf = hf_urls()
    data = pd.concat(
        [
            table(phishing_database(), 1, "phishing_database"),
            table(phish_ui, 1, "phiusiil"),
            table(phish_hf, 1, "hf_urls"),
            table(common_crawl(), 0, "common_crawl"),
            table(tranco(), 0, "tranco"),
            table(legit_ui, 0, "phiusiil"),
            table(legit_hf, 0, "hf_urls"),
        ],
        ignore_index=True,
    )
    data = data.sort_values("label", ascending=False).drop_duplicates("url")
    data["domain"] = data["url"].map(domain_of)
    data["bucket"] = data["domain"].map(bucket)
    train = data[data["bucket"] <= 7]
    valid = data[data["bucket"] == 8]
    test = data[data["bucket"] == 9]
    fresh = table((RAW / "feed_openphish" / "feed.txt").read_text(encoding="utf-8", errors="ignore").splitlines(), 1, "openphish_today")
    fresh["domain"] = fresh["url"].map(domain_of)
    known = set(train["domain"])
    fresh_unseen = fresh[~fresh["domain"].isin(known)]
    train.to_parquet(WORK / "url_train.parquet")
    valid.to_parquet(WORK / "url_valid.parquet")
    test.to_parquet(WORK / "url_test.parquet")
    fresh.to_parquet(WORK / "url_test_openphish.parquet")
    fresh_unseen.to_parquet(WORK / "url_test_openphish_unseen.parquet")
    summary = {
        "train": len(train),
        "valid": len(valid),
        "test": len(test),
        "train_phish": int(train["label"].sum()),
        "test_phish": int(test["label"].sum()),
        "openphish_today": len(fresh),
        "openphish_unseen_domains": len(fresh_unseen),
        "by_source": data.groupby(["source", "label"]).size().rename(lambda x: str(x)).to_dict().__repr__(),
    }
    (WORK / "url_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
