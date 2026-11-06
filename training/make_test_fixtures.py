"""Make fake fraudulent links and QR codes for testing STL.

Every fraudulent item points at a reserved name or address that cannot reach
any real website: .test, .invalid and .example (RFC 2606, RFC 6761) or the
documentation IP ranges (RFC 5737). guard() stops the script if one does not.
"""
import csv
import html
import ipaddress
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import segno
import zxingcpp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "fixtures"
QR_DIR = OUT / "qr"
RESERVED_TLDS = (".test", ".invalid", ".example")
DOC_NETS = [ipaddress.ip_network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")]

FRAUD_LINKS = [
    ("lookalike", "https://hbI-online.test/login"),
    ("lookalike", "https://hbl-digital-banking.test/signin"),
    ("lookalike", "https://meezanbank-secure.test/account/verify"),
    ("lookalike", "https://ubl-netbanking.test/otp"),
    ("lookalike", "https://jazzcash-verify.test/wallet/confirm"),
    ("lookalike", "https://easypaisa-rewards.test/claim"),
    ("lookalike", "https://paypaI-security.test/update"),
    ("lookalike", "https://rnicrosoft-login.test/office365/session"),
    ("lookalike", "https://g00gle-accounts.test/recover"),
    ("lookalike", "https://nutech-edu-pk.test/portal/password-reset"),
    ("brand_subdomain", "https://hbl.com.pk.secure-login.test/account"),
    ("brand_subdomain", "https://www.nadra.gov.pk.cnic-update.test/form"),
    ("brand_subdomain", "https://login.microsoftonline.com.tenant-check.test/auth"),
    ("brand_subdomain", "https://paypal.com.resolution-center.test/case/88213"),
    ("brand_subdomain", "https://portal.nutech.edu.pk.mail-quota.test/renew"),
    ("ip_host", "http://192.0.2.44/hbl/login.php"),
    ("ip_host", "http://198.51.100.23:8080/jazzcash/verify.html"),
    ("ip_host", "http://203.0.113.9/office365/signin/index.php"),
    ("ip_host", "http://192.0.2.181/wp-content/uploads/secure/account.html"),
    ("punycode", "https://xn--pypal-4ve.test/signin"),
    ("punycode", "https://xn--hbl-online-9dh.test/login"),
    ("shortener", "https://bit-ly.test/3xY9kQ"),
    ("shortener", "https://tinyurl.test/hbl-kyc"),
    ("shortener", "https://t-co.test/Qz81pL"),
    ("userinfo", "https://www.hbl.com@account-update.test/login"),
    ("userinfo", "https://accounts.google.com:443@session-renew.test/"),
    ("redirect", "https://www.google.com/url?q=https://hbl-login.test/verify"),
    ("apk_download", "http://whatsapp-gold.test/download/WhatsAppGold.apk"),
    ("apk_download", "http://bisp-registration.test/app/BISP_8171.apk"),
    ("apk_download", "https://daraz-sale.test/DarazBonus.apk"),
    ("exe_download", "http://zoom-update.test/ZoomInstaller.exe"),
    ("exe_download", "https://invoice-viewer.test/invoice_2026.pdf.exe"),
    ("prize_scam", "https://jeeto-pakistan-winner.test/claim-prize"),
    ("prize_scam", "https://telenor-lucky-draw.test/winner?id=88213"),
    ("gov_scam", "https://bisp-8171-payment.test/register"),
    ("gov_scam", "https://fbr-tax-refund.test/iris/claim"),
    ("gov_scam", "https://nadra-sim-verification.test/cnic"),
    ("delivery_scam", "https://tcs-parcel-held.test/track/PK9921"),
    ("delivery_scam", "https://dhl-customs-fee.test/pay"),
    ("job_scam", "https://work-from-home-pk.test/register-fee"),
    ("crypto_scam", "https://binance-airdrop-claim.test/connect-wallet"),
    ("crypto_scam", "https://usdt-double.invalid/deposit"),
    ("credential_path", "https://mail-storage-full.example/webmail/login.php?user=rector"),
    ("credential_path", "https://secure-update.invalid/banking/verify/card-details"),
]

SAFE_LINKS = [
    ("homepage", "https://www.hbl.com/"),
    ("homepage", "https://www.meezanbank.com/"),
    ("homepage", "https://www.nadra.gov.pk/"),
    ("homepage", "https://www.fbr.gov.pk/"),
    ("homepage", "https://nutech.edu.pk/"),
    ("homepage", "https://www.wikipedia.org/"),
    ("homepage", "https://github.com/"),
    ("deep_link", "https://en.wikipedia.org/wiki/Phishing"),
    ("deep_link", "https://docs.python.org/3/library/urllib.parse.html"),
    ("deep_link", "https://www.google.com/search?q=weather+islamabad"),
    ("deep_link", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
    ("deep_link", "https://stackoverflow.com/questions/tagged/python"),
    ("deep_link", "https://github.com/pytorch/pytorch/releases"),
    ("deep_link", "https://www.bbc.com/news/world-asia"),
    ("deep_link", "https://www.dawn.com/pakistan"),
    ("login_page", "https://accounts.google.com/signin"),
    ("login_page", "https://login.microsoftonline.com/"),
    ("login_page", "https://github.com/login"),
    ("long_query", "https://www.amazon.com/s?k=usb+c+cable&ref=nb_sb_noss"),
    ("long_query", "https://www.booking.com/searchresults.html?ss=Lahore&checkin=2026-12-01&checkout=2026-12-03"),
    ("download", "https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe"),
    ("download", "https://www.7-zip.org/a/7z2408-x64.exe"),
]

FRAUD_QR = [
    ("qr_bank_login", "url", "https://hbl-digital-banking.test/signin"),
    ("qr_parking_pay", "url", "https://city-parking-payment.test/pay?meter=4471"),
    ("qr_gov_refund", "url", "https://bisp-8171-payment.test/register"),
    ("qr_campus_portal", "url", "https://nutech-edu-pk.test/portal/password-reset"),
    ("qr_apk", "url", "http://whatsapp-gold.test/download/WhatsAppGold.apk"),
    ("qr_ip_host", "url", "http://192.0.2.44/hbl/login.php"),
    ("qr_payment", "payment", "upi://pay?pa=refund-desk@scam.test&pn=Refund%20Desk&am=5000&cu=PKR"),
    ("qr_wifi", "wifi", "WIFI:T:nopass;S:Free_Airport_WiFi_Login;;"),
    ("qr_sms", "sms", "SMSTO:+920000000000:Send 5000 to confirm your prize"),
    ("qr_text", "text", "Congratulations! Your CNIC won Rs 500000. Send your OTP to claim: visit prize-desk.test"),
    ("qr_contact", "contact", "BEGIN:VCARD\nVERSION:3.0\nFN:HBL Support\nTEL:+920000000000\nURL:https://hbl-login.test\nEND:VCARD"),
]

SAFE_QR = [
    ("qr_safe_university", "url", "https://nutech.edu.pk/"),
    ("qr_safe_wikipedia", "url", "https://en.wikipedia.org/wiki/QR_code"),
    ("qr_safe_python", "url", "https://www.python.org/"),
    ("qr_safe_wifi", "wifi", "WIFI:T:WPA;S:NUTECH_Lab_3;P:lab-guest-2026;;"),
    ("qr_safe_text", "text", "PDC lab moved to Lab 3 on Thursday at 2 pm."),
]

VARIANTS = ("clean", "rotated", "blurred", "dim", "perspective", "sticker")


def host_of(url: str) -> str:
    return (urlsplit(url).hostname or "").lower()


def is_unreachable(url: str) -> bool:
    host = host_of(url)
    if host.endswith(RESERVED_TLDS):
        return True
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    return any(address in net for net in DOC_NETS)


def guard(url: str) -> None:
    target = url
    if "?q=" in url and host_of(url) == "www.google.com":
        target = parse_qs(urlsplit(url).query)["q"][0]
    if not is_unreachable(target):
        sys.exit(f"Stopped: {url} could reach a real site")


def font(size: int):
    return ImageFont.load_default(size)


def base_code(payload: str) -> Image.Image:
    code = segno.make(payload, error="m", micro=False)
    side = code.symbol_size(scale=8, border=4)[0]
    canvas = Image.new("RGB", (side, side), "white")
    pixels = canvas.load()
    for row, line in enumerate(code.matrix_iter(scale=8, border=4)):
        for col, dark in enumerate(line):
            if dark:
                pixels[col, row] = (0, 0, 0)
    return canvas


def caption(image: Image.Image, label: str) -> Image.Image:
    height = image.height + 56
    canvas = Image.new("RGB", (max(image.width, 420), height), "white")
    canvas.paste(image, ((canvas.width - image.width) // 2, 0))
    draw = ImageDraw.Draw(canvas)
    draw.text((canvas.width / 2, image.height + 6), "STL TEST CODE. NOT A REAL OFFER.", fill="black", font=font(18), anchor="ma")
    draw.text((canvas.width / 2, image.height + 30), label, fill="black", font=font(14), anchor="ma")
    return canvas


def perspective(image: Image.Image) -> Image.Image:
    w, h = image.size
    shift = w * 0.09
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    dst = [(shift, h * 0.04), (w - shift * 0.3, 0), (w, h), (0, h * 0.95)]
    matrix = []
    for (x, y), (u, v) in zip(dst, src):
        matrix.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        matrix.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    target = [c for point in src for c in point]
    import numpy as np

    coeffs = np.linalg.solve(np.array(matrix, dtype=float), np.array(target, dtype=float))
    return image.transform((w, h), Image.PERSPECTIVE, tuple(coeffs), Image.BICUBIC, fillcolor="white")


def sticker(image: Image.Image) -> Image.Image:
    poster = Image.new("RGB", (image.width + 220, image.height + 300), (232, 232, 232))
    draw = ImageDraw.Draw(poster)
    draw.rectangle((30, 30, poster.width - 30, poster.height - 30), outline=(60, 60, 60), width=4)
    draw.text((poster.width / 2, 60), "SCAN TO PAY", fill=(30, 30, 30), font=font(44), anchor="ma")
    draw.text((poster.width / 2, poster.height - 90), "Test poster", fill=(70, 70, 70), font=font(24), anchor="ma")
    tilted = image.rotate(5, expand=True, fillcolor="white")
    poster.paste(tilted, ((poster.width - tilted.width) // 2, 130))
    return poster


def apply_variant(image: Image.Image, variant: str) -> Image.Image:
    if variant == "rotated":
        return image.rotate(12, expand=True, fillcolor="white")
    if variant == "blurred":
        return image.filter(ImageFilter.GaussianBlur(1.6))
    if variant == "dim":
        return ImageEnhance.Contrast(ImageEnhance.Brightness(image).enhance(0.75)).enhance(0.45)
    if variant == "perspective":
        return perspective(image)
    if variant == "sticker":
        return sticker(image)
    return image


def read_back(path: Path) -> str | None:
    with Image.open(path) as image:
        found = zxingcpp.read_barcodes(image.convert("RGB"))
    return found[0].text if found else None


def write_links() -> int:
    rows = []
    for index, (kind, url) in enumerate(FRAUD_LINKS, 1):
        guard(url)
        rows.append({"id": f"fraud-{index:03}", "url": url, "label": "fraud", "kind": kind})
    for index, (kind, url) in enumerate(SAFE_LINKS, 1):
        rows.append({"id": f"safe-{index:03}", "url": url, "label": "safe", "kind": kind})
    with (OUT / "links.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "url", "label", "kind"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def write_codes() -> tuple[int, int]:
    rows = []
    failed = 0
    for label, group in (("fraud", FRAUD_QR), ("safe", SAFE_QR)):
        for name, kind, payload in group:
            if label == "fraud" and kind == "url":
                guard(payload)
            base = caption(base_code(payload), name)
            for variant in VARIANTS:
                path = QR_DIR / f"{name}_{variant}.png"
                apply_variant(base, variant).save(path)
                decoded = read_back(path)
                ok = decoded == payload
                failed += not ok
                rows.append(
                    {
                        "file": path.name,
                        "name": name,
                        "label": label,
                        "kind": kind,
                        "variant": variant,
                        "payload": payload,
                        "decoded_ok": ok,
                    }
                )
    with (QR_DIR / "manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return len(rows), failed


def write_gallery() -> None:
    cards = []
    for label, group in (("Fraud test", FRAUD_QR), ("Safe test", SAFE_QR)):
        for name, _, payload in group:
            cards.append(
                f'<figure><img src="{name}_clean.png" alt="{html.escape(name)}">'
                f"<figcaption><b>{label}</b><br>{html.escape(payload)}</figcaption></figure>"
            )
    page = (
        "<!doctype html><meta charset=utf-8><title>STL test QR codes</title>"
        "<style>body{font:14px/1.4 Arial,sans-serif;margin:16px;color:#111}"
        "main{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}"
        "figure{margin:0;border:1px solid #bbb;padding:8px}img{width:100%}"
        "figcaption{word-break:break-all;font-size:12px}</style>"
        "<h1>STL test QR codes</h1>"
        "<p>Every fraud code uses a reserved test name that cannot reach a real website.</p>"
        f"<main>{''.join(cards)}</main>"
    )
    (QR_DIR / "index.html").write_text(page, encoding="utf-8")


def main() -> None:
    QR_DIR.mkdir(parents=True, exist_ok=True)
    links = write_links()
    codes, failed = write_codes()
    write_gallery()
    print(f"{links} links, {codes} QR images, {failed} could not be read back")


if __name__ == "__main__":
    main()
