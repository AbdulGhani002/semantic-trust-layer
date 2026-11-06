"""Turn real traffic records into one compact format for the Network Agent.

Every record keeps metadata only. Host addresses are used to group a host's
connections in time order and are never given to the model as an input.
"""
import bz2
import io
import json
import sys
import tarfile
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
WORK = ROOT / "data" / "work" / "flows"
PROTO = {6: "tcp", 17: "udp", 1: "icmp"}


def finish(table: pd.DataFrame, name: str) -> dict:
    table = table.sort_values(["src", "start"], kind="stable").reset_index(drop=True)
    table.to_parquet(WORK / f"{name}.parquet")
    return {"rows": len(table), "attack": int(table["attack"].sum()), "hosts": int(table["src"].nunique())}


def cic_day(handle, day: str) -> pd.DataFrame:
    wanted = {
        "Src IP": "src",
        "Dst IP": "dst",
        "Src Port": "sport",
        "Dst Port": "dport",
        "Protocol": "proto",
        "Timestamp": "stamp",
        "Flow Duration": "duration",
        "Total Fwd Packet": "fwd_packets",
        "Total Bwd packets": "bwd_packets",
        "Total Length of Fwd Packet": "fwd_bytes",
        "Total Length of Bwd Packet": "bwd_bytes",
        "Label": "label",
    }
    data = pd.read_csv(handle, usecols=list(wanted), encoding_errors="replace", low_memory=False).rename(columns=wanted)
    attempted = data["label"].astype(str).str.contains("Attempted", case=False)
    data["label"] = data["label"].astype(str).where(~attempted, "BENIGN")
    table = pd.DataFrame(
        {
            "src": data["src"].astype(str),
            "dst": data["dst"].astype(str),
            "sport": pd.to_numeric(data["sport"], errors="coerce").fillna(0).astype(np.int32),
            "dport": pd.to_numeric(data["dport"], errors="coerce").fillna(0).astype(np.int32),
            "proto": pd.to_numeric(data["proto"], errors="coerce").fillna(0).astype(int).map(PROTO).fillna("other"),
            "start": pd.to_datetime(data["stamp"], errors="coerce", format="mixed").astype("int64") / 1e9,
            "duration": pd.to_numeric(data["duration"], errors="coerce").fillna(0).clip(lower=0) / 1e6,
            "packets": (data["fwd_packets"] + data["bwd_packets"]).astype(np.int64),
            "bytes": (data["fwd_bytes"] + data["bwd_bytes"]).astype(np.int64),
            "src_bytes": data["fwd_bytes"].astype(np.int64),
            "label": data["label"].astype(str),
        }
    )
    table["attack"] = (~table["label"].str.upper().str.startswith("BENIGN")).astype(np.int8)
    table["day"] = day
    return table


def prepare_cic(summary: dict) -> None:
    path = RAW / "traffic_cicids2017" / "CICIDS2017_improved.zip"
    if not path.exists():
        return
    with zipfile.ZipFile(path) as archive:
        files = [n for n in archive.namelist() if n.lower().endswith(".csv")]
        print(files, flush=True)
        for name in files:
            day = Path(name).stem.lower()
            with archive.open(name) as handle:
                table = cic_day(handle, day)
            summary[f"cic_{day}"] = finish(table, f"cic_{day}")
            summary[f"cic_{day}"]["attacks"] = table.loc[table["attack"] == 1, "label"].value_counts().to_dict()
            print(day, summary[f"cic_{day}"], flush=True)


def ctu_table(stream, scenario: str) -> pd.DataFrame:
    data = pd.read_csv(stream, encoding_errors="replace", low_memory=False)
    label = data["Label"].astype(str)
    port = lambda column: pd.to_numeric(data[column].fillna("0").astype(str).map(lambda v: int(v, 16) if v.startswith("0x") else v), errors="coerce")
    table = pd.DataFrame(
        {
            "src": data["SrcAddr"].astype(str),
            "dst": data["DstAddr"].astype(str),
            "sport": port("Sport").fillna(0).astype(np.int32),
            "dport": port("Dport").fillna(0).astype(np.int32),
            "proto": data["Proto"].astype(str).str.lower(),
            "start": pd.to_datetime(data["StartTime"], errors="coerce").astype("int64") / 1e9,
            "duration": pd.to_numeric(data["Dur"], errors="coerce").fillna(0).clip(lower=0),
            "packets": pd.to_numeric(data["TotPkts"], errors="coerce").fillna(0).astype(np.int64),
            "bytes": pd.to_numeric(data["TotBytes"], errors="coerce").fillna(0).astype(np.int64),
            "src_bytes": pd.to_numeric(data["SrcBytes"], errors="coerce").fillna(0).astype(np.int64),
            "label": label,
        }
    )
    table["attack"] = label.str.contains("From-Botnet", regex=False).astype(np.int8)
    table["kind"] = np.select(
        [label.str.contains("Botnet", regex=False), label.str.contains("Normal", regex=False)], ["botnet", "normal"], "background"
    )
    table["scenario"] = scenario
    return table


def keep_hosts(table: pd.DataFrame, background_share: float = 0.05) -> pd.DataFrame:
    """Keep every labelled host whole, plus a random share of background hosts."""
    labelled = set(table.loc[table["kind"] != "background", "src"])
    others = pd.Series(table.loc[~table["src"].isin(labelled), "src"].unique())
    chosen = set(others.sample(frac=background_share, random_state=7))
    return table[table["src"].isin(labelled | chosen)]


def prepare_ctu(summary: dict) -> None:
    path = RAW / "traffic_ctu13" / "CTU-13-Dataset.tar.bz2"
    if not path.exists():
        return
    with tarfile.open(path, "r:bz2") as archive:
        for member in archive:
            if member.isfile() and member.name.endswith(".binetflow"):
                scenario = Path(member.name).parts[-2]
                with archive.extractfile(member) as handle:
                    table = ctu_table(io.BytesIO(handle.read()), scenario)
                table = keep_hosts(table)
                summary[f"ctu_{scenario}"] = finish(table, f"ctu_{scenario}")
                print(scenario, summary[f"ctu_{scenario}"], flush=True)


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    path = WORK.parent / "flow_summary.json"
    summary = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    wanted = sys.argv[1:] or ["cic", "ctu"]
    if "cic" in wanted:
        prepare_cic(summary)
    if "ctu" in wanted:
        prepare_ctu(summary)
    path.write_text(json.dumps(summary, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
