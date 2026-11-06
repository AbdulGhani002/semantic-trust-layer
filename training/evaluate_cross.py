"""Cross-dataset test: models built on CICIDS2017, tested on CTU-13 botnets."""
import json
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from stl.flow_model import FlowModel  # noqa: E402
from train_flows import RESULTS, WORK, Flows, metrics  # noqa: E402


def main() -> None:
    model = FlowModel()
    report = {}
    rng = np.random.default_rng(7)
    for name in sorted(path.stem for path in WORK.glob("ctu_*.parquet")):
        data = Flows([name])
        attacks = data.rows[data.attack[data.rows] == 1]
        others = data.rows[data.attack[data.rows] == 0]
        rows = np.concatenate([rng.choice(attacks, min(len(attacks), 20_000), replace=False), rng.choice(others, min(len(others), 60_000), replace=False)])
        known, unusual = [], []
        for start in range(0, len(rows), 2048):
            numbers, kinds, mask = data.batch(rows[start : start + 2048], "cpu")
            a, b, c = numbers.numpy(), kinds.numpy(), mask.numpy()
            known.append(model.score_many(a, b, c))
            unusual.append(model.unusual_many(a, b, c))
        known, unusual = np.concatenate(known), np.concatenate(unusual)
        y = data.attack[rows].astype(int)
        flagged = (known >= model.threshold) | (unusual >= 0.5)
        report[name] = {
            "known_attack_model": metrics(y, known, model.threshold),
            "normal_behaviour_model": metrics(y, unusual, 0.5),
            "either_model": metrics(y, flagged.astype(float), 0.5),
        }
        print(name, json.dumps({k: {m: v[m] for m in ("recall", "false_alarm_rate", "auc")} for k, v in report[name].items()}), flush=True)
    (RESULTS / "cross_dataset.json").write_text(json.dumps(report, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
