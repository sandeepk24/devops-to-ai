"""
Gated ops agent API — Phase 08.

Path A: PLANNER_BACKEND=mock
Mutations require approval. Kill switch blocks new investigates' write proposals
and blocks approve→execute when enabled.
"""

from __future__ import annotations

import os
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from planner import mock_plan, summarize
from tools import ToolError, ToolRegistry, execute_rollback

PLANNER_BACKEND = os.getenv("PLANNER_BACKEND", "mock").strip().lower()
ALLOWED_TOOLS = {
    a.strip()
    for a in os.getenv(
        "ALLOWED_TOOLS",
        "get_service_metrics,get_recent_logs,search_runbook,propose_rollback",
    ).split(",")
    if a.strip()
}
KILL_SWITCH = os.getenv("KILL_SWITCH", "false").strip().lower() in {"1", "true", "yes", "on"}
APPROVAL_TTL_SECONDS = int(os.getenv("APPROVAL_TTL_SECONDS", "3600"))
DATA_DIR = Path(os.getenv("DATA_DIR", str(Path(__file__).resolve().parents[2] / "data")))
PORT = int(os.getenv("PORT", "8100"))

app = FastAPI(title="gated-ops-agent", version="0.1.0")

_approvals: dict[str, Any] = {}
_audit: list[dict[str, Any]] = []
_world: dict[str, Any] = {"services": {}}
_registry = ToolRegistry(ALLOWED_TOOLS, DATA_DIR)


def _audit_event(event: dict[str, Any]) -> dict[str, Any]:
    event = {**event, "ts": time.time(), "id": str(uuid.uuid4())}
    _audit.append(event)
    if len(_audit) > 500:
        del _audit[:-500]
    return event


class InvestigateIn(BaseModel):
    type: str = Field(default="high_error_rate")
    service: str = "payments-api"
    message: str = ""
    incident_id: Optional[str] = None


class ApproveIn(BaseModel):
    approver: str = "local-dev"


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "planner": PLANNER_BACKEND,
        "kill_switch": KILL_SWITCH,
        "allowed_tools": sorted(ALLOWED_TOOLS),
    }


@app.post("/v1/reset")
def reset() -> dict[str, str]:
    _approvals.clear()
    _audit.clear()
    _world["services"] = {}
    return {"status": "reset"}


@app.get("/v1/audit")
def get_audit(limit: int = 50) -> list[dict[str, Any]]:
    return list(_audit[-limit:])


@app.get("/v1/approvals")
def list_approvals() -> dict[str, Any]:
    return {"approvals": list(_approvals.values())}


@app.get("/v1/approvals/{approval_id}")
def get_approval(approval_id: str) -> dict[str, Any]:
    rec = _approvals.get(approval_id)
    if not rec:
        raise HTTPException(404, "approval not found")
    return rec


@app.get("/v1/world")
def world() -> dict[str, Any]:
    return _world


@app.post("/v1/investigate")
def investigate(body: InvestigateIn) -> dict[str, Any]:
    if PLANNER_BACKEND != "mock":
        # Path A finishes on mock; Path B is documented stretch.
        raise HTTPException(
            501,
            f"planner backend '{PLANNER_BACKEND}' not enabled in this lab build — use mock",
        )

    run_id = str(uuid.uuid4())
    incident = body.model_dump()
    incident["incident_id"] = body.incident_id or str(uuid.uuid4())

    _audit_event({"kind": "investigate_start", "run_id": run_id, "incident": incident})

    plan = mock_plan(incident)
    if KILL_SWITCH:
        plan = [s for s in plan if s["name"] != "propose_rollback"]

    ctx = {"approvals": _approvals, "world": _world, "run_id": run_id}
    tool_results: list[dict[str, Any]] = []

    for step in plan:
        name, args = step["name"], step.get("args") or {}
        try:
            result = _registry.call(name, args, ctx)
            entry = {"tool": name, "args": args, "ok": True, "result": result}
            _audit_event(
                {"kind": "tool_call", "run_id": run_id, "tool": name, "args": args, "ok": True}
            )
        except ToolError as exc:
            entry = {"tool": name, "args": args, "ok": False, "error": str(exc)}
            _audit_event(
                {
                    "kind": "tool_call",
                    "run_id": run_id,
                    "tool": name,
                    "args": args,
                    "ok": False,
                    "error": str(exc),
                }
            )
        tool_results.append(entry)

    # Attempt a disallowed tool name in audit for teaching? No — evals call API separately.

    approval_id = None
    for tr in tool_results:
        if tr.get("ok") and tr.get("tool") == "propose_rollback":
            approval_id = tr["result"].get("approval_id")

    summary = summarize(incident, tool_results)
    out = {
        "run_id": run_id,
        "incident": incident,
        "planner": PLANNER_BACKEND,
        "tool_results": tool_results,
        "approval_id": approval_id,
        "summary": summary,
        "mutation_executed": False,
    }
    _audit_event({"kind": "investigate_done", "run_id": run_id, "approval_id": approval_id})
    return out


