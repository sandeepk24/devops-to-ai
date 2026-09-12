"""
Mock planner for the Phase 09 intent-ops-platform.

Deliberately deterministic. Phase 08 already taught tool-calling and
LLM-backed planning — bolting a real model in here is a documented Path B
stretch (see docs/path-b-real-infra.md), not the point of this lab. The
point is everything *around* the planner: policy, approval, bounded
retries, and the episode record. So this function just maps a known cause
to a known-safe action.
"""

from __future__ import annotations

from typing import Any


def plan_step(service_snapshot: dict[str, Any]) -> dict[str, Any]:
    """
    Given one service's current state (plus its name), propose the next step.

    Returns a dict with `action` (or None), `args`, and a human-readable
    `rationale` — the "why" a reviewer sees before approving.
    """
    cause = service_snapshot.get("cause")
    service_name = service_snapshot.get("name")

    if cause == "bad_deploy":
        return {
            "action": "rollback",
            "args": {"service": service_name},
            "rationale": (
                "Error spike lines up with the latest deploy — rollback is the "
                "known-safe first move for this cause."
            ),
        }

    if cause == "overload":
        target_replicas = max(int(service_snapshot["replicas"]) * 2, 1)
        return {
            "action": "scale_replicas",
            "args": {"service": service_name, "replicas": target_replicas},
            "rationale": (
                f"Error rate tracks load, not a bad deploy — doubling replicas to "
                f"{target_replicas} to spread it out."
            ),
        }

    return {
        "action": None,
        "args": {},
        "rationale": f"No known-safe action mapped for cause='{cause}' — this needs a human.",
    }
