"""Keeps verdicts in a small SQLite file for the dashboard."""
from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

from .schema import Item, Verdict

COLUMNS = ("id", "at", "kind", "action", "risk", "labels", "sender", "summary", "flagged_by", "seconds")


class VerdictStore:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute(
            "create table if not exists verdicts ("
            "id text primary key, at real, kind text, action text, risk real, labels text, sender text, "
            "summary text, flagged_by text, seconds real, item text, verdict text, envelope text)"
        )
        self.db.commit()

    def save(self, item: Item, verdict: Verdict, envelope: dict) -> None:
        names = [flow.sni or flow.dns_query for flow in item.flows if flow.sni or flow.dns_query]
        summary = item.subject or item.text or item.file_name or (item.urls[0] if item.urls else "")
        summary = summary or (item.qr_payloads[0] if item.qr_payloads else "") or (f"Session to {names[-1]}" if names else f"{len(item.flows)} connections")
        with self.lock:
            self.db.execute(
                "insert or replace into verdicts values (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    item.id,
                    verdict.decided_at,
                    item.kind,
                    verdict.action,
                    verdict.risk,
                    ",".join(verdict.labels),
                    item.sender or item.source_host or "",
                    summary[:160],
                    ",".join(verdict.flagged_by),
                    verdict.seconds,
                    item.model_dump_json(),
                    verdict.model_dump_json(),
                    json.dumps(envelope),
                ),
            )
            self.db.commit()

    def recent(self, limit: int = 100, action: str | None = None, found_by: str | None = None, kind: str | None = None) -> list[dict]:
        query = f"select {', '.join(COLUMNS)} from verdicts"
        clauses, args = [], []
        if action:
            clauses.append("action = ?")
            args.append(action)
        if kind:
            clauses.append("kind = ?")
            args.append(kind)
        if found_by == "both":
            clauses.append("flagged_by like '%,%'")
        elif found_by == "application":
            clauses.append("flagged_by = 'application-agent'")
        elif found_by == "network":
            clauses.append("flagged_by = 'network-agent'")
        if clauses:
            query += " where " + " and ".join(clauses)
        with self.lock:
            rows = self.db.execute(query + " order by at desc limit ?", (*args, limit)).fetchall()
        return [dict(zip(COLUMNS, row)) for row in rows]

    def one(self, item_id: str) -> dict | None:
        with self.lock:
            row = self.db.execute("select item, verdict, envelope from verdicts where id = ?", (item_id,)).fetchone()
        if row is None:
            return None
        return {"item": json.loads(row[0]), "verdict": json.loads(row[1]), "envelope": json.loads(row[2])}

    def counts(self) -> dict[str, int]:
        with self.lock:
            rows = self.db.execute("select action, count(*) from verdicts group by action").fetchall()
        return {action: count for action, count in rows}

    def stats(self) -> dict:
        with self.lock:
            actions = self.db.execute("select action, count(*) from verdicts group by action").fetchall()
            found = self.db.execute("select flagged_by, count(*) from verdicts where flagged_by != '' group by flagged_by").fetchall()
            labels = self.db.execute("select labels from verdicts where labels != ''").fetchall()
            timing = self.db.execute("select avg(seconds), max(seconds), count(*) from verdicts").fetchone()
        tally: dict[str, int] = {}
        for (value,) in labels:
            for label in value.split(","):
                tally[label] = tally.get(label, 0) + 1
        by_agent = {"application": 0, "network": 0, "both": 0}
        for value, count in found:
            key = "both" if "," in value else value.replace("-agent", "")
            by_agent[key] = by_agent.get(key, 0) + count
        return {
            "actions": dict(actions),
            "found_by": by_agent,
            "labels": tally,
            "total": timing[2] or 0,
            "mean_seconds": round(timing[0] or 0.0, 3),
            "max_seconds": round(timing[1] or 0.0, 3),
        }

    def clear(self) -> None:
        with self.lock:
            self.db.execute("delete from verdicts")
            self.db.commit()
