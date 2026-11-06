"""Runs both agents at the same time and joins their findings into one verdict."""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .agents import ApplicationAgent, NetworkAgent
from .schema import Finding, Item, Verdict
from .signing import Signer, TrustRegistry
from .store import VerdictStore

ACTIONS = ((0.85, "block"), (0.5, "flag"), (0.3, "warn"))
LABEL_WORDS = {
    "threat": "a threat",
    "hate": "hate speech",
    "abuse": "abusive language",
    "fraud": "fraud or phishing",
    "link": "a dangerous link",
    "behaviour": "suspicious network behaviour",
    "server_name": "a suspicious server name",
}


def join_risk(application: Finding | None, network: Finding | None) -> float:
    """Treat the agents as two independent witnesses."""
    safe = 1.0
    for finding in (application, network):
        if finding is not None and finding.available:
            safe *= 1.0 - finding.risk
    return 1.0 - safe


def action_for(risk: float) -> str:
    for limit, action in ACTIONS:
        if risk >= limit:
            return action
    return "allow"


class Coordinator:
    def __init__(self, application: ApplicationAgent, network: NetworkAgent, store: VerdictStore, key_dir: Path):
        self.application = application
        self.network = network
        self.store = store
        self.pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="stl-agent")
        self.registry = TrustRegistry()
        self.signers = {name: Signer(name, key_dir) for name in (application.name, network.name, "coordinator")}
        for name, signer in self.signers.items():
            self.registry.add(name, signer.public_key)

    def _signed(self, finding: Finding) -> dict:
        return self.signers[finding.agent].sign(finding.model_dump(mode="json"))

    def _labels(self, application: Finding, network: Finding) -> list[str]:
        labels = []
        model = self.application.text
        link_model = self.application.url
        reviewed = "review_confidence" in application.scores
        for label in ("threat", "hate", "abuse", "fraud"):
            if reviewed:
                if f"review_{label}" in application.scores:
                    labels.append(label)
            elif model and application.scores.get(label, 0.0) >= model.thresholds[label]:
                labels.append(label)
        if link_model and application.scores.get("link", 0.0) >= link_model.threshold and (not reviewed or labels):
            labels.append("link")
        flow_model = self.network.flows
        if flow_model and network.scores.get("behaviour", 0.0) >= flow_model.threshold:
            labels.append("behaviour")
        if link_model and network.scores.get("server_name", 0.0) >= link_model.threshold:
            labels.append("server_name")
        return labels

    @staticmethod
    def _reason(labels: list[str], application: Finding, network: Finding, action: str) -> str:
        written = [e.detail for e in application.evidence if e.source == "language model"]
        content_problem = application.available and application.risk >= 0.5
        if written and content_problem:
            return written[-1]
        if network.available and network.risk >= 0.5 and not content_problem:
            detail = network.evidence[0].detail if network.evidence else network.note
            return f"The content looks normal, but the network behaviour is suspicious: {detail}."
        if action in ("flag", "block"):
            return "Neither agent flagged this alone, but the content and the traffic both show signs of a problem."
        unsure = any(key.startswith("review_") and key != "review_confidence" for key in application.scores)
        if written and unsure and action != "allow":
            return f"The language model saw a possible problem but is not sure: {written[-1]}"
        if written and action != "allow":
            return f"The first check raised a concern, but the language model disagreed: {written[-1]}"
        if not labels:
            return "Neither agent found a problem." if action == "allow" else "Both agents see weak signs of a problem."
        words = [LABEL_WORDS[label] for label in labels]
        return "Found " + (words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]) + "."

    def inspect(self, item: Item) -> tuple[Verdict, dict]:
        started = time.time()
        first_app = self.pool.submit(self.application.inspect, item)
        first_net = self.pool.submit(self.network.inspect, item)
        application, network = first_app.result(), first_net.result()
        second_app = self.pool.submit(self.application.second_look, item, application, network)
        second_net = self.pool.submit(self.network.second_look, item, network, application)
        application, network = second_app.result(), second_net.result()

        risk = join_risk(application, network)
        action = action_for(risk)
        labels = self._labels(application, network)
        flagged_by = [f.agent for f in (application, network) if f.available and f.risk >= 0.5]
        verdict = Verdict(
            item_id=item.id,
            action=action,
            risk=round(risk, 4),
            labels=labels,
            reason=self._reason(labels, application, network, action),
            findings=[application, network],
            flagged_by=flagged_by,
            seconds=round(time.time() - started, 4),
        )
        envelope = self.signers["coordinator"].sign(
            {"verdict": verdict.model_dump(mode="json"), "findings": [self._signed(application), self._signed(network)]}
        )
        self.store.save(item, verdict, envelope)
        return verdict, envelope

    def verify(self, envelope: dict) -> bool:
        if not self.registry.verify(envelope):
            return False
        return all(self.registry.verify(part) for part in envelope["payload"]["findings"])
