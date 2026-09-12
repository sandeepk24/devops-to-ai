"""
Mock infrastructure world for the Phase 09 intent-ops-platform.

There's no real cluster underneath this. `data/services.json` seeds a
handful of pretend services, each with a `cause` for whatever's currently
wrong with it. The two mutating actions below are the *only* way the world
changes — and both are only ever called from inside the orchestrator's
approved-episode execution loop, never directly from the API.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class WorldError(Exception):
    pass


class World:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self._services: dict[str, Any] = {}
        self.reset()

    def reset(self) -> None:
        """Reload every service from data/services.json to its starting state."""
        raw = json.loads((self.data_dir / "services.json").read_text(encoding="utf-8"))
        services: dict[str, Any] = {}
        for name, svc in raw.items():
            error_rate = float(svc["error_rate"])
            replicas = int(svc["replicas"])
            services[name] = {
                "replicas": replicas,
                "version": svc.get("version", "v1"),
                "error_rate": error_rate,
                "baseline_error_rate": float(svc.get("baseline_error_rate", error_rate)),
                "cause": svc.get("cause", "unknown"),
                # Load stays constant for a given incident: error_rate * replicas.
                # scale_replicas redistributes it; rollback ignores it entirely.
                "overload_k": round(error_rate * replicas, 6),
                "last_action": None,
            }
        self._services = services

    def snapshot(self) -> dict[str, Any]:
        """A cheap deep copy — callers can't mutate world state by editing this."""
        return json.loads(json.dumps(self._services))

    def get(self, service: str) -> dict[str, Any]:
        if service not in self._services:
            raise WorldError(f"unknown service: {service}")
        return dict(self._services[service])

    def exists(self, service: str) -> bool:
        return service in self._services

    def rollback(self, service: str) -> dict[str, Any]:
        """Bad-deploy fix: back to the previous version, error rate back to baseline."""
        if service not in self._services:
            raise WorldError(f"unknown service: {service}")
        svc = self._services[service]
        svc["version"] = "previous"
        svc["error_rate"] = svc["baseline_error_rate"]
        svc["last_action"] = "rollback"
        return dict(svc)

    def scale_replicas(self, service: str, replicas: int) -> dict[str, Any]:
        """Overload fix: more replicas spread the same load, error rate drops with it."""
        if service not in self._services:
            raise WorldError(f"unknown service: {service}")
        if not isinstance(replicas, int) or replicas <= 0:
            raise WorldError("replicas must be a positive integer")
        svc = self._services[service]
        svc["replicas"] = replicas
        if svc["overload_k"]:
            new_rate = svc["overload_k"] / replicas
        else:
            new_rate = svc["error_rate"]
        svc["error_rate"] = max(round(new_rate, 6), svc["baseline_error_rate"])
        svc["last_action"] = "scale_replicas"
        return dict(svc)
