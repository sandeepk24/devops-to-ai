"""
Healer — Phase 07 self-healing lab.

Polls open alerts from the control plane and applies policy:
  suggest → audit only
  auto    → allowlisted actions, unless kill switch / cooldown says no
"""

from __future__ import annotations

import os
import threading
import time
from collections import defaultdict, deque
from typing import Any

import httpx
import structlog
from fastapi import FastAPI

CONTROL_PLANE_URL = os.getenv("CONTROL_PLANE_URL", "http://control-plane:8090").rstrip("/")
HEALER_MODE = os.getenv("HEALER_MODE", "suggest").strip().lower()  # suggest | auto
KILL_SWITCH = os.getenv("KILL_SWITCH", "false").strip().lower() in {"1", "true", "yes", "on"}
ALLOWED_ACTIONS = {
    a.strip() for a in os.getenv("ALLOWED_ACTIONS", "restart_service").split(",") if a.strip()
}
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "15"))
MAX_RESTARTS_PER_HOUR = int(os.getenv("MAX_RESTARTS_PER_HOUR", "5"))
POLL_SECONDS = float(os.getenv("POLL_SECONDS", "2"))
PORT = int(os.getenv("PORT", "8091"))

# Map alert types → proposed action (None = detect only / page human)
ALERT_POLICY: dict[str, str | None] = {
    "crashloop": "restart_service",
    "high_latency": None,  # suggest-only narrative: do not auto-restart for latency
}

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)
log = structlog.get_logger()

app = FastAPI(title="healer", version="0.1.0")

_seen: set[str] = set()
_last_action_at: dict[str, float] = {}
_restart_times: dict[str, deque[float]] = defaultdict(deque)
_stop = threading.Event()


def _audit(event: dict[str, Any]) -> None:
    try:
        httpx.post(f"{CONTROL_PLANE_URL}/v1/audit", json={"event": event}, timeout=5.0)
    except Exception as exc:  # noqa: BLE001 — lab: never crash the loop on audit fail
        log.warning("audit_failed", error=str(exc))


def _cooldown_ok(service: str) -> bool:
    last = _last_action_at.get(service, 0.0)
    return (time.time() - last) >= COOLDOWN_SECONDS


def _rate_ok(service: str) -> bool:
    q = _restart_times[service]
    cutoff = time.time() - 3600
    while q and q[0] < cutoff:
        q.popleft()
    return len(q) < MAX_RESTARTS_PER_HOUR


def _mark_action(service: str) -> None:
    now = time.time()
    _last_action_at[service] = now
    _restart_times[service].append(now)


def _verify(service: str) -> bool:
    r = httpx.get(f"{CONTROL_PLANE_URL}/v1/services/{service}", timeout=5.0)
    r.raise_for_status()
    return r.json().get("status") == "healthy"


def handle_alert(alert: dict[str, Any]) -> None:
    alert_id = alert["alert_id"]
    if alert_id in _seen:
        return
    _seen.add(alert_id)

    alert_type = alert.get("type", "")
    service = alert.get("service", "flappy")
    action = ALERT_POLICY.get(alert_type)

    decision = {
        "kind": "decision",
        "alert_id": alert_id,
        "alert_type": alert_type,
        "service": service,
        "mode": HEALER_MODE,
        "kill_switch": KILL_SWITCH,
        "proposed_action": action,
    }

    if action is None:
        decision["outcome"] = "suggest_only_no_safe_action"
        decision["message"] = "No allowlisted auto action for this alert — page a human."
        _audit(decision)
        httpx.post(f"{CONTROL_PLANE_URL}/v1/alerts/{alert_id}/ack", timeout=5.0)
        return

    if action not in ALLOWED_ACTIONS:
        decision["outcome"] = "skipped_not_allowlisted"
        _audit(decision)
        httpx.post(f"{CONTROL_PLANE_URL}/v1/alerts/{alert_id}/ack", timeout=5.0)
        return

    if KILL_SWITCH:
        decision["outcome"] = "skipped_kill_switch"
        _audit(decision)
        httpx.post(f"{CONTROL_PLANE_URL}/v1/alerts/{alert_id}/ack", timeout=5.0)
        return

    if not _cooldown_ok(service):
        decision["outcome"] = "skipped_cooldown"
        _audit(decision)
        httpx.post(f"{CONTROL_PLANE_URL}/v1/alerts/{alert_id}/ack", timeout=5.0)
        return

    if not _rate_ok(service):
        decision["outcome"] = "skipped_rate_limit"
        _audit(decision)
        httpx.post(f"{CONTROL_PLANE_URL}/v1/alerts/{alert_id}/ack", timeout=5.0)
        return

    if HEALER_MODE != "auto":
        decision["outcome"] = "suggest"
        decision["message"] = f"Would run {action} on {service} (suggest mode)."
        _audit(decision)
        httpx.post(f"{CONTROL_PLANE_URL}/v1/alerts/{alert_id}/ack", timeout=5.0)
        return

    # AUTO path
    decision["outcome"] = "auto_executing"
    _audit(decision)
    resp = httpx.post(
        f"{CONTROL_PLANE_URL}/v1/actions/restart",
        json={
            "action": action,
            "service": service,
            "reason": f"alert:{alert_id}:{alert_type}",
            "mode": "auto",
            "actor": "healer/0.1.0",
        },
        timeout=10.0,
    )
    resp.raise_for_status()
    _mark_action(service)

    ok = _verify(service)
    _audit(
        {
            "kind": "verify",
            "alert_id": alert_id,
            "service": service,
            "action": action,
            "verified_healthy": ok,
        }
    )
    httpx.post(f"{CONTROL_PLANE_URL}/v1/alerts/{alert_id}/ack", timeout=5.0)


def poll_loop() -> None:
    log.info(
        "healer_started",
        mode=HEALER_MODE,
        kill_switch=KILL_SWITCH,
        allowed=sorted(ALLOWED_ACTIONS),
    )
    while not _stop.is_set():
        try:
            r = httpx.get(f"{CONTROL_PLANE_URL}/v1/alerts?status=open", timeout=5.0)
            r.raise_for_status()
            for alert in r.json().get("alerts", []):
                try:
                    handle_alert(alert)
                except Exception as exc:  # noqa: BLE001
                    log.error("handle_alert_failed", error=str(exc), alert=alert)
                    _audit(
                        {
                            "kind": "error",
                            "message": str(exc),
                            "alert_id": alert.get("alert_id"),
                        }
                    )
        except Exception as exc:  # noqa: BLE001
            log.warning("poll_failed", error=str(exc))
        _stop.wait(POLL_SECONDS)


@app.on_event("startup")
def _startup() -> None:
    t = threading.Thread(target=poll_loop, name="healer-poll", daemon=True)
    t.start()


@app.on_event("shutdown")
def _shutdown() -> None:
    _stop.set()


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "mode": HEALER_MODE,
        "kill_switch": KILL_SWITCH,
        "allowed_actions": sorted(ALLOWED_ACTIONS),
    }


@app.get("/v1/config")
def config() -> dict[str, Any]:
    return health()
