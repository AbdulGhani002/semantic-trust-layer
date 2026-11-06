"""Train the link model: a character-level network that reads a URL as text."""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import average_precision_score, precision_recall_curve
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "data" / "work"
OUT = ROOT / "models" / "url"
MAX_CHARS = 200


def encode(urls: list[str]) -> np.ndarray:
    ids = np.zeros((len(urls), MAX_CHARS), dtype=np.int64)
    for row, url in enumerate(urls):
        for col, char in enumerate(url[:MAX_CHARS]):
            code = ord(char)
            ids[row, col] = code if 2 <= code < 128 else 1
    return ids


class UrlNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed = nn.Embedding(128, 48, padding_idx=0)
        self.grams = nn.ModuleList(nn.Conv1d(48, 96, size, padding=size // 2) for size in (3, 5, 7))
        self.deep = nn.Sequential(
            nn.Conv1d(288, 192, 3, padding=1), nn.GELU(), nn.Conv1d(192, 192, 3, padding=2, dilation=2), nn.GELU()
        )
        self.head = nn.Sequential(nn.Dropout(0.2), nn.Linear(384, 128), nn.GELU(), nn.Linear(128, 1))

    def forward(self, ids):
        mask = (ids > 0).float().unsqueeze(1)
        x = self.embed(ids).transpose(1, 2)
        x = torch.cat([conv(x).relu() for conv in self.grams], dim=1)
        x = self.deep(x) * mask
        mean = x.sum(2) / mask.sum(2).clamp(min=1)
        peak = x.max(2).values
        return self.head(torch.cat([mean, peak], dim=1)).squeeze(1)


def scores(model, ids, device, batch=2048):
    model.eval()
    parts = []
    with torch.inference_mode():
        for start in range(0, len(ids), batch):
            chunk = torch.from_numpy(ids[start : start + batch]).to(device)
            parts.append(torch.sigmoid(model(chunk)).cpu().numpy())
    return np.concatenate(parts)


def main() -> None:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(7)
    OUT.mkdir(parents=True, exist_ok=True)
    train = pd.read_parquet(WORK / "url_train.parquet")
    valid = pd.read_parquet(WORK / "url_valid.parquet")
    print(len(train), "train", len(valid), "valid", flush=True)
    data = TensorDataset(torch.from_numpy(encode(train["url"].tolist())), torch.tensor(train["label"].to_numpy(), dtype=torch.float32))
    loader = DataLoader(data, batch_size=512, shuffle=True, drop_last=True, pin_memory=True)
    valid_ids = encode(valid["url"].tolist())
    y_valid = valid["label"].to_numpy()
    model = UrlNet().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    epochs = 5
    schedule = torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr=2e-3, total_steps=epochs * len(loader))
    pos_weight = torch.tensor([(train["label"] == 0).sum() / max(1, (train["label"] == 1).sum())], device=device)
    best = -1.0
    started = time.time()
    for epoch in range(epochs):
        model.train()
        for ids, target in loader:
            ids, target = ids.to(device), target.to(device)
            loss = nn.functional.binary_cross_entropy_with_logits(model(ids), target, pos_weight=pos_weight)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            schedule.step()
        s = scores(model, valid_ids, device)
        ap = float(average_precision_score(y_valid, s))
        print(f"epoch {epoch + 1} valid AP {ap:.4f} {time.time() - started:.0f}s", flush=True)
        if ap > best:
            best = ap
            torch.save(model.state_dict(), OUT / "best.pt")
    model.load_state_dict(torch.load(OUT / "best.pt", map_location=device))
    s = scores(model, valid_ids, device)
    precision, recall, cut = precision_recall_curve(y_valid, s)
    f1 = 2 * precision * recall / np.clip(precision + recall, 1e-9, None)
    index = int(np.argmax(f1[:-1]))
    meta = {
        "max_chars": MAX_CHARS,
        "threshold": float(cut[index]),
        "valid_f1": float(f1[index]),
        "valid_ap": best,
        "train_rows": len(train),
        "seconds": time.time() - started,
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    model = model.cpu().eval()
    torch.onnx.export(
        model,
        (torch.zeros(1, MAX_CHARS, dtype=torch.long),),
        str(OUT / "url.onnx"),
        input_names=["ids"],
        output_names=["logit"],
        dynamic_axes={"ids": {0: "batch"}, "logit": {0: "batch"}},
        opset_version=17,
        dynamo=False,
    )
    print(json.dumps(meta), flush=True)


if __name__ == "__main__":
    main()
