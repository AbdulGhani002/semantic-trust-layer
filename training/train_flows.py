"""Train the Network Agent's behaviour model on real traffic.

A small transformer reads a host's last 32 connections and scores the newest
one. LightGBM on single flows is the baseline. Days or whole capture scenarios
are held out, so the test covers traffic the model never saw.
"""
import argparse
import json
import time
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import average_precision_score, precision_recall_curve, precision_recall_fscore_support, roc_auc_score
from torch import nn

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "data" / "work" / "flows"
OUT = ROOT / "models" / "flow"
RESULTS = ROOT / "results"
WINDOW = 32
PROTOS = {"tcp": 0, "udp": 1, "icmp": 2}
KNOWN_PORTS = {
    80: 1, 8080: 1, 8000: 1, 443: 2, 8443: 2, 53: 3, 25: 4, 465: 4, 587: 4, 110: 4, 143: 4, 993: 4, 995: 4,
    22: 5, 21: 6, 20: 6, 23: 7, 3389: 8, 445: 9, 139: 9, 135: 9, 123: 10, 6667: 11, 6666: 11, 6668: 11,
}


def port_groups(ports: np.ndarray) -> np.ndarray:
    groups = np.where(ports < 1024, 12, np.where(ports < 49152, 13, 14))
    for port, group in KNOWN_PORTS.items():
        groups[ports == port] = group
    return groups


class Flows:
    def __init__(self, names: list[str], part: tuple[float, float] = (0.0, 1.0)):
        table = pd.concat([pd.read_parquet(WORK / f"{name}.parquet").assign(group=name) for name in names], ignore_index=True)
        table = table[table["start"].notna()].sort_values(["src", "start"], kind="stable").reset_index(drop=True)
        by_time = table.sort_values("start", kind="stable").groupby(["group", "label"], sort=False).cumcount()
        sizes = table.groupby(["group", "label"], sort=False)["label"].transform("size")
        place = (by_time.reindex(table.index) / sizes).to_numpy()
        self.rows = np.flatnonzero((place >= part[0]) & (place < part[1]))
        packets = table["packets"].clip(lower=1).to_numpy(np.float64)
        total = table["bytes"].clip(lower=0).to_numpy(np.float64)
        sent = table["src_bytes"].clip(lower=0).to_numpy(np.float64)
        same_host = table["src"].to_numpy()[1:] == table["src"].to_numpy()[:-1]
        starts = table["start"].to_numpy(np.float64)
        gap = np.zeros(len(table))
        gap[1:] = np.where(same_host, np.clip(starts[1:] - starts[:-1], 0, None), 0.0)
        self.numbers = np.stack(
            [
                np.log1p(table["duration"].to_numpy(np.float64)),
                np.log1p(packets),
                np.log1p(sent),
                np.log1p(np.clip(total - sent, 0, None)),
                np.log1p(total / packets),
                sent / np.clip(total, 1, None),
                np.log1p(gap),
            ],
            axis=1,
        ).astype(np.float32)
        ports = table["dport"].to_numpy(np.int64)
        self.kinds = np.stack([table["proto"].map(PROTOS).fillna(3).to_numpy(np.int64), port_groups(ports)], axis=1)
        self.dst = pd.factorize(table["dst"])[0].astype(np.int64)
        self.port = ports
        first = np.zeros(len(table), dtype=np.int64)
        boundary = np.r_[True, ~same_host]
        first[boundary] = np.flatnonzero(boundary)
        self.first = np.maximum.accumulate(first)
        self.attack = table["attack"].to_numpy(np.float32)
        self.table = table

    def __len__(self):
        return len(self.rows)

    def batch(self, positions: np.ndarray, device: str):
        offsets = np.arange(-WINDOW + 1, 1)
        index = positions[:, None] + offsets
        valid = index >= self.first[positions][:, None]
        index = np.maximum(index, 0)
        numbers = torch.from_numpy(self.numbers[index]).to(device)
        kinds = torch.from_numpy(self.kinds[index]).to(device)
        valid_t = torch.from_numpy(valid).to(device)
        dst = torch.from_numpy(self.dst[index]).to(device)
        port = torch.from_numpy(self.port[index]).to(device)
        earlier = torch.tril(torch.ones(WINDOW, WINDOW, dtype=torch.bool, device=device), diagonal=-1)
        before = valid_t.unsqueeze(1) & earlier
        new_dst = ~((dst.unsqueeze(1) == dst.unsqueeze(2)) & before).any(2)
        new_port = ~((port.unsqueeze(1) == port.unsqueeze(2)) & before).any(2)
        first_valid = valid_t & ~torch.cat([torch.zeros_like(valid_t[:, :1]), valid_t[:, :-1]], dim=1)
        numbers[:, :, 6] = numbers[:, :, 6].masked_fill(first_valid, 0.0)
        numbers = torch.cat([numbers, new_dst.float().unsqueeze(2), new_port.float().unsqueeze(2)], dim=2)
        numbers = numbers.masked_fill(~valid_t.unsqueeze(2), 0.0)
        kinds = kinds.masked_fill(~valid_t.unsqueeze(2), 0)
        return numbers, kinds, ~valid_t


