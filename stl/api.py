"""Web API and dashboard for the Semantic Trust Layer."""
from __future__ import annotations

import asyncio
import csv
import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import demo
from .agents import MIN_HISTORY, UNUSUAL_CAP, ApplicationAgent, NetworkAgent
from .coordinator import Coordinator
from .extract import file_text, find_urls, read_qr
from .flow_model import FlowModel, describe, flows_from_pcap
from .gateway import FlowLedger, WebProxy, start_mail
from .models import MODELS, ROOT, TextModel, UrlModel, risk_from_score
from .reviewer import Reviewer
from .schema import Flow, Item
from .store import VerdictStore

WEB = Path(__file__).parent / "web"
DATA = ROOT / "data"
RESULTS = ROOT / "results"
TEST_CODES = ROOT / "tests" / "fixtures" / "qr"
MAX_UPLOAD = 20_000_000
IMAGE_TYPES = (".png", ".jpg", ".jpeg", ".webp", ".bmp")
MAIL_PORT = 8025
WEB_PROXY_PORT = 8026


class TextCheck(BaseModel):
    text: str = Field(min_length=1, max_length=50_000)
    subject: str | None = None
    sender: str | None = None
    source_host: str | None = None


class LinkCheck(BaseModel):
    url: str = Field(min_length=3, max_length=4_000)


def load(factory, folder: Path):
    if not (folder / "meta.json").exists():
        print(f"{folder.name} model is not trained yet")
        return None
    return factory(folder)


class Layer:
    def __init__(self, database: Path = DATA / "stl.db"):
        self.text = load(TextModel, MODELS / "text")
        self.url = load(UrlModel, MODELS / "url")
        self.flows = load(FlowModel, MODELS / "flow")
        reviewer = Reviewer()
        self.reviewer = reviewer if reviewer.available() else None
        self.application = ApplicationAgent(self.text, self.url, self.reviewer)
        self.network = NetworkAgent(self.flows, self.url)
        self.store = VerdictStore(database)
        self.coordinator = Coordinator(self.application, self.network, self.store, DATA / "keys")
        self.ledger = FlowLedger()
        self.mail_running = False
        self.proxy_running = False

    def health(self) -> dict:
        return {
            "text_model": self.text.version if self.text else None,
            "url_model": self.url.version if self.url else None,
            "flow_model": self.flows.version if self.flows else None,
            "language_model": self.reviewer.model if self.reviewer else None,
            "smtp_gateway": MAIL_PORT if self.mail_running else None,
            "http_proxy": WEB_PROXY_PORT if self.proxy_running else None,
            "counts": self.store.counts(),
        }

    def agents(self) -> list[dict]:
        keys = self.coordinator.signers
        rows = [
            {
                "name": "Application Agent",
                "layer": "Application",
                "reads": "Message text, links, QR codes and file text",
                "models": [m for m in (self.text and self.text.version, self.url and self.url.version, self.reviewer and self.reviewer.model) if m],
                "cut_offs": {**(self.text.thresholds if self.text else {}), **({"link": self.url.threshold} if self.url else {})},
                "key": keys["application-agent"].public_key.hex()[:16],
            },
            {
                "name": "Network Agent",
                "layer": "Network",
                "reads": "Connection timing, sizes, ports, and DNS and TLS names. Never content.",
                "models": [m for m in (self.flows and self.flows.version, self.url and self.url.version) if m],
                "cut_offs": {"behaviour": self.flows.threshold} if self.flows else {},
                "key": keys["network-agent"].public_key.hex()[:16],
            },
            {
                "name": "Coordinator",
                "layer": "Both",
                "reads": "The two agents' findings",
                "models": [],
                "cut_offs": {"warn": 0.3, "flag": 0.5, "block": 0.85},
                "key": keys["coordinator"].public_key.hex()[:16],
            },
        ]
        return rows

    def hosts(self) -> list[dict]:
        rows = []
        for host, flows in list(self.ledger.hosts.items())[:200]:
            history = list(flows)
            if not history:
                continue
            risk = None
            if self.flows:
                known, _ = self.flows.score_flows(history)
                unusual = self.flows.unusual_flows(history) if len(history) >= MIN_HISTORY else 0.0
                risk = round(max(risk_from_score(known, self.flows.threshold), min(unusual, UNUSUAL_CAP)), 3)
            rows.append(
                {
                    "host": host,
                    "connections": len(history),
                    "last_seen": max(f.start for f in history),
                    "summary": describe(history),
                    "risk": risk,
                }
            )
        rows.sort(key=lambda row: -(row["risk"] or 0))
        return rows


def read_results() -> dict:
    found = {}
    for path in RESULTS.glob("*.json"):
        try:
            found[path.stem] = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            continue
    return found


def test_codes() -> list[dict]:
    manifest = TEST_CODES / "manifest.csv"
    if not manifest.exists():
        return []
    with manifest.open(encoding="utf-8") as handle:
        return [row for row in csv.DictReader(handle) if row["variant"] in ("clean", "sticker", "blurred")]


