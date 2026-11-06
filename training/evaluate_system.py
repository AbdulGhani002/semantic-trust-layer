"""Experiment E7: real SMTP sessions through the gateway, with both agents.

Public data does not link one event across both layers. So each session here
pairs real held-out content with a real held-out traffic history. This tests
how the agents combine. It is not field data, and because a harmful side is
always placed in every flagged group, the joined result beating one agent is
built into the design. Report it as a system test only.

Four kinds of session are sent:
  content fine, behaviour normal    expected: allow
  content harmful, behaviour normal expected: flag
  content fine, behaviour bad       expected: flag
  content harmful, behaviour bad    expected: flag
"""
import argparse
import json
import random
import smtplib
import sys
import time
from email.message import EmailMessage
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from stl.api import Layer  # noqa: E402
from stl.gateway import start_mail  # noqa: E402
from stl.schema import Flow  # noqa: E402

WORK = ROOT / "data" / "work"
RESULTS = ROOT / "results"
PORT = 8125


def content_sets(rng: random.Random, size: int) -> tuple[list[str], list[str]]:
    fraud = pd.read_parquet(WORK / "text_test_fraud_email_unseen_source.parquet")
    civil = pd.read_parquet(WORK / "text_test_abuse_civil.parquet")
    harmful = fraud.loc[fraud["fraud"] == 1, "text"].tolist()
    toxic = civil[(civil["threat"] == 1) | (civil["hate"] == 1) | (civil["abuse"] == 1)]["text"].tolist()
    normal = fraud.loc[fraud["fraud"] == 0, "text"].tolist() + civil[(civil["abuse"] == 0) & (civil["hate"] == 0) & (civil["threat"] == 0)]["text"].tolist()[:3000]
    rng.shuffle(harmful)
    rng.shuffle(toxic)
    rng.shuffle(normal)
    mix = harmful[: size // 2] + toxic[: size - size // 2]
    rng.shuffle(mix)
    return mix, normal[:size * 2]


def held_out(name: str) -> pd.DataFrame:
    """The last 20% of each label in a day, which no traffic model trained on."""
    table = pd.read_parquet(WORK / "flows" / f"{name}.parquet")
    table = table[table["start"].notna()].reset_index(drop=True)
    place = table.sort_values("start", kind="stable").groupby("label", sort=False).cumcount()
    sizes = table.groupby("label", sort=False)["label"].transform("size")
    table["held_out"] = (place.reindex(table.index) / sizes) >= 0.8
    table["src"] = name + "_" + table["src"].astype(str)
    return table


def histories(rng: random.Random, size: int) -> tuple[list[list[Flow]], list[list[Flow]]]:
    table = pd.concat([held_out("cic_thursday"), held_out("cic_friday")], ignore_index=True)
    parts = {host: part.sort_values("start", kind="stable") for host, part in table.groupby("src") if len(part) >= 32}
    by_attack: dict[str, list[tuple[str, int]]] = {}
    good: list[tuple[str, int]] = []
    for host, part in parts.items():
        attack = part["attack"].to_numpy()
        held = part["held_out"].to_numpy()
        labels = part["label"].to_numpy()
        for end in range(32, len(part) + 1, 16):
            if not held[end - 8 : end].all():
                continue
            share = attack[end - 8 : end].mean()
            if share > 0.5:
                by_attack.setdefault(str(labels[end - 1]), []).append((host, end))
            elif share == 0:
                good.append((host, end))
    for windows in by_attack.values():
        rng.shuffle(windows)
    rng.shuffle(good)
    bad: list[tuple[str, int]] = []
    while len(bad) < size and any(by_attack.values()):
        for windows in by_attack.values():
            if windows and len(bad) < size:
                bad.append(windows.pop())

    def build(pairs):
        result = []
        for host, end in pairs:
            flows = [
                Flow(
                    src="", dst=row.dst, sport=int(row.sport), dport=int(row.dport), proto=row.proto, start=float(row.start),
                    duration=float(row.duration), packets=int(row.packets), bytes=int(row.bytes), src_bytes=int(row.src_bytes),
                )
                for row in parts[host].iloc[end - 31 : end].itertuples()
            ]
            result.append(flows)
        return result

    print("attack windows", {name: len(windows) for name, windows in by_attack.items()}, "chosen", len(bad), flush=True)
    return build(bad), build(good[:size * 2])


def send(address: str, port: int, text: str, index: int) -> bool:
    message = EmailMessage()
    message["From"] = f"sender{index}@campus.test"
    message["To"] = "rector@nutech.test"
    subject, _, body = text.partition("\n")
    if subject.startswith("Subject: "):
        message["Subject"] = subject[9:60]
    else:
        message["Subject"] = "Message"
        body = text
    message.set_content(body or text)
    try:
        with smtplib.SMTP("127.0.0.1", port, source_address=(address, 0), timeout=180) as client:
            client.send_message(message)
    except smtplib.SMTPDataError:
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-group", type=int, default=100)
    parser.add_argument("--no-language-model", action="store_true")
    args = parser.parse_args()
    rng = random.Random(7)
    database = WORK / "system_eval.db"
    database.unlink(missing_ok=True)
    layer = Layer(database)
    if args.no_language_model:
        layer.application.reviewer = None
    controller = start_mail(layer.coordinator, layer.ledger, ROOT / "data" / "mailbox_eval", PORT)
    harmful, normal = content_sets(rng, args.per_group * 2)
    bad, good = histories(rng, args.per_group * 2)
    size = args.per_group
    plan = (
        [("clean_clean", False, False, normal[i], good[i]) for i in range(size)]
        + [("harmful_content", True, False, harmful[i], good[size + i]) for i in range(size)]
        + [("bad_behaviour", False, True, normal[size + i], bad[i]) for i in range(size)]
        + [("both_bad", True, True, harmful[size + i], bad[size + i]) for i in range(size)]
    )
    rng.shuffle(plan)
    rows = []
    started = time.time()
    for index, (group, bad_content, bad_host, text, history) in enumerate(plan):
        address = f"127.0.{1 + index // 250}.{1 + index % 250}"
        for flow in history:
            layer.ledger.add(flow.model_copy(update={"src": address}))
        began = time.time()
        accepted = send(address, PORT, text, index)
        took = time.time() - began
        latest = layer.store.recent(1)[0]
        record = layer.store.one(latest["id"])
        application, network = record["verdict"]["findings"]
        rows.append(
            {
                "group": group, "expected_flag": bad_content or bad_host, "action": record["verdict"]["action"],
                "application_risk": application["risk"], "network_risk": network["risk"], "joined_risk": record["verdict"]["risk"],
                "accepted": accepted, "seconds": took, "signature_valid": layer.coordinator.verify(record["envelope"]),
            }
        )
        if index % 50 == 0:
            print(index, "of", len(plan), round(time.time() - started), "s", flush=True)
    controller.stop()
    table = pd.DataFrame(rows)
    name = "system_no_language_model" if args.no_language_model else "system"
    table.to_csv(RESULTS / f"{name}_sessions.csv", index=False)

    def score(flagged: pd.Series) -> dict:
        y = table["expected_flag"]
        tp, fp = int((flagged & y).sum()), int((flagged & ~y).sum())
        fn, tn = int((~flagged & y).sum()), int((~flagged & ~y).sum())
        return {
            "recall": round(tp / max(1, tp + fn), 4), "precision": round(tp / max(1, tp + fp), 4),
            "false_alarm_rate": round(fp / max(1, fp + tn), 4), "f1": round(2 * tp / max(1, 2 * tp + fp + fn), 4),
            "by_group": {g: round(float(flagged[table["group"] == g].mean()), 4) for g in sorted(table["group"].unique())},
        }

    report = {
        "sessions": len(table),
        "language_model": layer.application.reviewer is not None,
        "application_only": score(table["application_risk"] >= 0.5),
        "network_only": score(table["network_risk"] >= 0.5),
        "both_joined": score(table["joined_risk"] >= 0.5),
        "actions_by_group": {g: part["action"].value_counts().to_dict() for g, part in table.groupby("group")},
        "clean_sessions_blocked": int(((table["group"] == "clean_clean") & (table["action"] == "block")).sum()),
        "all_signatures_valid": bool(table["signature_valid"].all()),
        "seconds_per_session": {"median": round(float(table["seconds"].median()), 3), "p95": round(float(table["seconds"].quantile(0.95)), 3)},
    }
    (RESULTS / f"{name}.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
