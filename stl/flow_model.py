"""Network Agent model: judges a host's behaviour from its recent connections.

Input is metadata only: timing, sizes, ports and protocol. No payload is read,
so this keeps working on encrypted traffic.
"""
from __future__ import annotations

import io
import json
import math
import socket
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Iterator

import numpy as np

from .schema import Flow

WINDOW = 32
RECENT = 8
NUMERIC = 9
PROTOS = {"tcp": 0, "udp": 1, "icmp": 2}
PORTS = {
    80: 1, 8080: 1, 8000: 1, 443: 2, 8443: 2, 53: 3, 25: 4, 465: 4, 587: 4, 110: 4, 143: 4, 993: 4, 995: 4,
    22: 5, 21: 6, 20: 6, 23: 7, 3389: 8, 445: 9, 139: 9, 135: 9, 123: 10, 6667: 11, 6666: 11, 6668: 11,
}
PORT_GROUPS = 15
IDLE_SECONDS = 120.0
MODEL_DIR = Path(__file__).resolve().parent.parent / "models" / "flow"


def port_group(port: int) -> int:
    if port in PORTS:
        return PORTS[port]
    if port < 1024:
        return 12
    return 13 if port < 49152 else 14


def encode(flows: list[Flow]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Turn a host's most recent flows into model input, oldest first."""
    recent = flows[-WINDOW:]
    numbers = np.zeros((1, WINDOW, NUMERIC), dtype=np.float32)
    kinds = np.zeros((1, WINDOW, 2), dtype=np.int64)
    mask = np.ones((1, WINDOW), dtype=bool)
    offset = WINDOW - len(recent)
    seen_hosts: set[str] = set()
    seen_ports: set[int] = set()
    last_start = None
    for index, flow in enumerate(recent):
        position = offset + index
        packets = max(flow.packets, 1)
        back = max(flow.bytes - flow.src_bytes, 0)
        gap = 0.0 if last_start is None else max(flow.start - last_start, 0.0)
        numbers[0, position] = (
            math.log1p(max(flow.duration, 0.0)),
            math.log1p(packets),
            math.log1p(max(flow.src_bytes, 0)),
            math.log1p(back),
            math.log1p(max(flow.bytes, 0) / packets),
            flow.src_bytes / max(flow.bytes, 1),
            math.log1p(gap),
            float(flow.dst not in seen_hosts),
            float(flow.dport not in seen_ports),
        )
        kinds[0, position] = (PROTOS.get(flow.proto, 3), port_group(flow.dport))
        mask[0, position] = False
        seen_hosts.add(flow.dst)
        seen_ports.add(flow.dport)
        last_start = flow.start
    return numbers, kinds, mask


def describe(flows: list[Flow]) -> str:
    recent = flows[-WINDOW:]
    hosts = len({f.dst for f in recent})
    common_port, uses = Counter(f.dport for f in recent).most_common(1)[0]
    sizes = np.mean([f.bytes for f in recent])
    return f"{len(recent)} recent connections to {hosts} hosts, port {common_port} used {uses} times, average {sizes:.0f} bytes"


def window_features(numbers: np.ndarray, kinds: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Summarise windows of connections into behaviour numbers for the anomaly model."""
    valid = (~mask).astype(np.float32)[:, :, None]
    count = np.clip(valid.sum(1), 1, None)
    mean = (numbers * valid).sum(1) / count
    spread = np.sqrt((((numbers - mean[:, None, :]) ** 2) * valid).sum(1) / count)
    protos = np.eye(4, dtype=np.float32)[kinds[:, :, 0]]
    ports = np.eye(PORT_GROUPS, dtype=np.float32)[kinds[:, :, 1]]
    return np.concatenate(
        [mean, spread, count / WINDOW, (protos * valid).sum(1) / count, (ports * valid).sum(1) / count, numbers[:, -1, :]],
        axis=1,
    ).astype(np.float32)


class FlowModel:
    def __init__(self, folder: Path = MODEL_DIR):
        from .models import session

        self.session = session(folder / "flow.onnx")
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        self.threshold = float(meta["threshold"])
        self.version = meta.get("name", "flow-transformer")
        self.anomaly = None
        path = folder / "anomaly.joblib"
        if path.exists():
            import joblib

            self.anomaly = joblib.load(path)
            self.anomaly["forest"].n_jobs = 1
            self.version += " + normal-behaviour model"

    def score_many(self, numbers: np.ndarray, kinds: np.ndarray, mask: np.ndarray) -> np.ndarray:
        logits = self.session.run(None, {"numbers": numbers, "kinds": kinds, "mask": mask})[0]
        return (1.0 / (1.0 + np.exp(-logits))).reshape(-1)

    def unusual_many(self, numbers: np.ndarray, kinds: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Return how far each window is from normal behaviour, where the cut-off sits at 0.5."""
        model = self.anomaly
        raw = -model["forest"].score_samples(window_features(numbers, kinds, mask))
        low, cut, high = model["low"], model["cut_off"], model["high"]
        below = 0.5 * np.clip((raw - low) / max(cut - low, 1e-6), 0, 1)
        above = 0.5 + 0.5 * np.clip((raw - cut) / max(high - cut, 1e-6), 0, 1)
        return np.where(raw < cut, below, above)

    def score_flows(self, flows: list[Flow]) -> tuple[float, str]:
        """Score the host's recent connections and keep the worst window."""
        ends = range(max(1, len(flows) - RECENT + 1), len(flows) + 1)
        parts = [encode(flows[:end]) for end in ends]
        numbers, kinds, mask = (np.concatenate(group) for group in zip(*parts))
        return float(self.score_many(numbers, kinds, mask).max()), describe(flows)

    def unusual_flows(self, flows: list[Flow]) -> float:
        if not self.anomaly:
            return 0.0
        return float(self.unusual_many(*encode(flows))[0])


class _Open:
    __slots__ = ("flow", "last")

    def __init__(self, flow: Flow, stamp: float):
        self.flow = flow
        self.last = stamp


def _tls_name(data: bytes) -> str | None:
    from .gateway import client_hello_name

    return client_hello_name(data)


def _dns_name(data: bytes) -> str | None:
    import dpkt

    try:
        message = dpkt.dns.DNS(data)
        return message.qd[0].name if message.qd else None
    except (dpkt.UnpackError, IndexError, ValueError):
        return None


def iter_flows(stream, idle: float = IDLE_SECONDS) -> Iterator[Flow]:
    """Read a pcap stream and yield two-way flows as they finish."""
    import dpkt

    reader = dpkt.pcap.Reader(stream)
    table: dict[tuple, _Open] = {}
    linktype = reader.datalink()
    since_sweep = 0
    for stamp, frame in reader:
        try:
            if linktype == dpkt.pcap.DLT_EN10MB:
                packet = dpkt.ethernet.Ethernet(frame).data
            elif linktype == dpkt.pcap.DLT_RAW or linktype == 101:
                packet = dpkt.ip.IP(frame)
            else:
                packet = dpkt.ethernet.Ethernet(frame).data
        except (dpkt.UnpackError, ValueError):
            continue
        if not isinstance(packet, (dpkt.ip.IP, dpkt.ip6.IP6)):
            continue
        is_v4 = isinstance(packet, dpkt.ip.IP)
        family = socket.AF_INET if is_v4 else socket.AF_INET6
        try:
            src, dst = socket.inet_ntop(family, packet.src), socket.inet_ntop(family, packet.dst)
        except (ValueError, OSError):
            continue
        size = packet.len if is_v4 else packet.plen + 40
        body = packet.data
        sport = getattr(body, "sport", 0) or 0
        dport = getattr(body, "dport", 0) or 0
        proto = "tcp" if isinstance(body, dpkt.tcp.TCP) else "udp" if isinstance(body, dpkt.udp.UDP) else "icmp" if isinstance(body, dpkt.icmp.ICMP) else "other"
        forward = (src, dst, sport, dport, proto)
        reverse = (dst, src, dport, sport, proto)
        key = forward if forward in table else reverse if reverse in table else None
        if key is None:
            key = forward
            table[key] = _Open(Flow(src=src, dst=dst, sport=sport, dport=dport, proto=proto, start=stamp), stamp)
        record = table[key]
        flow = record.flow
        flow.packets += 1
        flow.bytes += size
        if key == forward:
            flow.src_bytes += size
        else:
            flow.dst_packets += 1
        record.last = stamp
        flow.duration = stamp - flow.start
        payload = getattr(body, "data", b"")
        if isinstance(payload, bytes) and payload:
            if dport == 443 and flow.sni is None and proto == "tcp":
                flow.sni = _tls_name(payload)
            elif dport == 53 and flow.dns_query is None:
                flow.dns_query = _dns_name(payload)
        since_sweep += 1
        if since_sweep >= 50_000:
            since_sweep = 0
            for stale in [k for k, r in table.items() if stamp - r.last > idle]:
                yield table.pop(stale).flow
    yield from (record.flow for record in table.values())


def flows_from_pcap(data: bytes) -> dict[str, list[Flow]]:
    by_host: dict[str, list[Flow]] = defaultdict(list)
    for flow in iter_flows(io.BytesIO(data)):
        by_host[flow.src].append(flow)
    for flows in by_host.values():
        flows.sort(key=lambda f: f.start)
    return dict(by_host)


def windows(flows: Iterable[Flow]) -> list[Flow]:
    return sorted(flows, key=lambda f: f.start)
