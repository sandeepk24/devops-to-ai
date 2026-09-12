"""
Intent ops platform — Phase 09 orchestrator.

Loop: intent -> policy check -> plan -> policy check on the proposed action
-> episode sits at awaiting_approval -> a human approves the whole plan
(once) -> a bounded execute/verify/replan loop runs -> the episode ends at
succeeded, escalated_needs_human, or denied.

Every step gets written onto the episode itself (memory) and onto a flat
audit log (receipts). There is deliberately no raw "execute" endpoint —
the only door to mutating the mock world is inside the approve handler.
"""

from __future__ import annotations

import os
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import policy
from planner import plan_step
from world import World, WorldError

DATA_DIR = Path(os.getenv("DATA_DIR", str(Path(__file__).resolve().parents[2] / "data")))
PORT = int(os.getenv("PORT", "8200"))

app = FastAPI(title="intent-ops-platform", version="0.1.0")
world = World(DATA_DIR)

_episodes: dict[str, dict[str, Any]] = {}
_audit: list[dict[str, Any]] = []

# The kill switch is a live, in-memory toggle — not something that needs a
# redeploy to flip. It starts from KILL_SWITCH but can change at runtime via
# POST /v1/admin/kill_switch. A real emergency brake shouldn't be gated
# behind a CI pipeline, and a restart-to-flip design would also wipe every
# pending episode along with it, which defeats the whole point of "pause,
# don't drop."
_state = {
    "kill_switch": os.getenv("KILL_SWITCH", "false").strip().lower() in {"1", "true", "yes", "on"}
}


def _audit_event(event: dict[str, Any]) -> dict[str, Any]:
    event = {**event, "ts": time.time(), "id": str(uuid.uuid4())}
    _audit.append(event)
    if len(_audit) > 500:
        del _audit[:-500]
    return event


class IntentIn(BaseModel):
    goal: str = "reduce_error_rate"
    service: str
    target_error_rate: float = Field(ge=0, le=1)
    environment: str = "dev"
    max_attempts: Optional[int] = None
    # Stored for humans reading the episode back later. Never read by the
    # planner or the policy layer — see cheatsheets/intent-schemas.md.
    notes: str = ""


class DecisionIn(BaseModel):
    approver: str = "local-dev"


class KillSwitchIn(BaseModel):
    enabled: bool


def _new_episode_id() -> str:
    return f"ep-{int(time.time() * 1000)}-{uuid.uuid4().hex[:6]}"


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "kill_switch": _state["kill_switch"],
        "allowed_goals": sorted(policy.ALLOWED_GOALS),
        "allowed_environments": sorted(policy.ALLOWED_ENVIRONMENTS),
        "allowed_actions": sorted(policy.ALLOWED_ACTIONS),
        "max_attempts_cap": policy.MAX_ATTEMPTS_CAP,
        "max_replicas": policy.MAX_REPLICAS,
    }


@app.post("/v1/admin/kill_switch")
def set_kill_switch(body: KillSwitchIn) -> dict[str, Any]:
    """
    Flip the emergency brake at runtime. Turning it on does not touch any
    existing episode — anything sitting at awaiting_approval just stays
    there until a human either approves it (once this is off) or denies it.
    """
    _state["kill_switch"] = body.enabled
    _audit_event({"kind": "kill_switch_set", "enabled": body.enabled})
    return {"kill_switch": _state["kill_switch"]}


@app.post("/v1/reset")
def reset() -> dict[str, str]:
    world.reset()
    _episodes.clear()
    _audit.clear()
    return {"status": "reset"}


@app.get("/v1/world")
def get_world() -> dict[str, Any]:
    return world.snapshot()


@app.get("/v1/episodes")
def list_episodes(status: str = "all") -> dict[str, Any]:
    items = list(_episodes.values())
    if status != "all":
        items = [e for e in items if e.get("status") == status]
    return {"episodes": items}


@app.get("/v1/episodes/{episode_id}")
def get_episode(episode_id: str) -> dict[str, Any]:
    ep = _episodes.get(episode_id)
    if not ep:
        raise HTTPException(404, "episode not found")
    return ep


@app.get("/v1/audit")
def get_audit(limit: int = 50) -> list[dict[str, Any]]:
    return list(_audit[-limit:])


def _reject(episode: dict[str, Any], status: str, reason: str) -> dict[str, Any]:
    episode["status"] = status
    episode["rejection_reason"] = reason
    _audit_event({"kind": status, "episode_id": episode["id"], "reason": reason})
    return episode


