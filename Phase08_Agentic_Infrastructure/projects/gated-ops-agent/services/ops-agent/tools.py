"""
Allowlisted tools for the Phase 08 gated ops agent.

Write tools never run just because a planner asked — execute_rollback
requires a valid approval_id from the approval store.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
# In Docker, DATA_DIR is overridden via env in main.


ToolFn = Callable[..., dict[str, Any]]


class ToolError(Exception):
    pass


class ToolRegistry:
    def __init__(self, allowed: set[str], data_dir: Path) -> None:
        self.allowed = allowed
        self.data_dir = data_dir
        self._fns: dict[str, ToolFn] = {
            "get_service_metrics": self.get_service_metrics,
            "get_recent_logs": self.get_recent_logs,
            "search_runbook": self.search_runbook,
            "propose_rollback": self.propose_rollback,
        }

    def call(self, name: str, args: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        if name not in self.allowed:
            raise ToolError(f"tool not allowlisted: {name}")
        if name not in self._fns:
            raise ToolError(f"unknown tool: {name}")
        return self._fns[name](args, ctx)

    def get_service_metrics(self, args: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        service = args.get("service")
        if not service:
            raise ToolError("service required")
        raw = json.loads((self.data_dir / "metrics.json").read_text(encoding="utf-8"))
        if service not in raw:
            raise ToolError(f"no metrics for {service}")
        return {"service": service, "metrics": raw[service]}

    def get_recent_logs(self, args: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        service = args.get("service")
        limit = int(args.get("limit", 20))
        if not service:
            raise ToolError("service required")
        lines: list[dict[str, Any]] = []
        path = self.data_dir / "logs.jsonl"
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if row.get("service") == service:
                    lines.append(row)
        return {"service": service, "logs": lines[-limit:]}

    def search_runbook(self, args: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        query = (args.get("query") or "").lower()
        hits: list[dict[str, str]] = []
        rb = self.data_dir / "runbooks"
        for path in sorted(rb.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            if query in text.lower() or query in path.name.lower() or not query:
                hits.append({"path": path.name, "excerpt": text[:600]})
        return {"query": query, "hits": hits[:3]}

    def propose_rollback(self, args: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        """Creates a pending approval — does not mutate."""
        service = args.get("service")
        reason = args.get("reason") or "agent proposed rollback"
        if not service:
            raise ToolError("service required")
        approvals: dict[str, Any] = ctx["approvals"]
        approval_id = f"apr-{int(time.time() * 1000)}"
        approvals[approval_id] = {
            "id": approval_id,
            "action": "execute_rollback",
            "args": {"service": service},
            "reason": reason,
            "status": "pending",
            "created_at": time.time(),
            "run_id": ctx.get("run_id"),
        }
        return {
            "status": "pending_approval",
            "approval_id": approval_id,
            "action": "execute_rollback",
            "service": service,
            "message": "Rollback proposed. Human must approve before execute.",
        }


def execute_rollback(args: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    """
    Mutating tool — not on the planner allowlist.
    Only callable via approval flow with a valid approval_id.
    """
    approval_id = args.get("approval_id")
    service = args.get("service")
    approvals: dict[str, Any] = ctx["approvals"]
    world: dict[str, Any] = ctx["world"]

    if not approval_id:
        raise ToolError("approval_id required for execute_rollback")
    rec = approvals.get(approval_id)
    if not rec:
        raise ToolError("unknown approval_id")
    if rec["status"] != "approved":
        raise ToolError(f"approval not approved (status={rec['status']})")
    if rec["action"] != "execute_rollback":
        raise ToolError("approval action mismatch")
    if service and service != rec["args"].get("service"):
        raise ToolError("service does not match approval snapshot")

    target = rec["args"]["service"]
    world.setdefault("services", {})
    world["services"][target] = {
        "version": "previous",
        "last_action": "rollback",
        "rolled_back_at": time.time(),
        "status": "healthy",
    }
    rec["status"] = "executed"
    return {
        "ok": True,
        "service": target,
        "version": "previous",
        "verified": True,
        "message": f"Rolled back {target} to previous version (mock).",
    }
