"""Shared records for the Semantic Trust Layer."""
from __future__ import annotations

import time
import uuid
from typing import Literal

from pydantic import BaseModel, Field

CONTENT_LABELS = ("threat", "hate", "abuse", "fraud")
BEHAVIOUR_LABELS = ("malicious_behaviour",)
Action = Literal["allow", "warn", "flag", "block"]
Kind = Literal["email", "message", "link", "qr", "file", "session"]


class Flow(BaseModel):
    src: str
    dst: str
    sport: int = 0
    dport: int = 0
    proto: str = "tcp"
    start: float = 0.0
    duration: float = 0.0
    packets: int = 0
    bytes: int = 0
    src_bytes: int = 0
    dst_packets: int = 0
    state: str = ""
    sni: str | None = None
    dns_query: str | None = None


class Item(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    kind: Kind
    received: float = Field(default_factory=time.time)
    sender: str | None = None
    recipient: str | None = None
    subject: str | None = None
    text: str | None = None
    urls: list[str] = Field(default_factory=list)
    qr_payloads: list[str] = Field(default_factory=list)
    file_name: str | None = None
    source_host: str | None = None
    flows: list[Flow] = Field(default_factory=list)


class Evidence(BaseModel):
    source: str
    detail: str
    weight: float = 0.0


class Finding(BaseModel):
    agent: str
    layer: Literal["application", "network"]
    item_id: str
    scores: dict[str, float] = Field(default_factory=dict)
    risk: float = 0.0
    evidence: list[Evidence] = Field(default_factory=list)
    model: str = ""
    seconds: float = 0.0
    available: bool = True
    note: str = ""


class Verdict(BaseModel):
    item_id: str
    action: Action
    risk: float
    labels: list[str] = Field(default_factory=list)
    reason: str = ""
    findings: list[Finding] = Field(default_factory=list)
    flagged_by: list[str] = Field(default_factory=list)
    decided_at: float = Field(default_factory=time.time)
    seconds: float = 0.0