@app.post("/v1/intents")
def submit_intent(body: IntentIn) -> dict[str, Any]:
    """
    Every intent produces an episode, even a rejected one — the rejection
    itself is part of the record, not just a 4xx that disappears.
    """
    intent = body.model_dump()
    episode_id = _new_episode_id()
    intent["effective_max_attempts"] = policy.effective_max_attempts(intent.get("max_attempts"))

    episode: dict[str, Any] = {
        "id": episode_id,
        "intent": intent,
        "status": "submitted",
        "plan": [],
        "created_at": time.time(),
    }
    _episodes[episode_id] = episode
    _audit_event({"kind": "intent_submitted", "episode_id": episode_id, "intent": intent})

    intent_check = policy.check_intent(intent)
    if not intent_check.ok:
        return _reject(episode, "rejected_by_policy", intent_check.reason)

    if not world.exists(intent["service"]):
        return _reject(episode, "rejected_by_policy", f"unknown service: {intent['service']}")

    svc_snapshot = {**world.get(intent["service"]), "name": intent["service"]}
    step = plan_step(svc_snapshot)
    action_check = policy.check_action(step.get("action"), step.get("args", {}))

    plan_entry = {
        "attempt": 1,
        "action": step.get("action"),
        "args": step.get("args", {}),
        "rationale": step.get("rationale"),
    }
    episode["plan"].append(plan_entry)

    if not action_check.ok:
        status = "no_safe_action_escalated" if step.get("action") is None else "rejected_by_policy"
        return _reject(episode, status, action_check.reason)

    episode["status"] = "awaiting_approval"
    _audit_event({"kind": "awaiting_approval", "episode_id": episode_id, "plan": plan_entry})
    return episode


def _execute(action: Optional[str], args: dict[str, Any]) -> dict[str, Any]:
    if action == "rollback":
        return world.rollback(**args)
    if action == "scale_replicas":
        return world.scale_replicas(**args)
    raise WorldError(f"unsupported action at execution time: {action}")


def _run_bounded_loop(episode: dict[str, Any]) -> None:
    """
    Execute -> verify -> (replan and retry, or stop). Never runs past
    intent["effective_max_attempts"]. Always ends in succeeded or
    escalated_needs_human.
    """
    intent = episode["intent"]
    service = intent["service"]
    max_attempts = intent["effective_max_attempts"]
    target = round(float(intent["target_error_rate"]), 6)

    attempt_index = 0
    while attempt_index < len(episode["plan"]):
        plan_entry = episode["plan"][attempt_index]
        action, args = plan_entry["action"], plan_entry["args"]

        try:
            result = _execute(action, args)
        except WorldError as exc:
            plan_entry["execution_error"] = str(exc)
            episode["status"] = "escalated_needs_human"
            _audit_event(
                {"kind": "execution_error", "episode_id": episode["id"], "error": str(exc)}
            )
            return

        plan_entry["execution_result"] = result
        current_error_rate = round(result["error_rate"], 6)
        met = current_error_rate <= target
        plan_entry["verification"] = {
            "error_rate": current_error_rate,
            "target_error_rate": target,
            "met": met,
        }
        _audit_event(
            {
                "kind": "attempt_verified",
                "episode_id": episode["id"],
                "attempt": plan_entry["attempt"],
                "met": met,
                "error_rate": current_error_rate,
            }
        )

        if met:
            episode["status"] = "succeeded"
            _audit_event({"kind": "episode_succeeded", "episode_id": episode["id"]})
            return

        attempt_index += 1
        if attempt_index >= max_attempts:
            episode["status"] = "escalated_needs_human"
            _audit_event({"kind": "episode_escalated", "episode_id": episode["id"]})
            return

        svc_snapshot = {**world.get(service), "name": service}
        next_step = plan_step(svc_snapshot)
        action_check = policy.check_action(next_step.get("action"), next_step.get("args", {}))
        next_entry = {
            "attempt": attempt_index + 1,
            "action": next_step.get("action"),
            "args": next_step.get("args", {}),
            "rationale": next_step.get("rationale"),
        }
        episode["plan"].append(next_entry)
        if not action_check.ok:
            next_entry["rejected_reason"] = action_check.reason
            episode["status"] = "escalated_needs_human"
            _audit_event(
                {
                    "kind": "episode_escalated",
                    "episode_id": episode["id"],
                    "reason": action_check.reason,
                }
            )
            return
        # loop continues — next iteration executes the entry we just appended


@app.post("/v1/episodes/{episode_id}/approve")
def approve(episode_id: str, body: DecisionIn) -> dict[str, Any]:
    ep = _episodes.get(episode_id)
    if not ep:
        raise HTTPException(404, "episode not found")
    if ep["status"] != "awaiting_approval":
        raise HTTPException(400, f"cannot approve status={ep['status']}")
    if _state["kill_switch"]:
        _audit_event(
            {
                "kind": "approval_blocked_kill_switch",
                "episode_id": episode_id,
                "approver": body.approver,
            }
        )
        raise HTTPException(
            403, "kill switch enabled — episode stays awaiting_approval until it's off"
        )

    ep["approver"] = body.approver
    ep["approved_at"] = time.time()
    ep["status"] = "executing"
    _audit_event({"kind": "approval_granted", "episode_id": episode_id, "approver": body.approver})

    _run_bounded_loop(ep)
    return ep


@app.post("/v1/episodes/{episode_id}/deny")
def deny(episode_id: str, body: DecisionIn) -> dict[str, Any]:
    ep = _episodes.get(episode_id)
    if not ep:
        raise HTTPException(404, "episode not found")
    if ep["status"] != "awaiting_approval":
        raise HTTPException(400, f"cannot deny status={ep['status']}")
    ep["status"] = "denied"
    ep["approver"] = body.approver
    ep["denied_at"] = time.time()
    _audit_event({"kind": "episode_denied", "episode_id": episode_id, "approver": body.approver})
    return ep
