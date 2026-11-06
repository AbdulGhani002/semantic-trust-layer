"""Train the Application Agent's text model and export it to ONNX.

A multilingual transformer reads the text and scores four labels at once:
threat, hate, abuse and fraud. Toxic training text is sometimes respelled so
the model learns to see through disguised words.
"""
import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import average_precision_score, precision_recall_curve
from torch import nn
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
from transformers import AutoModel, AutoTokenizer, get_linear_schedule_with_warmup

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "data" / "work"
OUT = ROOT / "models" / "text"
LABELS = ["threat", "hate", "abuse", "fraud"]
RESPELL = {"a": "@", "e": "3", "i": "1", "o": "0", "s": "$", "g": "9", "t": "7"}


def respell(text: str, rng: random.Random) -> str:
    words = text.split(" ")
    for index, word in enumerate(words):
        if len(word) > 3 and rng.random() < 0.25:
            letters = list(word)
            spot = rng.randrange(len(letters))
            letters[spot] = RESPELL.get(letters[spot].lower(), letters[spot])
            words[index] = "".join(letters)
    return " ".join(words)


class TextSet(Dataset):
    def __init__(self, table: pd.DataFrame, train: bool):
        self.text = table["text"].tolist()
        self.labels = table[LABELS].to_numpy(dtype=np.float32)
        self.train = train
        self.rng = random.Random(11)

    def __len__(self):
        return len(self.text)

    def __getitem__(self, index):
        text = self.text[index]
        toxic = (self.labels[index, :3] == 1).any()
        if self.train and toxic and self.rng.random() < 0.2:
            text = respell(text, self.rng)
        return text, self.labels[index]


class TextNet(nn.Module):
    def __init__(self, name: str):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(name, add_pooling_layer=False)
        self.dropout = nn.Dropout(0.1)
        self.head = nn.Linear(self.encoder.config.hidden_size, len(LABELS))

    def forward(self, input_ids, attention_mask):
        hidden = self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        mask = attention_mask.unsqueeze(-1).float()
        pooled = (hidden * mask).sum(1) / mask.sum(1).clamp(min=1e-6)
        return self.head(self.dropout(pooled))


def masked_loss(logits, target, weights):
    known = (target >= 0).float()
    loss = nn.functional.binary_cross_entropy_with_logits(
        logits, target.clamp(min=0), pos_weight=weights, reduction="none"
    )
    return (loss * known).sum() / known.sum().clamp(min=1)


def predict(model, tokenizer, texts, device, max_length, batch=48):
    model.eval()
    scores = []
    order = np.argsort([len(t) for t in texts])
    with torch.inference_mode(), torch.autocast("cuda", enabled=device == "cuda"):
        for start in range(0, len(texts), batch):
            chunk = [texts[i] for i in order[start : start + batch]]
            encoded = tokenizer(chunk, truncation=True, max_length=max_length, padding=True, return_tensors="pt").to(device)
            scores.append(torch.sigmoid(model(encoded["input_ids"], encoded["attention_mask"])).float().cpu().numpy())
    merged = np.concatenate(scores)
    result = np.zeros_like(merged)
    result[order] = merged
    return result


def choose_thresholds(scores, labels):
    chosen = {}
    for index, name in enumerate(LABELS):
        known = labels[:, index] >= 0
        y, s = labels[known, index], scores[known, index]
        if y.sum() == 0:
            chosen[name] = {"threshold": 0.5, "average_precision": None}
            continue
        precision, recall, cut = precision_recall_curve(y, s)
        f1 = 2 * precision * recall / np.clip(precision + recall, 1e-9, None)
        best = int(np.argmax(f1[:-1]))
        chosen[name] = {
            "threshold": float(cut[best]),
            "f1": float(f1[best]),
            "precision": float(precision[best]),
            "recall": float(recall[best]),
            "average_precision": float(average_precision_score(y, s)),
        }
    return chosen


