"""Run every dashboard scenario against the running server and record what happened."""
import json
import sys
import time
import urllib.request
from pathlib import Path

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8050"
OUT = Path(__file__).resolve().parent.parent / "results" / "scenarios.json"


def call(path: str, method: str = "GET"):
    request = urllib.request.Request(BASE + path, method=method)
    with urllib.request.urlopen(request, timeout=400) as response:
        return json.load(response)


def main() -> None:
    rows = []
    for scenario in call("/api/scenarios"):
        started = time.time()
        item = call(f"/api/scenarios/{scenario['id']}/run", "POST")["id"]
        record = call(f"/api/verdicts/{item}")
        verdict = record["verdict"]
        application, network = verdict["findings"]
        expected_flag = scenario["expected"] == "flag"
        passed = verdict["action"] in ("flag", "block") if expected_flag else verdict["action"] in ("allow", "warn")
        row = {
            "scenario": scenario["id"],
            "expected": scenario["expected"],
            "action": verdict["action"],
            "risk": verdict["risk"],
            "application_risk": round(application["risk"], 3),
            "network_risk": round(network["risk"], 3),
            "labels": verdict["labels"],
            "flagged_by": verdict["flagged_by"],
            "language_model_used": any(e["source"] == "language model" for e in application["evidence"]),
            "review_confidence": application["scores"].get("review_confidence"),
            "signature_valid": record["signature_valid"],
            "seconds": round(time.time() - started, 2),
            "passed": passed,
        }
        rows.append(row)
        print(json.dumps(row), flush=True)
    summary = {"passed": sum(row["passed"] for row in rows), "total": len(rows), "rows": rows}
    OUT.write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(summary["passed"], "of", summary["total"], "scenarios behaved as expected")


if __name__ == "__main__":
    main()
