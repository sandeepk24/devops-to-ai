#!/usr/bin/env python3
"""
Eval suite for the Phase 09 intent ops platform.

Each case resets the mock world first, so cases never depend on the order
they run in. Run against a live orchestrator:

    AGENT_URL=http://localhost:8200 python3 scripts/run_evals.py
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

AGENT = os.getenv("AGENT_URL", "http://localhost:8200").rstrip("/")
ROOT = Path(__file__).resolve().parents[1]
CASES_FILE = ROOT / "fixtures" / "eval" / "cases.jsonl"
INTENTS_DIR = ROOT / "fixtures" / "intents"


def http_json(method: str, path: str, body: dict[str, Any] | None = None) -> tuple[int, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"} if body is not None else {}
    req = urllib.request.Request(f"{AGENT}{path}", data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = {"detail": raw}
        return exc.code, parsed


def load_intent(name: str) -> dict[str, Any]:
    return json.loads((INTENTS_DIR / f"{name}.json").read_text(encoding="utf-8"))


def submit(name: str) -> tuple[int, Any]:
    return http_json("POST", "/v1/intents", load_intent(name))


def run_case(case: dict[str, Any]) -> None:
    check = case.get("check")

    if check == "double_approve":
        code, ep = submit(case["intent"])
        assert code == 200 and ep["status"] == "awaiting_approval", ep
        code2, ep2 = http_json("POST", f"/v1/episodes/{ep['id']}/approve", {"approver": "eval"})
        assert code2 == 200 and ep2["status"] in {"succeeded", "escalated_needs_human"}, ep2
        code3, ep3 = http_json("POST", f"/v1/episodes/{ep['id']}/approve", {"approver": "eval"})
        assert code3 == 400, (code3, ep3)
        return

    if check == "deny_after_terminal":
        code, ep = submit(case["intent"])
        assert code == 200 and ep["status"] == "awaiting_approval", ep
        code2, ep2 = http_json("POST", f"/v1/episodes/{ep['id']}/approve", {"approver": "eval"})
        assert code2 == 200, ep2
        code3, ep3 = http_json("POST", f"/v1/episodes/{ep['id']}/deny", {"approver": "eval"})
        assert code3 == 400, (code3, ep3)
        return

    code, ep = submit(case["intent"])
    assert code == 200, ep

    if case.get("approve"):
        code2, ep = http_json("POST", f"/v1/episodes/{ep['id']}/approve", {"approver": "eval"})
        assert code2 == 200, ep

    expect_status = case.get("expect_status")
    if expect_status:
        assert ep["status"] == expect_status, f"expected {expect_status}, got {ep['status']}"

    if "expect_attempts" in case:
        got = len(ep["plan"])
        assert got == case["expect_attempts"], f"expected {case['expect_attempts']} attempts, got {got}"

    if "expect_environment" in case:
        got_env = ep["intent"]["environment"]
        assert got_env == case["expect_environment"], f"expected env {case['expect_environment']}, got {got_env}"


def main() -> int:
    failed = 0
    for line in CASES_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        case = json.loads(line)
        cid = case["id"]
        http_json("POST", "/v1/reset")
        try:
            run_case(case)
            print(f"PASS {cid}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {cid}: {exc}")
        except Exception as exc:  # noqa: BLE001 - surface unexpected errors as failures
            failed += 1
            print(f"FAIL {cid}: unexpected error: {exc}")

    if failed:
        print(f"{failed} eval(s) failed")
        return 1
    print("EVALS OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
