"""Save two real traffic histories from held-out CICIDS2017 data for the demo."""
import json
from pathlib import Path

import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stl.flow_model import FlowModel  # noqa: E402
from stl.schema import Flow  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "data" / "work" / "flows" / "cic_friday.parquet"
THURSDAY = ROOT / "data" / "work" / "flows" / "cic_thursday.parquet"
OUT = ROOT / "stl" / "data" / "demo_flows.json"


def rows(part: pd.DataFrame) -> list[dict]:
    keep = ["dst", "sport", "dport", "proto", "start", "duration", "packets", "bytes", "src_bytes"]
    return [dict(row, src="", dst=str(row["dst"])) for row in part[keep].to_dict("records")]


def typical_window(normal: pd.DataFrame) -> pd.DataFrame:
    """Pick the window closest to median behaviour among busy normal hosts."""
    model = FlowModel()
    candidates = []
    for host in normal["src"].value_counts().index[:12]:
        part = normal[normal["src"] == host]
        for start in range(0, max(1, len(part) - 31), max(1, len(part) // 30)):
            window = part.iloc[start : start + 31]
            if len(window) == 31:
                flows = [Flow(src="", **{k: row[k] for k in ("dst", "sport", "dport", "proto", "start", "duration", "packets", "bytes", "src_bytes")}) for row in rows(window)]
                candidates.append((model.unusual_flows(flows), start, host))
    candidates.sort(key=lambda item: item[0])
    _, start, host = candidates[len(candidates) // 2]
    return normal[normal["src"] == host].iloc[start : start + 31]


def as_flows(window: pd.DataFrame) -> list[Flow]:
    return [Flow(**row) for row in rows(window)]


def unusual_window() -> pd.DataFrame:
    """Flows that end in a held-out web attack: the known model misses them, the normal model does not."""
    model = FlowModel()
    table = pd.read_parquet(THURSDAY)
    table = table[table["start"].notna()].sort_values("start", kind="stable")
    web = table[table["label"].str.startswith("Web Attack")]
    place = web.groupby("label", sort=False).cumcount() / web.groupby("label", sort=False)["label"].transform("size")
    ends = web[place >= 0.8]
    best, best_score = None, -1.0
    for host, last in ends.groupby("src"):
        part = table[table["src"] == host]
        for position in part.index.get_indexer(last.index):
            if position < 30:
                continue
            window = part.iloc[position - 30 : position + 1]
            flows = as_flows(window)
            known, _ = model.score_flows(flows)
            unusual = model.unusual_flows(flows)
            if known < model.threshold and unusual > best_score:
                best, best_score = window, unusual
    print("unusual window score", round(best_score, 3))
    return best


def main() -> None:
    table = pd.read_parquet(TABLE).sort_values("start")
    tail = table.iloc[int(len(table) * 0.8) :]
    attack = tail[tail["label"].isin(["Portscan", "DDoS", "Botnet"])]
    host = attack["src"].value_counts().index[0]
    bad = attack[attack["src"] == host].iloc[200:231]
    normal = tail[tail["attack"] == 0]
    good = typical_window(normal)
    OUT.parent.mkdir(exist_ok=True)
    unusual = unusual_window()
    OUT.write_text(json.dumps({"normal": rows(good), "bad": rows(bad), "unusual": rows(unusual)}, indent=0), encoding="utf-8")
    print("bad", bad["label"].value_counts().to_dict(), "| normal", good["label"].value_counts().to_dict(), "| unusual", unusual["label"].value_counts().to_dict())


if __name__ == "__main__":
    main()
