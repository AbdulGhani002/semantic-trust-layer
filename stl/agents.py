"""The two AI agents. Both look at the same item at the same time."""
from __future__ import annotations

import os
import time

from .extract import clean_text, describe_qr, find_urls, looks_english
from .flow_model import FlowModel
from .models import TextModel, UrlModel, risk_from_score
from .reviewer import Reviewer
from .schema import CONTENT_LABELS, Evidence, Finding, Item

REVIEW_GATE = float(os.environ.get("STL_REVIEW_GATE", "0"))
WARN_FLOOR = 0.3
ONE_READER_CAP = 0.84
REVIEW_SURE = 0.9
UNUSUAL_CAP = 0.45
MIN_HISTORY = 8
ESTIMATED_FLOWS = ("established", "tls")


class ApplicationAgent:
    """Reads content and judges what it means."""

    name = "application-agent"
    layer = "application"

    def __init__(self, text: TextModel | None, url: UrlModel | None, reviewer: Reviewer | None, clean: bool = True):
        self.text = text
        self.url = url
        self.reviewer = reviewer
        self.clean = clean

    def content_of(self, item: Item) -> tuple[str, list[str]]:
        tidy = clean_text if self.clean else str
        parts: list[str] = []
        urls = list(item.urls)
        if item.subject:
            parts.append(f"Subject: {tidy(item.subject)}")
        if item.text:
            body = tidy(item.text)
            parts.append(body)
            urls += find_urls(body)
        for payload in item.qr_payloads:
            readable, link = describe_qr(payload)
            if readable:
                parts.append(readable)
            if link:
                urls.append(link)
        return "\n".join(parts).strip(), list(dict.fromkeys(urls))

    def inspect(self, item: Item) -> Finding:
        started = time.time()
        finding = Finding(agent=self.name, layer=self.layer, item_id=item.id)
        text, urls = self.content_of(item)
        if self.text is None and self.url is None:
            finding.available = False
            finding.note = "models are not loaded"
            return finding
        risks: dict[str, float] = {}
        if text and self.text:
            scores = self.text.score(text)
            finding.scores.update(scores)
            risks = {label: risk_from_score(scores[label], self.text.thresholds[label]) for label in CONTENT_LABELS}
            top = max(risks, key=risks.get)
            if risks[top] >= 0.3:
                words = self.text.influential_words(text, top)
                if words:
                    finding.evidence.append(
                        Evidence(
                            source="text model",
                            detail=f"{top}: strongest words are " + ", ".join(word for word, _ in words),
                            weight=round(risks[top], 3),
                        )
                    )
        if urls and self.url:
            link_scores = self.url.score_many(urls)
            worst = int(link_scores.argmax())
            score = float(link_scores[worst])
            finding.scores["link"] = score
            link_risk = risk_from_score(score, self.url.threshold)
            risks["fraud"] = max(risks.get("fraud", 0.0), link_risk)
            if link_risk >= 0.3:
                finding.evidence.append(
                    Evidence(source="link model", detail=f"link looks like phishing: {urls[worst]}", weight=round(link_risk, 3))
                )
        finding.risk = max(risks.values(), default=0.0)
        finding.seconds = round(time.time() - started, 4)
        finding.model = " + ".join(m.version for m in (self.text, self.url) if m)
        return finding

    def needs_review(self, own: Finding, other: Finding | None, text: str = "") -> bool:
        """A bare link reaches the language model only if the link model flagged it, because it invents impersonation on names it does not know."""
        if self.reviewer is None:
            return False
        if not text:
            return own.risk >= 0.5
        if own.risk >= REVIEW_GATE:
            return True
        if text and not looks_english(text):
            return True
        return other is not None and other.risk >= 0.5

    def second_look(self, item: Item, own: Finding, other: Finding | None) -> Finding:
        """Ask the language model to read the content. It judges alone, because it copies any opinion it is given."""
        text, urls = self.content_of(item)
        if not (text or urls) or not self.needs_review(own, other, text):
            return own
        started = time.time()
        message = text if not urls else f"{text}\nLinks: {' '.join(urls[:5])}"
        outcome = self.reviewer.review(message)
        own.seconds = round(own.seconds + time.time() - started, 4)
        if outcome is None:
            own.note = "language model did not answer"
            return own
        own.scores["review_confidence"] = outcome["confidence"]
        if outcome["labels"]:
            reviewed = 0.5 + 0.5 * outcome["confidence"]
            if own.risk >= 0.5:
                own.risk = max(own.risk, reviewed)
            elif outcome["confidence"] >= REVIEW_SURE:
                own.risk = min(reviewed, ONE_READER_CAP)
            else:
                own.risk = max(own.risk, WARN_FLOOR)
            for label in outcome["labels"]:
                own.scores[f"review_{label}"] = outcome["confidence"]
        else:
            floor = WARN_FLOOR if own.risk >= 0.5 else 0.0
            own.risk = max(floor, min(own.risk, 0.5 * (1 - outcome["confidence"])))
        own.evidence.append(Evidence(source="language model", detail=outcome["reason"], weight=outcome["confidence"]))
        own.model += f" + {self.reviewer.model}"
        return own


class NetworkAgent:
    """Reads how data travels and judges its behaviour. It never reads content."""

    name = "network-agent"
    layer = "network"

    def __init__(self, flows: FlowModel | None, url: UrlModel | None):
        self.flows = flows
        self.url = url

    def inspect(self, item: Item) -> Finding:
        started = time.time()
        finding = Finding(agent=self.name, layer=self.layer, item_id=item.id)
        if not item.flows:
            finding.available = False
            finding.note = "no traffic information for this item"
            return finding
        if self.flows is not None:
            known, summary = self.flows.score_flows(item.flows)
            measured = [flow for flow in item.flows if flow.state not in ESTIMATED_FLOWS]
            unusual = self.flows.unusual_flows(measured) if len(measured) >= MIN_HISTORY else 0.0
            finding.scores["behaviour"] = known
            finding.scores["unusual"] = unusual
            finding.risk = max(risk_from_score(known, self.flows.threshold), min(unusual, UNUSUAL_CAP))
            finding.note = summary
            finding.model = self.flows.version
            if finding.risk >= 0.3:
                finding.evidence.append(Evidence(source="traffic model", detail=summary, weight=round(finding.risk, 3)))
        names = [flow.sni or flow.dns_query for flow in item.flows if flow.sni or flow.dns_query]
        if names and self.url:
            scores = self.url.score_many(names)
            worst = int(scores.argmax())
            name_risk = risk_from_score(float(scores[worst]), self.url.threshold)
            finding.scores["server_name"] = float(scores[worst])
            if name_risk > finding.risk:
                finding.risk = name_risk
            if name_risk >= 0.3:
                finding.evidence.append(
                    Evidence(source="server name", detail=f"server name looks suspicious: {names[worst]}", weight=round(name_risk, 3))
                )
        finding.seconds = round(time.time() - started, 4)
        return finding

    def second_look(self, item: Item, own: Finding, other: Finding | None) -> Finding:
        return own
