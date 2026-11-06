# Semantic Trust Layer (STL)

An AI layer that checks incoming data by meaning. Two AI agents look at the same item at the same time:

- **Application Agent** reads the content: email, message, link, QR code or file text.
- **Network Agent** reads how the traffic behaves: timing, sizes, ports, and DNS and TLS names. It never reads content.
- **Coordinator** joins both findings into one signed verdict: allow, warn, flag or block, with the reason.

Keyword lists and fixed rules do not decide. Trained models do, and a local language model reads all text on its own, without being told what any other model thinks. A bare link reaches it only if the link model flagged it.

This is a final year project prototype. Agents run on one machine, and the two-agent test pairs real content with real traffic from separate sources, because no public data links both layers.

## Run it

**[SETUP.md](SETUP.md) has every step for a new PC**, from installing the tools to retraining the models and building the documents.

In short, in PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]" -c requirements-lock.txt
gh release download models-v1
tar -xf stl-models.zip
.venv\Scripts\python -m stl.cli serve
```

Then open http://127.0.0.1:8050. Ollama with `qwen3.5:9b` is optional, and adds the language model review.

Some files are not in Git. The trained models are in the `models-v1` release, because `text.onnx` is over GitHub's 100 MB file limit. The training checkpoints are in the `checkpoints-v1` release. `training/download_data.py` fetches the raw data, and `data/manifest.json` lists every source with its licence. Signing keys are made on the first run and stay on your machine.

## Use the dashboard

- **Run a scenario:** 13 ready demos go through the real agents. Emails travel as real SMTP sessions.
- **Verdict queue:** every item, with both agents' findings and the signature check.
- **Check an item:** paste a message or link, or upload a QR image or file.
- **Test QR codes:** fake codes on reserved test names that cannot reach any real website.
- **Test results:** measured results from the `results/` folder.

## Train and test

[SETUP.md, Part 3](SETUP.md#part-3-retrain-and-retest) lists every command in order.

Unload the language model before training the text model, or the GPU runs out of memory. `run_tests.sh` runs every test that uses the language model, in order. It starts with `compare_prompts.py` and `compare_link_rules.py`, which show how the review prompt and the decision rules were chosen on validation rows. `run_scenarios.py` needs `stl serve` running.

## Folders

| Path | What it holds |
|---|---|
| `stl/` | Agents, Coordinator, signing, gateway, API and dashboard |
| `training/` | Data preparation, training and evaluation scripts |
| `tests/` | Unit tests, fake links, fake QR codes and test messages |
| `results/` | Measured results |
| `docs/` | Plan, architecture document and paper draft. `docs/generated/` is written by `make_tables.py` |
| `reports/`, `research_notes/` | Related work |

## Safety

- Live phishing links are stored as text and are never opened.
- No malware files are downloaded.
- Every fake fraud link uses a reserved name such as `.test`, or a documentation IP address.
- A flag is a warning for a person to review. It is not proof that someone did wrong.
