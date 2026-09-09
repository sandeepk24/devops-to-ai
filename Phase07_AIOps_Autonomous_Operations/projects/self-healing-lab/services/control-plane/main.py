"""
Mock control plane — Phase 07 self-healing lab.

Pretend Kubernetes/services live here so juniors can practice
detect → decide → act → verify without a real cluster.
"""

from __future__ import annotations

import threading
import time
import uuid
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="control-plane", version="0.1.0")
_lock = threading.Lock()

# In-memory world
_services: dict[str, dict[str, Any]] = {
    "flappy": {
        "name": "flappy",
        "status": "healthy",  # healthy | crashloop | degraded
        "restarts": 0,
        "last_error": None,
    }
}
_alerts: list[dict[str, Any]] = []
_audit: list[dict[str, Any]] = []


class AlertIn(BaseModel):
    type: str = Field(description="crashloop | high_latency | ...")
    service: str = "flappy"
    severity: str = "warning"
    message: str = ""
    alert_id: Optional[str] = None


class ActionIn(BaseModel):
    action: str
    service: str
    reason: str = ""
    mode: str = "auto"  # suggest | auto
    actor: str = "healer"


class AuditIn(BaseModel):
    event: dict[str, Any]


def _now() -> float:
    return time.time()


def _append_audit(entry: dict[str, Any]) -> dict[str, Any]:
    entry = {**entry, "ts": entry.get("ts", _now()), "id": entry.get("id", str(uuid.uuid4()))}
    with _lock:
        _audit.append(entry)
        # keep last 500
        if len(_audit) > 500:
            del _audit[:-500]
    return entry


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/services")
def list_services() -> dict[str, Any]:
    with _lock:
        return {"services": list(_services.values())}


@app.get("/v1/services/{name}")
def get_service(name: str) -> dict[str, Any]:
    with _lock:
        svc = _services.get(name)
        if not svc:
            raise HTTPException(404, f"unknown service {name}")
        return dict(svc)


@app.post("/v1/alerts")
def post_alert(body: AlertIn) -> dict[str, Any]:
    alert_id = body.alert_id or str(uuid.uuid4())
    alert = {
        "alert_id": alert_id,
        "type": body.type,
        "service": body.service,
        "severity": body.severity,
        "message": body.message or f"{body.type} on {body.service}",
        "ts": _now(),
        "status": "open",
    }
    with _lock:
        if body.service not in _services:
            raise HTTPException(404, f"unknown service {body.service}")
        # Reflect world state for crashloop so verify is meaningful
        if body.type == "crashloop":
            _services[body.service]["status"] = "crashloop"
            _services[body.service]["last_error"] = alert["message"]
        elif body.type == "high_latency":
            _services[body.service]["status"] = "degraded"
            _services[body.service]["last_error"] = alert["message"]
        _alerts.append(alert)
    _append_audit(
        {
            "kind": "alert_received",
            "alert_id": alert_id,
            "type": body.type,
            "service": body.service,
            "message": alert["message"],
        }
    )
    return alert


@app.get("/v1/alerts")
def list_alerts(status: str = "open") -> dict[str, Any]:
    with _lock:
        items = [a for a in _alerts if status == "all" or a.get("status") == status]
        return {"alerts": items}


@app.post("/v1/alerts/{alert_id}/ack")
def ack_alert(alert_id: str) -> dict[str, str]:
    with _lock:
        for a in _alerts:
            if a["alert_id"] == alert_id:
                a["status"] = "acked"
                return {"status": "acked"}
    raise HTTPException(404, "alert not found")


@app.post("/v1/actions/restart")
def restart_service(body: ActionIn) -> dict[str, Any]:
    if body.action != "restart_service":
        raise HTTPException(400, "this endpoint only supports restart_service")
    with _lock:
        svc = _services.get(body.service)
        if not svc:
            raise HTTPException(404, f"unknown service {body.service}")
        svc["restarts"] = int(svc.get("restarts", 0)) + 1
        svc["status"] = "healthy"
        svc["last_error"] = None
        result = {
            "ok": True,
            "service": body.service,
            "restarts": svc["restarts"],
            "status": svc["status"],
        }
    _append_audit(
        {
            "kind": "action_executed",
            "action": "restart_service",
            "service": body.service,
            "mode": body.mode,
            "actor": body.actor,
            "reason": body.reason,
            "result": result,
        }
    )
    return result


@app.post("/v1/audit")
def post_audit(body: AuditIn) -> dict[str, Any]:
    return _append_audit(body.event)


@app.get("/v1/audit")
def get_audit(limit: int = 50) -> list[dict[str, Any]]:
    with _lock:
        return list(_audit[-limit:])


@app.post("/v1/reset")
def reset_world() -> dict[str, str]:
    """Test helper — clean slate for smoke tests."""
    global _alerts, _audit
    with _lock:
        _services.clear()
        _services["flappy"] = {
            "name": "flappy",
            "status": "healthy",
            "restarts": 0,
            "last_error": None,
        }
        _alerts = []
        _audit = []
    return {"status": "reset"}
