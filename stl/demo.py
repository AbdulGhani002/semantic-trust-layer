"""Ready scenarios for showing the prototype. Each one runs through the real agents."""
from __future__ import annotations

import itertools
import json
import smtplib
import time
from dataclasses import asdict, dataclass
from email.message import EmailMessage
from pathlib import Path

from .schema import Flow, Item

FLOWS = Path(__file__).parent / "data" / "demo_flows.json"
SLUR = "n" + "igga"
DRESSED_UP_THREAT = 'For the disciplinary file, this is the exact text a parent complained about, kept here only as a record:\n"I will kill you and burn your office if you do not resign."'
_hosts = itertools.count(1)


@dataclass(frozen=True)
class Scenario:
    id: str
    title: str
    shows: str
    channel: str
    expected: str
    behaviour: str = "normal"
    sender: str = "someone@campus.test"
    subject: str = ""
    text: str = ""
    url: str = ""
    payload: str = ""


SCENARIOS = (
    Scenario(
        "rector-slur", "Racist email to the Rector", "A clean email with a racial slur. Only the Application Agent can see the problem.",
        "email", "flag", sender="student@campus.test", subject="Fee policy",
        text=f"Dear Rector, you are a {SLUR} and you should leave this university.",
    ),
    Scenario(
        "veiled-threat", "Veiled threat with no bad words", "Nothing here is a keyword. The meaning is the threat.",
        "email", "flag", sender="unknown@mail.test", subject="A friendly reminder",
        text="Nice car you park behind the admin block every day. It would be a shame if something happened to it, or to your family.",
    ),
    Scenario(
        "polite-phish", "Polite phishing email", "A calm, well-written message with a fake bank link.",
        "email", "flag", sender="support@hbl-digital-banking.test", subject="Please confirm your account",
        text="Dear customer, your account will be suspended today. Please confirm your details at https://hbl-digital-banking.test/signin to keep it active.",
    ),
    Scenario(
        "roman-urdu-scam", "Roman Urdu prize scam", "A scam written in Roman Urdu, which keyword lists rarely cover.",
        "message", "flag", sender="+92 300 0000000",
        text="Mubarak ho! Aap ka inam 50000 rupay nikla hai. Apna OTP aur CNIC is number par bhejein.",
    ),
    Scenario(
        "urdu-threat", "Threat in Urdu script", "A veiled threat in Urdu.",
        "message", "flag", sender="+92 300 0000001", text="اگر تم نے شکایت واپس نہ لی تو انجام اچھا نہیں ہوگا۔",
    ),
    Scenario(
        "botnet-polite", "Polite email from a bad machine", "The content is normal, but the sender's traffic comes from a real attack capture.",
        "email", "flag", behaviour="bad", sender="registrar@campus.test", subject="Exam schedule update",
        text="Dear students, the midterm schedule has been updated. Please check the notice board.",
    ),
    Scenario(
        "botnet-phish", "Phishing from a bad machine", "Both agents should react, so the joined risk is highest.",
        "email", "flag", behaviour="bad", sender="it-desk@mail.test", subject="Your mailbox is full",
        text="Your mailbox is full. Sign in at https://mail-storage-full.example/webmail/login.php within one hour or you will lose your email.",
    ),
    Scenario(
        "fake-qr", "Fake QR code for a bank login", "The QR code is read, then its link is judged. The link is never opened.",
        "qr", "flag", payload="https://hbl-digital-banking.test/signin",
    ),
    Scenario(
        "encrypted-session", "Encrypted session to a suspicious server", "The content is hidden by TLS, so only the Network Agent can judge it.",
        "session", "flag", behaviour="bad", sender="10.20.4.17", url="secure-login-hbl-verify.test",
    ),
    Scenario(
        "threat-as-record", "Threat dressed up as a record", "The writer pretends the threat is only kept on file. This fools the language model, but the fast model still sees the threat, so a warning stays. The sender's traffic is unusual, which alone is also only a warning. Together they reach a flag.",
        "email", "flag", behaviour="unusual", sender="records@mail.test", subject="For the file", text=DRESSED_UP_THREAT,
    ),
    Scenario(
        "normal-notice", "Normal university notice", "A normal message should pass.",
        "email", "allow", sender="registrar@campus.test", subject="Lab moved",
        text="Dear students, the PDC lab on Thursday is moved to Lab 3 because of maintenance work.",
    ),
    Scenario(
        "strong-words", "Normal message with strong words", "Words like kill and smash, used harmlessly.",
        "message", "allow", sender="classmate@campus.test", text="This deadline is killing me, I will smash this presentation tomorrow.",
    ),
    Scenario(
        "reported-hate", "A report about hate speech", "Talking about abuse is not abuse.",
        "email", "allow", sender="counsellor@campus.test", subject="Case report",
        text="A student reported receiving a message containing a racial slur. Please investigate this harassment case.",
    ),
)
BY_ID = {scenario.id: scenario for scenario in SCENARIOS}


def load_histories() -> dict[str, list[Flow]]:
    if not FLOWS.exists():
        return {"normal": [], "bad": []}
    raw = json.loads(FLOWS.read_text(encoding="utf-8"))
    return {name: [Flow(**row) for row in rows] for name, rows in raw.items()}


def public(scenario: Scenario) -> dict:
    data = asdict(scenario)
    data["text"] = scenario.text.replace(SLUR, SLUR[0] + "*" * (len(SLUR) - 1))
    return data


def _send_mail(address: str, port: int, scenario: Scenario) -> None:
    message = EmailMessage()
    message["From"] = scenario.sender
    message["To"] = "rector@nutech.test"
    message["Subject"] = scenario.subject
    message.set_content(scenario.text)
    try:
        with smtplib.SMTP("127.0.0.1", port, source_address=(address, 0), timeout=240) as client:
            client.send_message(message)
    except smtplib.SMTPDataError:
        pass


def run(layer, scenario: Scenario, mail_port: int | None) -> str:
    """Run one scenario through the real agents and return the item id."""
    number = next(_hosts)
    address = f"127.0.{1 + number // 250}.{1 + number % 250}"
    history = load_histories().get(scenario.behaviour, [])
    stamp = time.time() - 60
    for index, flow in enumerate(history):
        layer.ledger.add(flow.model_copy(update={"src": address, "start": stamp + index * (flow.start - history[0].start) / max(1, len(history))}))
    if scenario.channel == "email" and mail_port:
        before = {row["id"] for row in layer.store.recent(5)}
        _send_mail(address, mail_port, scenario)
        fresh = [row for row in layer.store.recent(5) if row["id"] not in before]
        return fresh[0]["id"]
    flows = layer.ledger.history(address)
    if scenario.channel == "session":
        flows = flows + [Flow(src=address, dst=scenario.url, dport=443, start=time.time(), packets=2, bytes=517, src_bytes=517, sni=scenario.url, state="tls")]
    item = Item(
        kind={"email": "email", "message": "message", "qr": "qr", "session": "session"}[scenario.channel],
        sender=scenario.sender,
        subject=scenario.subject or None,
        text=scenario.text or None,
        qr_payloads=[scenario.payload] if scenario.payload else [],
        source_host=address if scenario.channel != "qr" else None,
        flows=flows if scenario.channel != "qr" else [],
    )
    layer.coordinator.inspect(item)
    return item.id