def export(model, tokenizer, max_length):
    from onnxruntime.quantization import QuantType, quantize_dynamic

    model = model.float().eval().cpu()
    sample = tokenizer(["export sample"], truncation=True, max_length=max_length, padding="max_length", return_tensors="pt")
    path = OUT / "text_float.onnx"
    torch.onnx.export(
        model,
        (sample["input_ids"], sample["attention_mask"]),
        str(path),
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={"input_ids": {0: "batch", 1: "length"}, "attention_mask": {0: "batch", 1: "length"}, "logits": {0: "batch"}},
        opset_version=17,
        dynamo=False,
    )
    quantize_dynamic(str(path), str(OUT / "text.onnx"), weight_type=QuantType.QInt8)
    path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="microsoft/Multilingual-MiniLM-L12-H384")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--lr", type=float, default=3e-5)
    parser.add_argument("--max-length", type=int, default=160)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--accumulate", type=int, default=1)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    torch.manual_seed(13 if args.resume else 7)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    OUT.mkdir(parents=True, exist_ok=True)
    train = pd.read_parquet(WORK / "text_train.parquet")
    valid = pd.read_parquet(WORK / "text_valid.parquet")
    if args.limit:
        train = train.sample(n=args.limit, random_state=7)
        valid = valid.sample(n=min(args.limit // 5, len(valid)), random_state=7)

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    labels = train[LABELS].to_numpy()
    positive = np.array([(labels[:, i] == 1).sum() for i in range(len(LABELS))], dtype=float)
    known = np.array([(labels[:, i] >= 0).sum() for i in range(len(LABELS))], dtype=float)
    pos_weight = torch.tensor(np.clip(np.sqrt((known - positive) / np.clip(positive, 1, None)), 1, 12), dtype=torch.float32, device=device)
    rarity = 1 / np.clip(positive / known, 1e-4, None)
    sample_weight = 1 + ((labels == 1) * (rarity / rarity.max()) * 12).sum(axis=1)

    def collate(rows):
        texts, targets = zip(*rows)
        encoded = tokenizer(list(texts), truncation=True, max_length=args.max_length, padding=True, return_tensors="pt")
        return encoded, torch.tensor(np.stack(targets))

    loader = DataLoader(
        TextSet(train, True),
        batch_size=args.batch,
        sampler=WeightedRandomSampler(sample_weight, len(train), replacement=True),
        collate_fn=collate,
        num_workers=0,
        pin_memory=True,
    )
    model = TextNet(args.model).to(device)
    best = -1.0
    if args.resume:
        model.load_state_dict(torch.load(OUT / "best.pt", map_location=device))
        earlier = json.loads((OUT / "thresholds.json").read_text(encoding="utf-8"))
        best = float(np.mean([v["average_precision"] for v in earlier.values()]))
        print(f"resumed from mean average precision {best:.4f}", flush=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    steps = len(loader) * args.epochs // args.accumulate
    schedule = get_linear_schedule_with_warmup(optimizer, int(0.05 * steps), steps)
    scaler = torch.amp.GradScaler("cuda", enabled=device == "cuda")
    log = []
    started = time.time()
    for epoch in range(args.epochs):
        model.train()
        running = 0.0
        skipped = 0
        optimizer.zero_grad(set_to_none=True)
        for step, (encoded, target) in enumerate(loader, 1):
            try:
                encoded = encoded.to(device)
                target = target.to(device)
                with torch.autocast("cuda", enabled=device == "cuda"):
                    loss = masked_loss(model(encoded["input_ids"], encoded["attention_mask"]), target, pos_weight)
                scaler.scale(loss / args.accumulate).backward()
                if step % args.accumulate == 0:
                    scaler.unscale_(optimizer)
                    nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    scaler.step(optimizer)
                    scaler.update()
                    schedule.step()
                    optimizer.zero_grad(set_to_none=True)
                running += loss.item()
            except RuntimeError as error:
                if "out of memory" not in str(error):
                    raise
                skipped += 1
                del encoded, target
                optimizer.zero_grad(set_to_none=True)
                try:
                    torch.cuda.empty_cache()
                except RuntimeError:
                    pass
                time.sleep(2)
            if step % 500 == 0:
                print(f"epoch {epoch + 1} step {step}/{len(loader)} loss {running / 500:.4f} skipped {skipped} {time.time() - started:.0f}s", flush=True)
                running = 0.0
        scores = predict(model, tokenizer, valid["text"].tolist(), device, args.max_length)
        thresholds = choose_thresholds(scores, valid[LABELS].to_numpy())
        mean_ap = np.mean([v["average_precision"] for v in thresholds.values() if v["average_precision"] is not None])
        log.append({"epoch": epoch + 1, "mean_ap": float(mean_ap), "labels": thresholds})
        print(json.dumps(log[-1]), flush=True)
        if mean_ap > best:
            best = float(mean_ap)
            torch.save(model.state_dict(), OUT / "best.pt")
            (OUT / "thresholds.json").write_text(json.dumps(thresholds, indent=1), encoding="utf-8")

    model.load_state_dict(torch.load(OUT / "best.pt", map_location=device))
    tokenizer.save_pretrained(OUT / "tokenizer")
    meta = {
        "base_model": args.model,
        "labels": LABELS,
        "max_length": args.max_length,
        "epochs": args.epochs,
        "train_rows": len(train),
        "seconds": time.time() - started,
        "log": log,
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    export(model, tokenizer, args.max_length)
    print("exported", flush=True)


if __name__ == "__main__":
    main()