class FlowNet(nn.Module):
    def __init__(self, size: int = 64):
        super().__init__()
        self.proto = nn.Embedding(4, 8)
        self.port = nn.Embedding(15, 16)
        self.project = nn.Linear(9 + 24, size)
        self.position = nn.Parameter(torch.zeros(1, WINDOW, size))
        layer = nn.TransformerEncoderLayer(size, 4, size * 2, dropout=0.1, activation="gelu", batch_first=True)
        self.encoder = nn.TransformerEncoder(layer, 2, enable_nested_tensor=False)
        self.head = nn.Sequential(nn.Linear(size, size), nn.GELU(), nn.Linear(size, 1))

    def forward(self, numbers, kinds, mask):
        features = torch.cat([numbers, self.proto(kinds[:, :, 0]), self.port(kinds[:, :, 1])], dim=2)
        hidden = self.encoder(self.project(features) + self.position, src_key_padding_mask=mask)
        return self.head(hidden[:, -1]).squeeze(1)


def predict(model, data: Flows, device: str, rows: np.ndarray | None = None, batch: int = 4096) -> np.ndarray:
    model.eval()
    rows = data.rows if rows is None else rows
    scores = np.zeros(len(rows), dtype=np.float32)
    with torch.inference_mode():
        for start in range(0, len(rows), batch):
            chunk = rows[start : start + batch]
            scores[start : start + len(chunk)] = torch.sigmoid(model(*data.batch(chunk, device))).float().cpu().numpy()
    return scores


def metrics(y: np.ndarray, score: np.ndarray, threshold: float) -> dict:
    predicted = (score >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(y, predicted, average="binary", zero_division=0)
    negative = y == 0
    both = 0 < y.sum() < len(y)
    at_rate = {}
    if both:
        for rate in (0.01, 0.001):
            cut = np.quantile(score[negative], 1 - rate)
            at_rate[f"recall_at_{rate:g}_false_alarms"] = round(float((score[y == 1] > cut).mean()), 4)
    return {
        **at_rate,
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "false_alarm_rate": round(float(predicted[negative].mean()) if negative.any() else 0.0, 5),
        "auc": round(float(roc_auc_score(y, score)), 4) if both else None,
        "average_precision": round(float(average_precision_score(y, score)), 4) if both else None,
        "rows": int(len(y)),
        "attacks": int(y.sum()),
    }


def best_threshold(y: np.ndarray, score: np.ndarray) -> float:
    precision, recall, cut = precision_recall_curve(y, score)
    f1 = 2 * precision * recall / np.clip(precision + recall, 1e-9, None)
    return float(cut[int(np.argmax(f1[:-1]))])


def fit(train: Flows, valid: Flows, device: str, epochs: int, steps: int) -> tuple[nn.Module, float]:
    model = FlowNet().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    attack = train.rows[train.attack[train.rows] == 1]
    benign = train.rows[train.attack[train.rows] == 0]
    rng = np.random.default_rng(7)
    total = epochs * steps
    schedule = torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr=2e-3, total_steps=total)
    picked = np.sort(rng.choice(valid.rows, min(len(valid), 400_000), replace=False))
    best, best_state = -1.0, None
    started = time.time()
    for epoch in range(epochs):
        model.train()
        running = 0.0
        for _ in range(steps):
            positions = np.concatenate([rng.choice(attack, 512), rng.choice(benign, 512)])
            target = torch.from_numpy(train.attack[positions]).to(device)
            loss = nn.functional.binary_cross_entropy_with_logits(model(*train.batch(positions, device)), target)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            schedule.step()
            running += loss.item()
        score = predict(model, valid, device, picked)
        y = valid.attack[picked]
        ap = float(average_precision_score(y, score)) if 0 < y.sum() < len(y) else 0.0
        print(f"epoch {epoch + 1} loss {running / steps:.4f} valid AP {ap:.4f} {time.time() - started:.0f}s", flush=True)
        if ap >= best:
            best = ap
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    model.load_state_dict(best_state)
    return model, best_threshold(valid.attack[picked], predict(model, valid, device, picked))


def single_flow_features(data: Flows) -> np.ndarray:
    return np.hstack([data.numbers, data.kinds.astype(np.float32)])


