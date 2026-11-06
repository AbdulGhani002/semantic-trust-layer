import csv
import ipaddress
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from stl.agents import ApplicationAgent, NetworkAgent
from stl.coordinator import Coordinator, action_for, join_risk
from stl.extract import clean_text, describe_qr, find_urls, looks_english, parse_email
from stl.gateway import client_hello_name
from stl.models import risk_from_score
from stl.schema import Evidence, Finding, Flow, Item
from stl.signing import Signer, TrustRegistry
from stl.store import VerdictStore

FIXTURES = Path(__file__).parent / "fixtures"
RESERVED = (".test", ".invalid", ".example")
DOC_NETS = [ipaddress.ip_network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")]


def finding(agent, layer, risk, item_id="x"):
    return Finding(agent=agent, layer=layer, item_id=item_id, risk=risk)


class FakeApp:
    name = "application-agent"
    layer = "application"
    text = None
    url = None

    def __init__(self, risk):
        self.risk = risk
        self.saw_network = None

    def inspect(self, item):
        return finding(self.name, self.layer, self.risk, item.id)

    def second_look(self, item, own, other):
        self.saw_network = other
        return own


class FakeNet(FakeApp):
    name = "network-agent"
    layer = "network"
    flows = None


@pytest.fixture
def coordinator(tmp_path):
    def build(app_risk, net_risk):
        return Coordinator(FakeApp(app_risk), FakeNet(net_risk), VerdictStore(tmp_path / "v.db"), tmp_path / "keys")

    return build


def test_risk_mapping_puts_the_threshold_at_one_half():
    assert risk_from_score(0.2, 0.2) == pytest.approx(0.5)
    assert risk_from_score(0.0, 0.2) == 0.0
    assert risk_from_score(1.0, 0.2) == pytest.approx(1.0)
    assert risk_from_score(0.1, 0.2) == pytest.approx(0.25)


def test_two_weak_witnesses_add_up():
    application, network = finding("a", "application", 0.4), finding("n", "network", 0.4)
    assert join_risk(application, network) == pytest.approx(0.64)
    assert action_for(0.4) == "warn"
    assert action_for(join_risk(application, network)) == "flag"


def test_missing_agent_does_not_change_the_risk():
    application = finding("a", "application", 0.4)
    network = finding("n", "network", 0.9)
    network.available = False
    assert join_risk(application, network) == pytest.approx(0.4)


@pytest.mark.parametrize(
    "app_risk, net_risk, action, flagged_by",
    [
        (0.0, 0.0, "allow", []),
        (0.9, 0.0, "block", ["application-agent"]),
        (0.0, 0.6, "flag", ["network-agent"]),
        (0.4, 0.4, "flag", []),
    ],
)
def test_coordinator_joins_both_agents(coordinator, app_risk, net_risk, action, flagged_by):
    verdict, envelope = coordinator(app_risk, net_risk).inspect(Item(kind="message", text="hello"))
    assert verdict.action == action
    assert verdict.flagged_by == flagged_by
    assert envelope["signer"] == "coordinator"


def test_agents_share_findings(coordinator):
    built = coordinator(0.1, 0.7)
    built.inspect(Item(kind="message", text="hello"))
    assert built.application.saw_network.risk == 0.7


def test_verdicts_are_signed_and_tampering_is_caught(coordinator):
    built = coordinator(0.9, 0.0)
    _, envelope = built.inspect(Item(kind="message", text="hello"))
    assert built.verify(envelope)
    envelope["payload"]["verdict"]["action"] = "allow"
    assert not built.verify(envelope)


def test_unknown_signer_is_rejected(tmp_path):
    registry = TrustRegistry()
    signed = Signer("stranger", tmp_path).sign({"a": 1})
    assert not registry.verify(signed)
    registry.add("stranger", Signer("stranger", tmp_path).public_key)
    assert registry.verify(signed)


def test_store_round_trip(coordinator):
    built = coordinator(0.9, 0.0)
    item = Item(kind="message", text="hello", sender="a@b.test")
    built.inspect(item)
    assert built.store.recent()[0]["action"] == "block"
    assert built.store.one(item.id)["item"]["sender"] == "a@b.test"
    assert built.store.counts() == {"block": 1}
    assert built.store.one("missing") is None


class FakeFlows:
    threshold = 0.5
    version = "fake"

    def __init__(self, known, unusual):
        self.known = known
        self.unusual = unusual

    def score_flows(self, flows):
        return self.known, "summary"

    def unusual_flows(self, flows):
        return self.unusual


@pytest.mark.parametrize(
    "known, unusual, state, count, risk",
    [
        (0.9, 0.0, "", 10, 0.9),
        (0.1, 0.9, "", 10, 0.45),
        (0.1, 0.9, "", 3, 0.1),
        (0.1, 0.9, "established", 10, 0.1),
    ],
)
def test_network_agent_keeps_unusual_behaviour_below_a_flag(known, unusual, state, count, risk):
    flows = [Flow(src="a", dst="b", state=state)] * count
    found = NetworkAgent(FakeFlows(known, unusual), None).inspect(Item(kind="session", flows=flows))
    assert found.risk == pytest.approx(risk)


def test_network_agent_never_sees_content():
    agent = NetworkAgent(None, None)
    found = agent.inspect(Item(kind="message", text="secret"))
    assert found.available is False
    assert "secret" not in found.model_dump_json()


class FakeReviewer:
    model = "fake"

    def __init__(self, labels, confidence=0.95):
        self.labels = labels
        self.confidence = confidence

    def review(self, text, context=""):
        return {"labels": self.labels, "confidence": self.confidence, "reason": "because"}


@pytest.mark.parametrize(
    "start, labels, low, high",
    [
        (0.6, [], 0.3, 0.3),
        (0.3, [], 0.0, 0.03),
        (0.3, ["fraud"], 0.84, 0.84),
        (0.6, ["fraud"], 0.97, 0.98),
    ],
)
def test_language_model_cannot_silently_clear_a_flagged_item(start, labels, low, high):
    agent = ApplicationAgent(None, None, FakeReviewer(labels))
    own = finding(agent.name, agent.layer, start)
    result = agent.second_look(Item(kind="message", text="pay now"), own, None)
    assert low <= result.risk <= high


def test_one_reader_alone_can_flag_but_not_block():
    agent = ApplicationAgent(None, None, FakeReviewer(["threat"]))
    own = finding(agent.name, agent.layer, 0.01)
    result = agent.second_look(Item(kind="message", text="nice car you have there"), own, None)
    assert action_for(result.risk) == "flag"


def test_an_unsure_reader_alone_only_warns():
    agent = ApplicationAgent(None, None, FakeReviewer(["hate"], confidence=0.85))
    own = finding(agent.name, agent.layer, 0.02)
    result = agent.second_look(Item(kind="message", text="your lot again"), own, None)
    assert action_for(result.risk) == "warn"


def test_an_unsure_reader_who_agrees_with_the_fast_model_still_flags():
    agent = ApplicationAgent(None, None, FakeReviewer(["hate"], confidence=0.85))
    own = finding(agent.name, agent.layer, 0.6)
    result = agent.second_look(Item(kind="message", text="your lot again"), own, None)
    assert action_for(result.risk) == "block"


def test_language_model_cannot_raise_a_bare_link_alone():
    agent = ApplicationAgent(None, None, FakeReviewer(["fraud"]))
    own = finding(agent.name, agent.layer, 0.1)
    result = agent.second_look(Item(kind="message", urls=["http://small-shop.test/"]), own, None)
    assert result.risk == pytest.approx(0.1)
    assert "review_confidence" not in result.scores


def test_language_model_can_lower_a_flagged_bare_link_to_a_warning():
    agent = ApplicationAgent(None, None, FakeReviewer([]))
    own = finding(agent.name, agent.layer, 0.7)
    result = agent.second_look(Item(kind="message", urls=["http://bank.test/"]), own, None)
    assert action_for(result.risk) == "warn"


def test_both_readers_agreeing_on_a_bare_link_can_block():
    agent = ApplicationAgent(None, None, FakeReviewer(["fraud"]))
    own = finding(agent.name, agent.layer, 0.7)
    result = agent.second_look(Item(kind="message", urls=["http://bank.test/"]), own, None)
    assert action_for(result.risk) == "block"


def test_language_model_judges_alone():
    seen = {}

    class Listening(FakeReviewer):
        def review(self, text, context=""):
            seen["context"] = context
            return super().review(text, context)

    agent = ApplicationAgent(None, None, Listening([]))
    other = finding("network-agent", "network", 0.99)
    agent.second_look(Item(kind="message", text="hello"), finding(agent.name, agent.layer, 0.1), other)
    assert seen["context"] == ""


@pytest.mark.parametrize(
    "text, english",
    [
        ("Please send the report to the office before you leave for the day.", True),
        ("Aap ka inam 50000 rupay nikla hai. Apna OTP aur CNIC is number par bhejein.", False),
        ("\u0627\u06af\u0631 \u062a\u0645 \u0646\u06d2 \u0634\u06a9\u0627\u06cc\u062a \u0648\u0627\u067e\u0633 \u0646\u06c1 \u0644\u06cc", False),
    ],
)
def test_text_is_routed_by_language(text, english):
    assert looks_english(text) is english


def test_language_model_labels_replace_the_fast_labels(coordinator):
    built = coordinator(0.9, 0.0)
    application = finding("application-agent", "application", 0.9)
    application.scores = {"fraud": 0.99, "review_confidence": 0.9, "review_hate": 0.9}
    network = finding("network-agent", "network", 0.0)
    assert built._labels(application, network) == ["hate"]


def test_application_agent_reads_qr_payloads():
    item = Item(kind="qr", qr_payloads=["https://a.test/x", "WIFI:T:nopass;S:Free_WiFi;;"])
    text, urls = ApplicationAgent(None, None, None).content_of(item)
    assert urls == ["https://a.test/x"]
    assert "Free_WiFi" in text


def test_text_cleaning_undoes_storage_tricks():
    assert clean_text("k\u200bi\u200bl\u200bl") == "kill"
    assert clean_text("p\u0430ssword") == "password"
    assert clean_text("\u043f\u0440\u0438\u0432\u0435\u0442") == "\u043f\u0440\u0438\u0432\u0435\u0442"
    assert clean_text("\u0627\u06af\u0631 \u062a\u0645") == "\u0627\u06af\u0631 \u062a\u0645"


def test_email_parsing_reads_html_and_links():
    raw = (
        b"From: a@b.test\r\nTo: rector@c.test\r\nSubject: Hi\r\nContent-Type: text/html\r\n\r\n"
        b"<p>Open <a href='https://x.test/login'>this</a></p><script>nope()</script>"
    )
    parsed = parse_email(raw)
    assert parsed.subject == "Hi"
    assert "nope" not in parsed.body
    assert parsed.urls == ["https://x.test/login"]


def test_find_urls_trims_punctuation():
    assert find_urls("See https://a.test/x, and www.b.test.") == ["https://a.test/x", "www.b.test"]


@pytest.mark.parametrize(
    "payload, text_part, link",
    [
        ("https://a.test", "", "https://a.test"),
        ("hello there", "hello there", ""),
        ("tel:+920000000000", "Call this number: +920000000000", ""),
    ],
)
def test_qr_payload_types(payload, text_part, link):
    assert describe_qr(payload) == (text_part, link)


def test_payment_and_wifi_qr_become_readable_text():
    assert describe_qr("upi://pay?pa=x@y.test")[0].startswith("Make this payment")
    assert "Free" in describe_qr("WIFI:T:nopass;S:Free;;")[0]


def test_tls_server_name_is_read_from_client_hello():
    name = b"evil.test"
    sni = b"\x00\x00" + (len(name) + 5).to_bytes(2, "big") + (len(name) + 3).to_bytes(2, "big") + b"\x00" + len(name).to_bytes(2, "big") + name
    hello = b"\x16\x03\x01\x00\x00\x01\x00\x00\x00\x03\x03" + bytes(32) + b"\x00" + b"\x00\x02\x13\x01" + b"\x01\x00" + len(sni).to_bytes(2, "big") + sni
    assert client_hello_name(hello) == "evil.test"
    assert client_hello_name(b"GET / HTTP/1.1") is None


def test_flow_record_defaults():
    assert Flow(src="a", dst="b").proto == "tcp"
    assert Evidence(source="s", detail="d").weight == 0.0


def reachable(url: str) -> bool:
    target = url
    if "?q=" in url:
        target = parse_qs(urlsplit(url).query)["q"][0]
    host = (urlsplit(target).hostname or "").lower()
    if host.endswith(RESERVED):
        return False
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return True
    return not any(address in net for net in DOC_NETS)


def test_no_fake_fraud_item_can_reach_a_real_site():
    path = FIXTURES / "links.csv"
    if not path.exists():
        pytest.skip("run training/make_test_fixtures.py first")
    with path.open(encoding="utf-8") as handle:
        fraud = [row["url"] for row in csv.DictReader(handle) if row["label"] == "fraud"]
    assert fraud
    assert not [url for url in fraud if reachable(url)]
