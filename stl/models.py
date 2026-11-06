"""Load the trained models and run them with ONNX Runtime."""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

from .schema import CONTENT_LABELS

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"
CLS, PAD, SEP = 0, 1, 2
MAX_WINDOWS = 8
SENTENCE = re.compile(r"(?<=[.!?\n])\s+")


def session(path: Path) -> ort.InferenceSession:
    options = ort.SessionOptions()
    options.log_severity_level = 3
    return ort.InferenceSession(str(path), options, providers=["CPUExecutionProvider"])


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


def risk_from_score(score: float, threshold: float) -> float:
    """Map a model score so that the operating threshold sits at 0.5."""
    threshold = min(max(threshold, 1e-4), 1 - 1e-4)
    if score < threshold:
        return float(0.5 * score / threshold)
    return float(0.5 + 0.5 * (score - threshold) / (1 - threshold))


class TextModel:
    def __init__(self, folder: Path = MODELS / "text"):
        self.session = session(folder / "text.onnx")
        self.tokenizer = Tokenizer.from_file(str(folder / "tokenizer" / "tokenizer.json"))
        self.tokenizer.no_truncation()
        self.tokenizer.no_padding()
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        self.max_length = int(meta["max_length"])
        self.labels = tuple(meta["labels"])
        limits = json.loads((folder / "thresholds.json").read_text(encoding="utf-8"))
        self.thresholds = {name: float(limits[name]["threshold"]) for name in CONTENT_LABELS}
        self.version = f"{meta['base_model'].split('/')[-1]}+stl"

    def _windows(self, text: str) -> list[list[int]]:
        ids = self.tokenizer.encode(text, add_special_tokens=False).ids
        size = self.max_length - 2
        stride = max(1, int(size * 0.75))
        chunks = [ids[start : start + size] for start in range(0, max(1, len(ids)), stride)][:MAX_WINDOWS]
        return [[CLS, *chunk, SEP] for chunk in chunks]

    def _run(self, windows: list[list[int]]) -> np.ndarray:
        width = max(len(window) for window in windows)
        ids = np.full((len(windows), width), PAD, dtype=np.int64)
        mask = np.zeros((len(windows), width), dtype=np.int64)
        for row, window in enumerate(windows):
            ids[row, : len(window)] = window
            mask[row, : len(window)] = 1
        logits = self.session.run(None, {"input_ids": ids, "attention_mask": mask})[0]
        return sigmoid(logits)

    def score(self, text: str) -> dict[str, float]:
        probabilities = self._run(self._windows(text)).max(axis=0)
        return {label: float(value) for label, value in zip(self.labels, probabilities)}

    def score_many(self, texts: list[str], batch: int = 64) -> np.ndarray:
        result = np.zeros((len(texts), len(self.labels)), dtype=np.float32)
        windows, owners = [], []
        for index, text in enumerate(texts):
            for window in self._windows(text):
                windows.append(window)
                owners.append(index)
        order = np.argsort([len(w) for w in windows])
        for start in range(0, len(order), batch):
            picked = order[start : start + batch]
            scores = self._run([windows[i] for i in picked])
            for position, index in enumerate(picked):
                owner = owners[index]
                result[owner] = np.maximum(result[owner], scores[position])
        return result

    def influential_words(self, text: str, label: str, limit: int = 4) -> list[tuple[str, float]]:
        """Find the words the model relied on, by hiding each one and rescoring."""
        index = self.labels.index(label)
        parts = [p for p in SENTENCE.split(text) if p.strip()] or [text]
        focus = max(parts[:40], key=lambda part: self.score(part)[label])
        words = focus.split()[:48]
        if len(words) < 2:
            return [(focus.strip(), self.score(focus)[label])]
        base = self.score(" ".join(words))[label]
        hidden = [" ".join(words[:i] + words[i + 1 :]) for i in range(len(words))]
        scores = self.score_many(hidden)[:, index]
        drops = sorted(zip(words, (base - scores).tolist()), key=lambda pair: -pair[1])
        return [(word.strip(".,;:!?\"'()"), round(drop, 3)) for word, drop in drops[:limit] if drop > 0.02]


class UrlModel:
    def __init__(self, folder: Path = MODELS / "url"):
        self.session = session(folder / "url.onnx")
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        self.max_chars = int(meta["max_chars"])
        self.threshold = float(meta["threshold"])
        self.version = "url-charnet"

    @staticmethod
    def normalise(url: str) -> str:
        url = url.strip().lower()
        for prefix in ("https://", "http://", "ftp://"):
            if url.startswith(prefix):
                url = url[len(prefix) :]
                break
        if url.startswith("www."):
            url = url[4:]
        return url.rstrip("/")

    def score_many(self, urls: list[str]) -> np.ndarray:
        ids = np.zeros((len(urls), self.max_chars), dtype=np.int64)
        for row, url in enumerate(urls):
            for col, char in enumerate(self.normalise(url)[: self.max_chars]):
                code = ord(char)
                ids[row, col] = code if 2 <= code < 128 else 1
        return sigmoid(self.session.run(None, {"ids": ids})[0]).reshape(-1)

    def score(self, url: str) -> float:
        return float(self.score_many([url])[0])
