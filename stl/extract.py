"""Turn incoming data into plain content the agents can read.

This only parses formats. It decides nothing about whether content is bad.
"""
from __future__ import annotations

import email
import email.policy
import io
import re
import unicodedata
import zipfile
from dataclasses import dataclass, field
from html.parser import HTMLParser

URL_PATTERN = re.compile(r"(?i)\b((?:https?://|ftp://|www\.)[^\s<>\"')\]]+)")
TEXT_FILES = (".txt", ".csv", ".md", ".log", ".html", ".htm", ".eml", ".json")
LOOKALIKE = str.maketrans(
    "\u0430\u0435\u043e\u0440\u0441\u0443\u0445\u0456\u0455\u0458\u0501\u04bb\u0410\u0415\u041e\u0420\u0421\u0422\u0425\u041d\u041a\u041c\u0412",
    "aeopcyxisjdhAEOPCTXHKMB",
)
COMMON_ENGLISH = frozenset(
    "the and you your for are this that with have from will not please our can all was has to of in on at it be as we by or an if".split()
)


def clean_text(text: str) -> str:
    """Undo tricks that change how text is stored but not how it reads."""
    text = unicodedata.normalize("NFKC", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Cf")

    def fix(match: re.Match) -> str:
        word = match.group()
        return word.translate(LOOKALIKE) if any("a" <= ch.lower() <= "z" for ch in word) else word

    return re.sub(r"\w+", fix, text)


class _HtmlText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.links: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag == "a":
            href = dict(attrs).get("href")
            if href and "://" in href:
                self.links.append(href)

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.parts.append(data.strip())


def html_to_text(markup: str) -> tuple[str, list[str]]:
    parser = _HtmlText()
    parser.feed(markup)
    return " ".join(parser.parts), parser.links


def looks_english(text: str) -> bool:
    """Route text the fast model was not trained for to the language model."""
    letters = [char for char in text if char.isalpha()]
    if not letters or sum(ord(char) > 127 for char in letters) / len(letters) > 0.2:
        return False
    words = re.findall(r"[a-z']+", text.lower())
    return len(words) >= 3 and sum(word in COMMON_ENGLISH for word in words) / len(words) >= 0.15


def find_urls(text: str) -> list[str]:
    seen: dict[str, None] = {}
    for match in URL_PATTERN.findall(text or ""):
        seen.setdefault(match.rstrip(".,;:!?"), None)
    return list(seen)


@dataclass
class ParsedEmail:
    sender: str | None = None
    recipient: str | None = None
    subject: str | None = None
    body: str = ""
    urls: list[str] = field(default_factory=list)
    attachments: list[tuple[str, bytes]] = field(default_factory=list)


def parse_email(raw: bytes) -> ParsedEmail:
    message = email.message_from_bytes(raw, policy=email.policy.default)
    parsed = ParsedEmail(sender=message.get("From"), recipient=message.get("To"), subject=message.get("Subject"))
    links: list[str] = []
    bodies: list[str] = []
    for part in message.walk():
        if part.is_multipart():
            continue
        name = part.get_filename()
        kind = part.get_content_type()
        if name:
            parsed.attachments.append((name, part.get_payload(decode=True) or b""))
        elif kind == "text/plain":
            bodies.append(part.get_content())
        elif kind == "text/html":
            text, found = html_to_text(part.get_content())
            bodies.append(text)
            links += found
    parsed.body = "\n".join(bodies).strip()
    parsed.urls = list(dict.fromkeys(links + find_urls(parsed.body)))
    return parsed


def _docx_text(data: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        markup = archive.read("word/document.xml").decode("utf-8", "ignore")
    return " ".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", markup))


def _pdf_text(data: bytes) -> str:
    import pymupdf

    with pymupdf.open(stream=data, filetype="pdf") as document:
        return "\n".join(page.get_text() for page in document)


def file_text(name: str, data: bytes) -> str:
    lowered = name.lower()
    try:
        if lowered.endswith(".pdf"):
            return _pdf_text(data)
        if lowered.endswith(".docx"):
            return _docx_text(data)
        if lowered.endswith((".html", ".htm")):
            return html_to_text(data.decode("utf-8", "ignore"))[0]
        if lowered.endswith(TEXT_FILES):
            return data.decode("utf-8", "ignore")
    except (ValueError, KeyError, zipfile.BadZipFile, RuntimeError):
        return ""
    return ""


def read_qr(image_bytes: bytes) -> list[str]:
    import zxingcpp
    from PIL import Image

    with Image.open(io.BytesIO(image_bytes)) as image:
        return [code.text for code in zxingcpp.read_barcodes(image.convert("RGB"))]


def describe_qr(payload: str) -> tuple[str, str]:
    """Split a QR payload into text a person would read, and any link inside it."""
    upper = payload[:10].upper()
    if upper.startswith("WIFI:"):
        fields = dict(re.findall(r"([STPH]):((?:\\.|[^;])*);", payload))
        security = fields.get("T", "unknown")
        return f"Join the Wi-Fi network {fields.get('S', '')} (security: {security or 'none'})", ""
    if upper.startswith(("SMSTO:", "SMS:")):
        return "Send this SMS: " + payload.split(":", 2)[-1], ""
    if upper.startswith("TEL:"):
        return "Call this number: " + payload[4:], ""
    if upper.startswith("BEGIN:VCARD"):
        links = find_urls(payload)
        return "Save this contact: " + " ".join(payload.splitlines()[2:-1]), links[0] if links else ""
    if "://" in payload[:12]:
        if payload.lower().startswith(("upi://", "raast://", "pay://")):
            return "Make this payment: " + payload, ""
        return "", payload
    return payload, ""