def lightgbm_baseline(train: Flows, valid: Flows):
    rng = np.random.default_rng(7)
    rows = rng.choice(train.rows, min(len(train), 1_500_000), replace=False)
    booster = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.08, num_leaves=63, subsample=0.8, subsample_freq=1, class_weight="balanced", verbose=-1, n_jobs=8)
    booster.fit(single_flow_features(train)[rows], train.attack[rows].astype(int), categorical_feature=[7, 8])
    picked = rng.choice(valid.rows, min(len(valid), 400_000), replace=False)
    score = booster.predict_proba(single_flow_features(valid)[picked])[:, 1]
    return booster, best_threshold(valid.attack[picked], score)


def run(name: str, train: "Flows", valid: "Flows", tests: dict, device: str, args) -> dict:
    print(f"=== {name}", flush=True)
    print(len(train), "train flows", int(train.attack[train.rows].sum()), "attacks;", len(valid), "valid flows", int(valid.attack[valid.rows].sum()), "attacks", flush=True)
    model, threshold = fit(train, valid, device, args.epochs, args.steps)
    booster, booster_threshold = lightgbm_baseline(train, valid)
    report = {"threshold": threshold, "tests": {}}
    for test_name, test in tests.items():
        y = test.attack[test.rows].astype(int)
        started = time.time()
        score = predict(model, test, device)
        seconds = time.time() - started
        report["tests"][test_name] = {
            "flow_transformer": metrics(y, score, threshold),
            "lightgbm_single_flow": metrics(y, booster.predict_proba(single_flow_features(test)[test.rows])[:, 1], booster_threshold),
            "flows_per_second_gpu": round(len(test) / max(seconds, 1e-6)),
        }
        labels = test.table["label"].to_numpy()[test.rows]
        found = score >= threshold
        report["tests"][test_name]["recall_by_attack"] = {
            str(kind): round(float(found[labels == kind].mean()), 4) for kind in pd.unique(labels[y == 1])[:30]
        }
        print(test_name, json.dumps(report["tests"][test_name]), flush=True)
    return report, model, threshold


def export(model: nn.Module, threshold: float, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    model = model.cpu().eval()
    sample = (torch.zeros(1, WINDOW, 9), torch.zeros(1, WINDOW, 2, dtype=torch.long), torch.zeros(1, WINDOW, dtype=torch.bool))
    sample[2][0, :-1] = True
    torch.onnx.export(
        model,
        sample,
        str(OUT / "flow.onnx"),
        input_names=["numbers", "kinds", "mask"],
        output_names=["logit"],
        dynamic_axes={"numbers": {0: "batch"}, "kinds": {0: "batch"}, "mask": {0: "batch"}, "logit": {0: "batch"}},
        opset_version=17,
        dynamo=False,
    )
    (OUT / "meta.json").write_text(json.dumps({"name": name, "threshold": threshold, "window": WINDOW}, indent=1), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--only", nargs="+", default=["cic", "ctu"])
    args = parser.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(7)
    RESULTS.mkdir(exist_ok=True)
    names = sorted(path.stem for path in WORK.glob("cic_*.parquet"))
    by_day = {name.split("_", 1)[1]: name for name in names}
    path = RESULTS / "flows.json"
    report = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    if "cic" in args.only:
        first = [by_day[d] for d in ("monday", "tuesday", "wednesday")]
        tests = {d: Flows([by_day[d]]) for d in ("thursday", "friday")}
        report["cic_unseen_attack_days"], _, _ = run("cic_unseen_attack_days", Flows(first, (0, 0.8)), Flows(first, (0.8, 1)), tests, device, args)
        every = list(by_day.values())
        tests = {"later_flows_all_days": Flows(every, (0.8, 1))}
        report["cic_seen_attacks_later_time"], model, threshold = run("cic_seen_attacks_later_time", Flows(every, (0, 0.7)), Flows(every, (0.7, 0.8)), tests, device, args)
        export(model, threshold, "flow-transformer-cic2017")
    ctu = sorted(path.stem for path in WORK.glob("ctu_*.parquet"))
    if "ctu" in args.only and len(ctu) >= 6:
        held = ctu[-4:]
        tests = {name: Flows([name]) for name in held}
        report["ctu_leave_scenarios_out"], _, _ = run("ctu_leave_scenarios_out", Flows(ctu[:-5]), Flows([ctu[-5]]), tests, device, args)
    if "final" in args.only and len(ctu) >= 6:
        every = list(by_day.values())
        pool = every + ctu[:-4]
        tests = {"cic_later_flows": Flows(every, (0.8, 1))}
        tests.update({name: Flows([name]) for name in ctu[-4:]})
        report["final_both_datasets"], model, threshold = run("final_both_datasets", Flows(pool, (0, 0.7)), Flows(pool, (0.7, 0.8)), tests, device, args)
        export(model, threshold, "flow-transformer-cic2017-ctu13")
    path.write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("saved", flush=True)


if __name__ == "__main__":
    main()
