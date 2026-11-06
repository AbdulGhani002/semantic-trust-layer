"""Add an anomaly model to the Network Agent, to catch attacks it never saw.

It learns normal host behaviour only, so it needs no attack examples. Each
window of 32 connections becomes a set of behaviour numbers. The cut-off is
set for a fixed false alarm rate on normal traffic from the validation data.
"""
import json
from pathlib import Path

import joblib
import numpy as np
import torch
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stl.flow_model import FlowModel  # noqa: E402
from train_flows import RESULTS, WORK, Flows, metrics  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "models" / "flow"
TARGET_FALSE_ALARMS = 0.005


def window_features(data: Flows, rows: np.ndarray, batch: int = 8192) -> np.ndarray:
    parts = []
    for start in range(0, len(rows), batch):
        numbers, kinds, mask = data.batch(rows[start : start + batch], "cpu")
        valid = (~mask).float().unsqueeze(2)
        count = valid.sum(1).clamp(min=1)
        mean = (numbers * valid).sum(1) / count
        var = (((numbers - mean.unsqueeze(1)) ** 2) * valid).sum(1) / count
        protos = torch.nn.functional.one_hot(kinds[:, :, 0], 4).float()
        ports = torch.nn.functional.one_hot(kinds[:, :, 1], 15).float()
        parts.append(
            torch.cat(
                [mean, var.sqrt(), count / 32, (protos * valid).sum(1) / count, (ports * valid).sum(1) / count, numbers[:, -1, :]],
                dim=1,
            ).numpy()
        )
    return np.concatenate(parts).astype(np.float32)


def main() -> None:
    names = {path.stem.split("_", 1)[1]: path.stem for path in WORK.glob("cic_*.parquet")}
    first = [names[d] for d in ("monday", "tuesday", "wednesday")]
    train, valid = Flows(first, (0, 0.8)), Flows(first, (0.8, 1))
    rng = np.random.default_rng(7)
    normal = train.rows[train.attack[train.rows] == 0]
    picked = rng.choice(normal, min(len(normal), 300_000), replace=False)
    print("fitting on", len(picked), "normal windows", flush=True)
    forest = IsolationForest(n_estimators=200, max_samples=8192, max_features=0.7, n_jobs=8, random_state=7)
    forest.fit(window_features(train, picked))
    calm = valid.rows[valid.attack[valid.rows] == 0]
    calm = rng.choice(calm, min(len(calm), 200_000), replace=False)
    calm_score = -forest.score_samples(window_features(valid, calm))
    cut = float(np.quantile(calm_score, 1 - TARGET_FALSE_ALARMS))
    low, high = float(np.quantile(calm_score, 0.9)), float(calm_score.max() + 0.2)
    report = {"cut_off": cut, "target_false_alarms": TARGET_FALSE_ALARMS, "tests": {}}

    def scale(score):
        return np.clip((score - calm_score.min()) / max(high - calm_score.min(), 1e-6), 0, 1)

    for day in ("thursday", "friday"):
        test = Flows([names[day]])
        rows = test.rows
        score = -forest.score_samples(window_features(test, rows))
        y = test.attack[rows].astype(int)
        result = metrics(y, scale(score), float(scale(cut)))
        labels = test.table["label"].to_numpy()[rows]
        result["recall_by_attack"] = {str(kind): round(float((score[labels == kind] >= cut).mean()), 4) for kind in np.unique(labels[y == 1])}
        report["tests"][day] = result
        print(day, json.dumps(result), flush=True)
    every = list(names.values())
    later = Flows(every, (0.8, 1))
    rows = rng.choice(later.rows, min(len(later), 150_000), replace=False)
    numbers, kinds, mask = zip(*(later.batch(rows[i : i + 4096], "cpu") for i in range(0, len(rows), 4096)))
    numbers, kinds, mask = torch.cat(numbers).numpy(), torch.cat(kinds).numpy(), torch.cat(mask).numpy()
    known_model = FlowModel()
    known = np.concatenate(
        [known_model.score_many(numbers[i : i + 2048], kinds[i : i + 2048], mask[i : i + 2048]) for i in range(0, len(rows), 2048)]
    ) >= known_model.threshold
    unusual =-forest.score_samples(window_features(later, rows)) >= cut
    y = later.attack[rows].astype(int)
    report["both_models_later_flows"] = {
        name: metrics(y, flagged.astype(float), 0.5)
        for name, flagged in (("known_attack_model", known), ("normal_behaviour_model", unusual), ("either_model", known | unusual))
    }
    print(json.dumps(report["both_models_later_flows"]), flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    joblib.dump({"forest": forest, "cut_off": cut, "low": low, "high": high}, OUT / "anomaly.joblib", compress=3)
    (RESULTS / "anomaly.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("saved", flush=True)


if __name__ == "__main__":
    main()
