# Set up STL on another PC

These steps are for Windows 10 or 11. Run every command in **PowerShell**, not Git Bash.

Most people only need Parts 1 and 2.

| Part | What you get | Time | Disk |
|---|---|---|---|
| [1. Run the prototype](#part-1-run-the-prototype) | Dashboard, gateways and fast models | 15 minutes | 1 GB |
| [2. Add the language model](#part-2-add-the-language-model) | The full system, as in the paper | 20 minutes | 7 GB |
| [3. Retrain and retest](#part-3-retrain-and-retest) | New models and new test results | About 8 hours, plus downloads | 10 GB |
| [4. Build the documents](#part-4-build-the-documents) | The paper and architecture PDFs | 5 minutes | 100 MB |

## Quick start with Docker

This runs the same thing as Parts 1 and 2 in two containers: STL and Ollama with the language model. It works on Windows, Linux and macOS.

1. Install Docker Desktop and open it once. On Windows:

   ```powershell
   winget install --id Docker.DockerDesktop -e
   ```

   Restart the PC if it asks. On Linux, install Docker Engine, and for an NVIDIA graphics card also the NVIDIA Container Toolkit.

2. Get the code:

   ```powershell
   git clone https://github.com/AbdulGhani002/semantic-trust-layer.git stl
   cd stl
   ```

3. Start it. With an NVIDIA graphics card:

   ```powershell
   docker compose -f compose.yaml -f compose.gpu.yaml up -d --build
   ```

   Without one:

   ```powershell
   docker compose up -d --build
   ```

   The first start downloads everything by itself: the Python packages, the 6.6 GB language model, the trained models (`models-v1`, 85 MB) and the training checkpoints (`checkpoints-v1`, 707 MB). Follow it with `docker compose logs -f stl`. Later starts skip the downloads and take about a minute.

   If the repo is ever made private again, give the container a GitHub token first: `$env:GH_TOKEN = gh auth token`.

4. Open http://127.0.0.1:8050. The top bar should say all four models are on.

| Task | Command |
|---|---|
| See if it is ready | `docker compose ps` |
| Follow the log | `docker compose logs -f stl` |
| Run the unit tests | `docker compose exec stl python -m pytest -q` |
| Stop it | `docker compose down` |
| Rebuild after `git pull` | Run the start command again |

`docker compose down` keeps the language model, the trained models and STL's data (signing keys, verdicts) in Docker volumes. `docker compose down -v` deletes them too, so the next start downloads everything again.

Without Docker, the same download works with `.venv\Scripts\python -m stl.cli download --checkpoints` (leave out `--checkpoints` to get only the 85 MB of trained models).

The ports only open on this PC. To let other devices on the network reach the dashboard, remove `127.0.0.1:` from the ports in `compose.yaml`. The dashboard has no login, so do this only on a network you trust.

## What the PC needs

| | Needed | What we used |
|---|---|---|
| System | Windows 10 or 11, 64-bit | Windows 11 |
| Memory | 8 GB for Part 1, 16 GB for the rest | 16 GB |
| Graphics card | None for Part 1. NVIDIA with 6 GB for Parts 2 and 3 | RTX 4050 Laptop, 6 GB |

Without a graphics card, the language model runs on the processor. It still works, but each item takes much longer than 2 seconds, and training the text model is not practical.

## Part 1: Run the prototype

### 1. Install the tools

```powershell
winget install --id Git.Git -e
winget install --id GitHub.cli -e
winget install --id Python.Python.3.13 -e
```

Close PowerShell and open it again, so it can find the new tools. If `winget` is missing, install them from [git-scm.com](https://git-scm.com), [cli.github.com](https://cli.github.com) and [python.org](https://www.python.org) (tick "Add to PATH").

### 2. Sign in to GitHub

The repo is public, so anyone can clone it. Signing in is still needed for `gh release download` below, and to push changes, which needs collaborator access (repo Settings, Collaborators).

```powershell
gh auth login
```

Pick GitHub.com, then HTTPS, then Login with a web browser.

### 3. Get the code

```powershell
mkdir C:\CC\Code -Force
cd C:\CC\Code
gh repo clone AbdulGhani002/semantic-trust-layer stl
cd stl
```

Stay in this folder for all the steps below.

### 4. Install the Python packages

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]" -c requirements-lock.txt
```

`requirements-lock.txt` holds the exact versions behind our results. You do not need to activate the environment, because every command here calls `.venv\Scripts` directly.

### 5. Get the trained models

They are in a GitHub release, because `text.onnx` is too big for a normal Git file.

```powershell
gh release download models-v1
tar -xf stl-models.zip
del stl-models.zip
```

This makes the `models` folder.

### 6. Check the code

```powershell
.venv\Scripts\python -m pytest
```

You should see `42 passed`.

### 7. Start it

```powershell
.venv\Scripts\python -m stl.cli serve
```

Open http://127.0.0.1:8050 and leave this window running. Press Ctrl+C to stop it.

Use this exact command. Windows Smart App Control can block `.venv\Scripts\stl.exe`, because pip makes that file unsigned on each PC.

The first start makes this PC's signing keys in `data\keys`. Part 1 runs without the language model, so results are not the same as in the paper. With it off, more clean messages get flagged.

## Part 2: Add the language model

Stop STL first with Ctrl+C, then install Ollama and the model. The model is a 6.6 GB download.

```powershell
winget install --id Ollama.Ollama -e
```

Close PowerShell and open it again in the `stl` folder.

```powershell
ollama pull qwen3.5:9b
ollama list
```

The ID should be `56671c2ab938`, the same model we tested. Ollama keeps running in the system tray. If it is not running, start it from the Start menu.

Start STL again. It looks for Ollama only when it starts, so Ollama must be running first.

```powershell
.venv\Scripts\python -m stl.cli serve
```

Open a second PowerShell in the `stl` folder and run all 13 demos:

```powershell
.venv\Scripts\python training\run_scenarios.py
```

You should see `12 of 13 scenarios behaved as expected`. This is the normal result: the Urdu threat only gets a warning, because the model's confidence of 0.85 is under the 0.9 cut-off. The first demo takes about 20 seconds while the model loads. After that, each one should take 2 to 3 seconds with a 6 GB graphics card.

This command rewrites `results\scenarios.json`. To put it back:

```powershell
git restore results\scenarios.json
```

To check that the model is on the graphics card, run `ollama ps` while a demo runs. It should say `100% GPU`.

## Part 3: Retrain and retest

Do this only if you want new models or new results. Text training needs an NVIDIA graphics card.

### 1. Install the training packages

```powershell
.venv\Scripts\python -m pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cu128
.venv\Scripts\python -m pip install -e ".[dev,train]" -c requirements-lock.txt
```

The first line gets the graphics card build of PyTorch, about 2.5 GB. Run them in this order, or pip installs the slow processor build.

### 2. Get the checkpoints (optional)

You only need these to continue text training with `--resume`, or to export `text.onnx` again with `training\export_text.py`. They are a 740 MB download.

```powershell
gh release download checkpoints-v1
tar -xf stl-checkpoints.zip
del stl-checkpoints.zip
```

| File | What it is |
|---|---|
| `models\text\best.pt` | Final text model |
| `models\text\epoch1\` | Text model after the first epoch |
| `models\url\best.pt` | Link model |

### 3. Get the data

You have two choices.

**Same data as ours:** copy `data\raw` and `data\work` from the first PC with a USB drive (4 GB). Then skip the three `prepare_` commands in step 4. Do not put these folders on GitHub.

**Fresh download:** about 3.4 GB. Live feeds such as OpenPhish change every day, so your numbers will differ a little from ours.

```powershell
.venv\Scripts\python training\download_data.py quick text traffic commoncrawl abuse
mkdir data\raw\traffic_mawi -Force
curl.exe -L -r 0-314572799 -o data\raw\traffic_mawi\202611041400-first-300MB.pcap.gz https://mawi.wide.ad.jp/mawi/samplepoint-F/2026/202611041400.pcap.gz
```

The last line takes only the first 300 MB of a large backbone capture. Phishing links are saved as plain text and are never opened.

### 4. Train the models

Unload the language model first, or the graphics card runs out of memory. Run the commands in this order.

```powershell
ollama stop qwen3.5:9b
.venv\Scripts\python training\prepare_text.py
.venv\Scripts\python training\train_text.py --epochs 1 --batch 16 --accumulate 2 --max-length 128
.venv\Scripts\python training\train_text.py --epochs 1 --batch 16 --accumulate 2 --max-length 128 --lr 1.5e-5 --resume
.venv\Scripts\python training\prepare_urls.py
.venv\Scripts\python training\train_url.py
.venv\Scripts\python training\prepare_flows.py
.venv\Scripts\python training\train_flows.py
.venv\Scripts\python training\train_anomaly.py
.venv\Scripts\python training\evaluate_cross.py
.venv\Scripts\python training\train_flows.py --only final
.venv\Scripts\python training\make_demo_flows.py
.venv\Scripts\python training\make_test_fixtures.py
.venv\Scripts\python training\evaluate_backbone.py
```

Each `train_text` run takes about an hour on an RTX 4050. The link and traffic steps take about an hour and a half together. The order of the traffic steps matters: `train_anomaly` and `evaluate_cross` need the model from the first `train_flows`, and `--only final` then replaces it with the final model.

### 5. Run all the tests

Ollama must be running. Keep the PC plugged in and stop it from sleeping, because a reboot stops the run.

```powershell
& "C:\Program Files\Git\bin\bash.exe" training/run_tests.sh
```

This takes about three and a half hours. Logs go to `logs\`, and `logs\run_tests.done` appears at the end with an exit code for each step.

### 6. Finish

Start STL in one window with `.venv\Scripts\python -m stl.cli serve`. In a second window, run:

```powershell
.venv\Scripts\python training\run_scenarios.py
.venv\Scripts\python docs\make_tables.py
.venv\Scripts\python -m pytest
```

`make_tables.py` turns the new results into the tables and numbers used in the documents.

## Part 4: Build the documents

Tectonic builds both PDFs. This puts it in `.tools`, which Git ignores.

```powershell
mkdir .tools -Force
curl.exe -L -o .tools\tectonic.zip https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.17.0/tectonic-0.17.0-x86_64-pc-windows-msvc.zip
tar -xf .tools\tectonic.zip -C .tools
del .tools\tectonic.zip
```

Then build:

```powershell
cd docs
mkdir paper\build -Force
..\.tools\tectonic.exe -X compile STL-Paper.tex --outdir paper/build
..\.tools\tectonic.exe -X compile STL-Architecture.tex --outdir paper/build
cd ..
```

The PDFs appear in `docs\paper\build`. The first build downloads its fonts and packages, so it needs the Internet.

## What is not on GitHub

| Path | What it is | How a new PC gets it |
|---|---|---|
| `.venv\` | Python packages | Part 1, step 4 |
| `models\` | Trained models | Part 1, step 5 |
| `models\**\best.pt` | Training checkpoints | Part 3, step 2 |
| `data\raw\`, `data\work\` | Datasets | Part 3, step 3 |
| `data\keys\` | Private signing keys | Made on the first start |
| `data\stl.db`, `data\mailbox\` | Verdicts and test mail | Start empty |

Each PC signs with its own keys. Copy `data\keys` by hand only if a new PC must sign as the same agents, and never put those keys on GitHub.

## Settings

Set these before you start STL, if you need them. For example: `$env:STL_REVIEW_GATE = "0.02"`.

| Setting | Default | What it does |
|---|---|---|
| `STL_REVIEW_MODEL` | `qwen3.5:9b` | Language model name |
| `STL_OLLAMA` | `http://127.0.0.1:11434` | Where Ollama runs |
| `STL_KEEP_ALIVE` | `60m` | How long the language model stays loaded on the graphics card after the last item. STL also loads it when it starts, so the first item is fast |
| `STL_REVIEW_GATE` | `0` | Fast risk an item needs before the language model reads it. Raising it saves time on a slow PC but misses polite and veiled messages |
| `STL_GATEWAY_HOST` | `127.0.0.1` | Address the SMTP gateway and HTTP proxy listen on. The Docker image sets `0.0.0.0` |

STL uses ports 8050 (dashboard), 8025 (SMTP gateway), 8026 (HTTP proxy) and 11434 (Ollama). They all stay on this PC.

## If something goes wrong

| Problem | Fix |
|---|---|
| `gh`, `python` or `ollama` is not recognised | Close PowerShell and open it again |
| `python` opens the Microsoft Store | In Windows Settings, search for App execution aliases and turn off the two Python entries |
| `running scripts is disabled` | You ran `activate`. You do not need it here. Use the `.venv\Scripts\...` commands as written |
| `repository not found` when cloning | Your GitHub account has no access yet, or you signed in to another account |
| `An Application Control policy has blocked this file` | Windows Smart App Control blocked `stl.exe`. Start STL with `.venv\Scripts\python -m stl.cli serve` |
| `tar` cannot read the zip | You are in Git Bash. Use PowerShell |
| `gh release download` says the file exists | Delete the old zip and run it again |
| The dashboard says the language model is off | Start Ollama, then stop and start STL |
| An address or port is already in use | Another copy is running. Close it, or add `--port 8051 --no-gateways` to the start command |
| Each item takes much longer than 2 seconds | Run `ollama ps`. If it does not say `100% GPU`, close other programs that use the graphics card |
| `CUDA out of memory` during training | Run `ollama stop qwen3.5:9b` and close other programs, or lower `--batch` |

## What was tested

Tested on 6 November 2026 from a clean clone with a new Python environment, on the laptop we used for the paper, with Smart App Control on:

- Part 1, steps 3 to 7: all 42 unit tests passed.
- The demos in Part 2: 12 of 13, with the same actions and risks as the original copy.
- Part 4: both PDFs came out the same size as the originals.

Versions: Python 3.13.15, Ollama 0.40.14, Tectonic 0.17.0. The tools and the Ollama model were already on that laptop, so the `winget` lines and the 6.6 GB download were not run again, and this was not a separate PC.

Part 3 uses the commands that built our results, but it has not been rerun from a clean copy. Only its package versions and the checkpoint download were checked. The restored checkpoints matched the originals exactly.
