"""Export the best text model so far to ONNX, without touching the GPU."""
import json
from pathlib import Path

import torch
from transformers import AutoTokenizer

from train_text import LABELS, OUT, TextNet, export

NAME = "microsoft/Multilingual-MiniLM-L12-H384"
MAX_LENGTH = 128


def main() -> None:
    tokenizer = AutoTokenizer.from_pretrained(NAME)
    model = TextNet(NAME)
    model.load_state_dict(torch.load(OUT / "best.pt", map_location="cpu"))
    tokenizer.save_pretrained(OUT / "tokenizer")
    meta = {"base_model": NAME, "labels": LABELS, "max_length": MAX_LENGTH, "note": "exported from the best checkpoint so far"}
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    export(model, tokenizer, MAX_LENGTH)
    print("exported", Path(OUT / "text.onnx").stat().st_size)


if __name__ == "__main__":
    main()