def create_app(start_gateways: bool = False) -> FastAPI:
    layer = Layer()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        mail, proxy = None, None
        if start_gateways:
            mail = start_mail(layer.coordinator, layer.ledger, DATA / "mailbox", MAIL_PORT)
            proxy = WebProxy(layer.coordinator, layer.ledger, WEB_PROXY_PORT)
            await proxy.start()
            layer.mail_running = layer.proxy_running = True
        yield
        if mail:
            mail.stop()
        if proxy:
            await proxy.stop()

    app = FastAPI(title="Semantic Trust Layer", version="0.1.0", lifespan=lifespan)
    app.state.layer = layer

    @app.middleware("http")
    async def always_fresh(request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache"
        return response

    async def in_thread(function, *args):
        return await asyncio.get_running_loop().run_in_executor(None, function, *args)

    async def run(item: Item):
        return await in_thread(layer.coordinator.inspect, item)

    def history(host: str | None) -> list[Flow]:
        return layer.ledger.history(host) if host else []

    @app.get("/api/health")
    def health():
        return layer.health()

    @app.get("/api/stats")
    def stats():
        return layer.store.stats()

    @app.get("/api/agents")
    def agents():
        return layer.agents()

    @app.get("/api/hosts")
    def hosts():
        return layer.hosts()

    @app.get("/api/results")
    def results():
        return read_results()

    @app.get("/api/scenarios")
    def scenarios():
        return [demo.public(item) for item in demo.SCENARIOS]

    @app.post("/api/scenarios/{scenario_id}/run")
    async def run_scenario(scenario_id: str):
        scenario = demo.BY_ID.get(scenario_id)
        if scenario is None:
            raise HTTPException(404, "No such scenario")
        port = MAIL_PORT if layer.mail_running else None
        return {"id": await in_thread(demo.run, layer, scenario, port)}

    @app.get("/api/testcodes")
    def codes():
        return test_codes()

    @app.post("/api/testcodes/{name}/check")
    async def check_code(name: str):
        path = TEST_CODES / Path(name).name
        if not path.is_file() or path.suffix != ".png":
            raise HTTPException(404, "No such test code")
        payloads = await in_thread(read_qr, path.read_bytes())
        if not payloads:
            raise HTTPException(422, "The QR code could not be read")
        item = Item(kind="qr", file_name=name, qr_payloads=payloads)
        await run(item)
        return {"id": item.id, "qr": payloads}

    @app.post("/api/check/text")
    async def check_text(body: TextCheck):
        item = Item(
            kind="message",
            text=body.text,
            subject=body.subject,
            sender=body.sender,
            source_host=body.source_host,
            urls=find_urls(body.text),
            flows=history(body.source_host),
        )
        await run(item)
        return {"id": item.id}

    @app.post("/api/check/link")
    async def check_link(body: LinkCheck):
        item = Item(kind="link", urls=[body.url])
        await run(item)
        return {"id": item.id}

    @app.post("/api/check/file")
    async def check_file(file: UploadFile):
        data = await file.read()
        if len(data) > MAX_UPLOAD:
            raise HTTPException(413, "File is too large")
        name = file.filename or "upload"
        if name.lower().endswith(IMAGE_TYPES):
            payloads = await in_thread(read_qr, data)
            if not payloads:
                raise HTTPException(422, "No QR code found in this image")
            item = Item(kind="qr", file_name=name, qr_payloads=payloads)
        else:
            text = file_text(name, data)
            if not text.strip():
                raise HTTPException(422, "No readable text in this file")
            item = Item(kind="file", file_name=name, text=text, urls=find_urls(text))
        await run(item)
        return {"id": item.id}

    @app.post("/api/check/pcap")
    async def check_pcap(file: UploadFile):
        data = await file.read()
        if len(data) > MAX_UPLOAD * 5:
            raise HTTPException(413, "Capture is too large")
        try:
            by_host = await in_thread(flows_from_pcap, data)
        except ValueError as error:
            raise HTTPException(422, f"Could not read this capture: {error}")
        checked = 0
        for host, flows in list(by_host.items())[:50]:
            for flow in flows[-32:]:
                layer.ledger.add(flow)
            await run(Item(kind="session", source_host=host, flows=flows[-32:]))
            checked += 1
        return {"hosts": len(by_host), "checked": checked}

    @app.get("/api/verdicts")
    def verdicts(limit: int = 100, action: str | None = None, found_by: str | None = None, kind: str | None = None):
        return layer.store.recent(min(limit, 500), action or None, found_by or None, kind or None)

    @app.delete("/api/verdicts")
    def clear_verdicts():
        layer.store.clear()
        return {"cleared": True}

    @app.get("/api/verdicts/{item_id}")
    def verdict(item_id: str):
        record = layer.store.one(item_id)
        if record is None:
            raise HTTPException(404, "No such item")
        record["signature_valid"] = layer.coordinator.verify(record["envelope"])
        return record

    @app.get("/")
    def index():
        return FileResponse(WEB / "index.html", headers={"Cache-Control": "no-cache"})

    if TEST_CODES.is_dir():
        app.mount("/testcodes", StaticFiles(directory=TEST_CODES), name="testcodes")
    app.mount("/static", StaticFiles(directory=WEB), name="static")
    return app
