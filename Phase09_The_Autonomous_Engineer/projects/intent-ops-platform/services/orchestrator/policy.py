"""
Policy checks for the Phase 09 intent-ops-platform.

Everything here is deliberately boring: allowlists and numeric caps read
from the environment at startup. No LLM, no scoring, no vibes — a function
either says yes, or gives a plain-English reason why not.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

ALLOWED_GOALS = {"reduce_error_rate"}

ALLOWED_ENVIRONMENTS = {
    e.strip()
    for e in os.getenv("ALLOWED_ENVIRONMENTS", "dev,staging").split(",")
    if e.strip()
}

ALLOWED_ACTIONS = {
    a.strip()
    for a in os.getenv("ALLOWED_ACTIONS", "rollback,scale_replicas").split(",")
    if a.strip()
}

MAX_ATTEMPTS_CAP = int(os.getenv("MAX_ATTEMPTS_CAP", "2"))
MAX_REPLICAS = int(os.getenv("MAX_REPLICAS", "16"))


@dataclass
class PolicyResult:
    ok: bool
    reason: str = ""


def check_intent(intent: dict[str, Any]) -> PolicyResult:
    """Gate #1 — does this ask even make sense to plan for?"""
    goal = intent.get("goal")
    environment = intent.get("environment")
    target = intent.get("target_error_rate")

    if goal not in ALLOWED_GOALS:
        return PolicyResult(
            False, f"goal '{goal}' is not enabled here — allowed: {sorted(ALLOWED_GOALS)}"
        )
    if environment not in ALLOWED_ENVIRONMENTS:
        return PolicyResult(
            False,
            f"environment '{environment}' is not enabled in this lab — allowed: "
            f"{sorted(ALLOWED_ENVIRONMENTS)} (prod needs a higher trust tier and its own "
            "approval chain in a real org, not a flag flip)",
        )
    if target is None or not (0 <= float(target) <= 1):
        return PolicyResult(False, "target_error_rate must be a number between 0 and 1")
    return PolicyResult(True)


def check_action(action: Optional[str], args: dict[str, Any]) -> PolicyResult:
    """Gate #2 — does the proposed action stay inside what's allowed and how big it can be?"""
    if action is None:
        return PolicyResult(False, "no allowlisted action maps to this situation")
    if action not in ALLOWED_ACTIONS:
        return PolicyResult(
            False, f"action '{action}' is not allowlisted — allowed: {sorted(ALLOWED_ACTIONS)}"
        )
    if action == "scale_replicas":
        replicas = args.get("replicas")
        if not isinstance(replicas, int) or replicas <= 0:
            return PolicyResult(False, "scale_replicas requires a positive integer replica count")
        if replicas > MAX_REPLICAS:
            return PolicyResult(
                False,
                f"scale_replicas to {replicas} exceeds MAX_REPLICAS={MAX_REPLICAS} "
                "(blast-radius cap)",
            )
    return PolicyResult(True)


def effective_max_attempts(requested: Optional[int]) -> int:
    """The caller can ask for fewer attempts, never more than the policy-owned cap."""
    if not requested or requested <= 0:
        return MAX_ATTEMPTS_CAP
    return min(int(requested), MAX_ATTEMPTS_CAP)