@app.post("/v1/approvals/{approval_id}/approve")
def approve(approval_id: str, body: ApproveIn) -> dict[str, Any]:
    rec = _approvals.get(approval_id)
    if not rec:
        raise HTTPException(404, "approval not found")
    if rec["status"] != "pending":
        raise HTTPException(400, f"cannot approve status={rec['status']}")
    if time.time() - rec["created_at"] > APPROVAL_TTL_SECONDS:
        rec["status"] = "expired"
        raise HTTPException(400, "approval expired")
    if KILL_SWITCH:
        _audit_event(
            {
                "kind": "approval_blocked_kill_switch",
                "approval_id": approval_id,
                "approver": body.approver,
            }
        )
        raise HTTPException(403, "kill switch enabled — approve/execute blocked")

    rec["status"] = "approved"
    rec["approver"] = body.approver
    rec["approved_at"] = time.time()
    _audit_event(
        {
            "kind": "approval_granted",
            "approval_id": approval_id,
            "approver": body.approver,
            "action": rec["action"],
            "args": rec["args"],
        }
    )

    ctx = {"approvals": _approvals, "world": _world, "run_id": rec.get("run_id")}
    try:
        result = execute_rollback(
            {"approval_id": approval_id, "service": rec["args"]["service"]}, ctx
        )
    except ToolError as exc:
        raise HTTPException(400, str(exc)) from exc

    _audit_event(
        {
            "kind": "mutation_executed",
            "approval_id": approval_id,
            "action": "execute_rollback",
            "result": result,
        }
    )
    return {"approval": rec, "execution": result}


@app.post("/v1/approvals/{approval_id}/deny")
def deny(approval_id: str, body: ApproveIn) -> dict[str, Any]:
    rec = _approvals.get(approval_id)
    if not rec:
        raise HTTPException(404, "approval not found")
    if rec["status"] != "pending":
        raise HTTPException(400, f"cannot deny status={rec['status']}")
    rec["status"] = "denied"
    rec["approver"] = body.approver
    _audit_event(
        {"kind": "approval_denied", "approval_id": approval_id, "approver": body.approver}
    )
    return rec


@app.post("/v1/actions/execute_rollback")
def execute_rollback_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Direct mutate attempt — must include approval_id for an *approved* record.
    Used by smoke/evals to prove ungated calls fail.
    """
    ctx = {"approvals": _approvals, "world": _world, "run_id": None}
    try:
        result = execute_rollback(payload, ctx)
    except ToolError as exc:
        _audit_event(
            {
                "kind": "mutation_refused",
                "action": "execute_rollback",
                "error": str(exc),
                "payload": payload,
            }
        )
        raise HTTPException(403, str(exc)) from exc
    _audit_event({"kind": "mutation_executed", "action": "execute_rollback", "result": result})
    return result


@app.post("/v1/tools/call")
def raw_tool_call(payload: dict[str, Any]) -> dict[str, Any]:
    """Eval helper: try calling a tool by name (still allowlist-enforced)."""
    name = payload.get("name")
    args = payload.get("args") or {}
    ctx = {"approvals": _approvals, "world": _world, "run_id": "eval"}
    try:
        result = _registry.call(str(name), args, ctx)
        return {"ok": True, "result": result}
    except ToolError as exc:
        return {"ok": False, "error": str(exc)}
