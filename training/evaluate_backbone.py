"""Run the Network Agent on a sample of real Internet backbone traffic (MAWI).

MAWI has no labels, so this measures speed and how often each model alerts.
An alert here is not proven false, because real attacks do cross a backbone.
"""
import gzip
import json
import random
import sys
import time
import zlib
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sklearn.ensemble import IsolationForest  # noqa: E402

from stl.flow_model import FlowModel, encode, iter_flows, window_features  # noqa: E402

RAW = ROOT / "data" / "raw" / "traffic_mawi"
RESULTS = ROOT / "results"
LIMIT = 300_000


class Stream:
    """Reads a gzip capture that was cut short, and stops cleanly at the cut."""

    def __init__(self, path: Path):
        self.inner = gzip.open(path, "rb")

    def read(self, size: int = -1) -> bytes:
        try:
            return self.inner.read(size)
        except (EOFError, zlib.error, OSError):
            return b""


def own_site_test(numbers, kinds, masks, owner: np.ndarray) -> dict:
    """Train the normal-behaviour model on half the hosts, test it on the other half."""
    features = window_features(np.concatenate(numbers), np.concatenate(kinds), np.concatenate(masks))
    first = owner % 2 == 0
    fit, rest = features[first], features[~first]
    forest = IsolationForest(n_estimators=200, max_samples=8192, max_features=0.7, n_jobs=4, random_state=7).fit(fit[::2])
    cut = np.quantile(-forest.score_samples(fit[1::2]), 0.995)
    return {
        "fitted_on_windows": int(len(fit) // 2),
        "alert_rate_on_other_hosts": round(float((-forest.score_samples(rest) >= cut).mean()), 5),
        "target": 0.005,
    }


def main() -> None:
    path = next(RAW.glob("*.pcap.gz"))
    model = FlowModel()
    started = time.time()
    by_host = defaultdict(list)
    total = 0
    try:
        for flow in iter_flows(Stream(path)):
            by_host[flow.src].append(flow)
            total += 1
    except (EOFError, ValueError, OSError) as error:
        print("stopped at", error)
    read_seconds = time.time() - started
    print(total, "flows from", len(by_host), "hosts in", round(read_seconds), "s", flush=True)
    hosts = list(by_host)
    random.Random(7).shuffle(hosts)
    known, unusual, owners = [], [], []
    numbers, kinds, masks = [], [], []
    windows = 0

    numbers_all, kinds_all, masks_all = [], [], []

    def flush():
        if not numbers:
            return
        a, b, c = np.concatenate(numbers), np.concatenate(kinds), np.concatenate(masks)
        numbers_all.append(a)
        kinds_all.append(b)
        masks_all.append(c)
        known.append(model.score_many(a, b, c))
        if model.anomaly:
            unusual.append(model.unusual_many(a, b, c))
        numbers.clear()
        kinds.clear()
        masks.clear()

    started = time.time()
    used = 0
    for host in hosts:
        flows = sorted(by_host[host], key=lambda f: f.start)[:200]
        used += 1
        for end in range(1, len(flows) + 1):
            a, b, c = encode(flows[max(0, end - 32) : end])
            numbers.append(a)
            kinds.append(b)
            masks.append(c)
            owners.append(used)
            windows += 1
            if len(numbers) >= 1024:
                flush()
        if windows >= LIMIT:
            break
    flush()
    score_seconds = time.time() - started
    known = np.concatenate(known) >= model.threshold
    unusual = np.concatenate(unusual) >= 0.5 if unusual else np.zeros_like(known)
    either = known | unusual
    owner = np.array(owners)
    report = {
        "trace": path.name,
        "flows_read": total,
        "hosts_seen": len(by_host),
        "hosts_scored": used,
        "flows_scored": int(len(known)),
        "known_attack_alert_rate": round(float(known.mean()), 5),
        "normal_behaviour_alert_rate": round(float(unusual.mean()), 5),
        "either_alert_rate": round(float(either.mean()), 5),
        "hosts_with_alerts": int(len(np.unique(owner[either]))),
        "read_flows_per_second": round(total / max(read_seconds, 1e-6)),
        "score_flows_per_second_cpu": round(len(known) / max(score_seconds, 1e-6)),
    }
    report["trained_on_this_traffic"] = own_site_test(numbers_all, kinds_all, masks_all, owner)
    (RESULTS / "backbone.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
