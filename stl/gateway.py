"""Test gateway: real SMTP and HTTP sessions pass through the trust layer.

The SMTP side accepts mail, checks it and files it in a local mailbox folder.
The HTTP side is a forward proxy. Plain HTTP can be read by both agents. HTTPS
stays encrypted, so only the Network Agent can judge it, from its metadata.
"""
from __future__ import annotations

import asyncio
import json
import time
from collections import defaultdict, deque
from email import message_from_bytes, policy
from pathlib import Path
from urllib.parse import urlsplit

from aiosmtpd.controller import Controller

from .coordinator import Coordinator
from .extract import file_text, html_to_text, parse_email
from .schema import Flow, Item

HISTORY = 32
MAX_BODY = 1_000_000


class FlowLedger:
    """Remembers each host's recent connections for the Network Agent."""

    def __init__(self):
        self.hosts: dict[str, deque[Flow]] = defaultdict(lambda: deque(maxlen=HISTORY))

    def add(self, flow: Flow) -> None:
        self.hosts[flow.src].append(flow)

    def history(self, host: str) -> list[Flow]:
        return list(self.hosts[host])


class MailHandler:
    def __init__(self, coordinator: Coordinator, ledger: FlowLedger, mailbox: Path, port: int):
        self.coordinator = coordinator
        self.ledger = ledger
        self.mailbox = mailbox
        self.port = port
        mailbox.mkdir(parents=True, exist_ok=True)

    async def handle_CONNECT(self, server, session, envelope, hostname, port):
        session.stl_started = time.time()
        session.stl_sent = 0
        return f"220 {hostname} ready"

    async def handle_DATA(self, server, session, envelope):
        raw = envelope.original_content or envelope.content
        host, sport = session.peer[0], session.peer[1]
        started = getattr(session, "stl_started", time.time())
        flow = Flow(
            src=host,
            dst="127.0.0.1",
            sport=sport,
            dport=self.port,
            proto="tcp",
            start=started,
            duration=max(time.time() - started, 0.001),
            packets=max(8, len(raw) // 1400 + 8),
            bytes=len(raw) + 600,
            src_bytes=len(raw) + 200,
            dst_packets=4,
            state="established",
        )
        self.ledger.add(flow)
        parsed = parse_email(raw)
        texts = [parsed.body] + [file_text(name, data) for name, data in parsed.attachments]
        item = Item(
            kind="email",
            sender=parsed.sender or envelope.mail_from,
            recipient=parsed.recipient or ",".join(envelope.rcpt_tos),
            subject=parsed.subject,
            text="\n".join(part for part in texts if part),
            urls=parsed.urls,
            source_host=host,
            flows=self.ledger.history(host),
        )
        verdict, _ = await asyncio.get_running_loop().run_in_executor(None, self.coordinator.inspect, item)
        if verdict.action == "block":
            return "550 5.7.1 Message blocked by the Semantic Trust Layer"
        message = message_from_bytes(raw, policy=policy.default)
        message["X-STL-Verdict"] = f"{verdict.action}; risk={verdict.risk}; id={item.id}"
        (self.mailbox / f"{item.id}.eml").write_bytes(bytes(message))
        return "250 Message accepted"


def start_mail(coordinator: Coordinator, ledger: FlowLedger, mailbox: Path, port: int = 8025) -> Controller:
    controller = Controller(MailHandler(coordinator, ledger, mailbox, port), hostname="127.0.0.1", port=port)
    controller.start()
    return controller


def client_hello_name(data: bytes) -> str | None:
    """Read the server name from a TLS ClientHello. The message is not encrypted."""
    try:
        if len(data) < 44 or data[0] != 22:
            return None
        position = 43
        position += 1 + data[position]
        position += 2 + int.from_bytes(data[position : position + 2], "big")
        position += 1 + data[position]
        end = position + 2 + int.from_bytes(data[position : position + 2], "big")
        position += 2
        while position + 4 <= end:
            kind = int.from_bytes(data[position : position + 2], "big")
            size = int.from_bytes(data[position + 2 : position + 4], "big")
            if kind == 0:
                length = int.from_bytes(data[position + 7 : position + 9], "big")
                return data[position + 9 : position + 9 + length].decode("ascii", "ignore")
            position += 4 + size
    except (IndexError, ValueError):
        return None
    return None


class WebProxy:
    def __init__(self, coordinator: Coordinator, ledger: FlowLedger, port: int = 8026):
        self.coordinator = coordinator
        self.ledger = ledger
        self.port = port
        self.server: asyncio.AbstractServer | None = None

    async def start(self) -> None:
        self.server = await asyncio.start_server(self.handle, "127.0.0.1", self.port)

    async def stop(self) -> None:
        if self.server:
            self.server.close()
            await self.server.wait_closed()

    async def inspect(self, item: Item):
        return await asyncio.get_running_loop().run_in_executor(None, self.coordinator.inspect, item)

    async def handle(self, reader, writer):
        host = writer.get_extra_info("peername")[0]
        started = time.time()
        try:
            header = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), 15)
            first = header.split(b"\r\n", 1)[0].decode("latin-1").split()
            if len(first) < 3:
                return
            if first[0].upper() == "CONNECT":
                await self.tunnel(first[1], reader, writer, host, started)
            else:
                await self.plain(first[0], first[1], header, reader, writer, host, started)
        except (asyncio.IncompleteReadError, asyncio.TimeoutError, ConnectionError, OSError):
            pass
        finally:
            writer.close()

    async def tunnel(self, target, reader, writer, host, started):
        name, _, port = target.partition(":")
        upstream_reader, upstream_writer = await asyncio.open_connection(name, int(port or 443))
        writer.write(b"HTTP/1.1 200 Connection established\r\n\r\n")
        await writer.drain()
        hello = await asyncio.wait_for(reader.read(4096), 15)
        server_name = client_hello_name(hello)
        flow = Flow(src=host, dst=name, dport=int(port or 443), proto="tcp", start=started, packets=2, bytes=len(hello), src_bytes=len(hello), sni=server_name or name, state="tls")
        self.ledger.add(flow)
        item = Item(kind="session", source_host=host, text=None, flows=self.ledger.history(host))
        verdict, _ = await self.inspect(item)
        if verdict.action == "block":
            upstream_writer.close()
            return
        upstream_writer.write(hello)
        await upstream_writer.drain()

        async def pipe(source, sink):
            while data := await source.read(65536):
                sink.write(data)
                await sink.drain()

        await asyncio.gather(pipe(reader, upstream_writer), pipe(upstream_reader, writer), return_exceptions=True)
        upstream_writer.close()

    async def plain(self, method, url, header, reader, writer, host, started):
        parts = urlsplit(url)
        upstream_reader, upstream_writer = await asyncio.open_connection(parts.hostname, parts.port or 80)
        path = parts.path or "/"
        if parts.query:
            path += "?" + parts.query
        lines = header.split(b"\r\n")
        lines[0] = f"{method} {path} HTTP/1.0".encode("latin-1")
        kept = [line for line in lines if not line.lower().startswith((b"proxy-", b"connection:"))]
        upstream_writer.write(b"\r\n".join(kept))
        await upstream_writer.drain()
        response = await asyncio.wait_for(upstream_reader.read(MAX_BODY), 20)
        while len(response) < MAX_BODY and (more := await asyncio.wait_for(upstream_reader.read(65536), 20)):
            response += more
        upstream_writer.close()
        head, _, body = response.partition(b"\r\n\r\n")
        text = ""
        if b"text/" in head.lower():
            text = html_to_text(body.decode("utf-8", "ignore"))[0]
        flow = Flow(
            src=host, dst=parts.hostname or "", dport=parts.port or 80, proto="tcp", start=started,
            duration=max(time.time() - started, 0.001), packets=max(6, len(response) // 1400 + 6),
            bytes=len(response) + len(header), src_bytes=len(header), dst_packets=max(3, len(response) // 1400 + 3), state="established",
        )
        self.ledger.add(flow)
        item = Item(kind="session", source_host=host, text=text or None, urls=[url], flows=self.ledger.history(host))
        verdict, _ = await self.inspect(item)
        if verdict.action == "block":
            page = json.dumps({"blocked": True, "reason": verdict.reason, "id": item.id}).encode()
            writer.write(b"HTTP/1.0 403 Forbidden\r\nContent-Type: application/json\r\n\r\n" + page)
        else:
            writer.write(response)
        await writer.drain()
