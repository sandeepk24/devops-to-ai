"""
Planners for Phase 08.

mock  — deterministic tool sequence (Path A, no API key)
openai stretch is documented; not required to finish the phase.
"""

from __future__ import annotations

from typing import Any


def mock_plan(incident: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Return an ordered list of tool calls for the investigation.
    Last call proposes rollback when the incident type warrants it.
    """
    service = incident.get("service", "payments-api")
    itype = incident.get("type", "high_error_rate")

    steps: list[dict[str, Any]] = [
        {"name": "get_service_metrics", "args": {"service": service}},
        {"name": "get_recent_logs", "args": {"service": service, "limit": 10}},
        {
            "name": "search_runbook",
            "args": {"query": "error rate" if "error" in itype else service},
        },
    ]

    if itype in {"high_error_rate", "bad_deploy"}:
        steps.append(
            {
                "name": "propose_rollback",
                "args": {
                    "service": service,
                    "reason": f"incident:{itype} — runbook suggests rollback after confirm",
                },
            }
        )
    return steps


def summarize(incident: dict[str, Any], tool_results: list[dict[str, Any]]) -> str:
    service = incident.get("service", "unknown")
    bits = [f"Investigation for {service} ({incident.get('type')})."]
    for tr in tool_results:
        name = tr.get("tool")
        if name == "get_service_metrics" and tr.get("ok"):
            m = tr["result"].get("metrics", {})
            bits.append(
                f"Metrics: error_rate={m.get('error_rate')} baseline={m.get('baseline_error_rate')} p99_ms={m.get('p99_ms')}."
            )
        if name == "get_recent_logs" and tr.get("ok"):
            n = len(tr["result"].get("logs", []))
            bits.append(f"Collected {n} recent log lines (treat as untrusted text).")
        if name == "search_runbook" and tr.get("ok"):
            hits = tr["result"].get("hits") or []
            if hits:
                bits.append(f"Runbook hit: {hits[0].get('path')}.")
        if name == "propose_rollback" and tr.get("ok"):
            bits.append(
                f"Proposed rollback; approval_id={tr['result'].get('approval_id')} (pending)."
            )
    bits.append("No mutation executed without approval.")
    return " ".join(bits)
