"""Download the trained models and training checkpoints from the GitHub releases."""
from __future__ import annotations

import json
import os
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

REPO = os.environ.get("STL_REPO", "AbdulGhani002/semantic-trust-layer")
RELEASES = {"models-v1": "stl-models.zip", "checkpoints-v1": "stl-checkpoints.zip"}
CHUNK = 1 << 20


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def _headers(token: str | None, accept: str) -> dict:
    headers = {"Accept": accept, "User-Agent": "stl-download"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _asset_url(tag: str, name: str, token: str | None) -> str:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/releases/tags/{tag}",
        headers=_headers(token, "application/vnd.github+json"),
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            release = json.load(response)
    except urllib.error.HTTPError as error:
        if error.code in (401, 403, 404):
            raise SystemExit(
                f"Cannot read release {tag} of {REPO}. If the repo is private, set GH_TOKEN to a GitHub token "
                "with access to it (for example the output of: gh auth token)."
            ) from None
        raise
    for asset in release.get("assets", []):
        if asset["name"] == name:
            return asset["url"]
    raise SystemExit(f"Release {tag} has no file named {name}")


def _open(url: str, token: str | None):
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        return opener.open(urllib.request.Request(url, headers=_headers(token, "application/octet-stream")), timeout=60)
    except urllib.error.HTTPError as error:
        if error.code not in (301, 302, 303, 307, 308):
            raise
        location = error.headers["Location"]
    return urllib.request.urlopen(urllib.request.Request(location, headers={"User-Agent": "stl-download"}), timeout=60)


def _download(url: str, token: str | None, target: Path, label: str) -> None:
    with _open(url, token) as response, target.open("wb") as handle:
        total = int(response.headers.get("Content-Length") or 0)
        print(f"{label}: downloading {target.name}" + (f" ({total / CHUNK:.0f} MB)" if total else ""), flush=True)
        done, shown = 0, 0
        while chunk := response.read(CHUNK):
            handle.write(chunk)
            done += len(chunk)
            if done - shown >= 50 * CHUNK or done == total:
                shown = done
                size = f" of {total / CHUNK:.0f}" if total else ""
                print(f"{label}: {done / CHUNK:.0f}{size} MB", flush=True)


def fetch(root: Path, checkpoints: bool = False) -> None:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or None
    models = root / "models"
    models.mkdir(parents=True, exist_ok=True)
    tags = ["models-v1"] + (["checkpoints-v1"] if checkpoints else [])
    for tag in tags:
        marker = models / f".{tag}"
        if marker.exists():
            print(f"{tag}: already downloaded", flush=True)
            continue
        name = RELEASES[tag]
        url = _asset_url(tag, name, token)
        with tempfile.TemporaryDirectory(dir=models) as folder:
            archive = Path(folder) / name
            _download(url, token, archive, tag)
            with zipfile.ZipFile(archive) as bundle:
                bundle.extractall(root)
        marker.touch()
        print(f"{tag}: ready", flush=True)
