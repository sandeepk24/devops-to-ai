"""
Golden-path skeleton — Phase 06.

Keep this boring on purpose. App teams should get /health for free
and spend their brain on business logic, not Dockerfile archaeology.
"""

from fastapi import FastAPI

SERVICE_NAME = "__SERVICE_NAME__"
SERVICE_PORT = 8080

app = FastAPI(title=SERVICE_NAME, version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness — process is up."""
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/ready")
def ready() -> dict[str, str]:
    """Readiness — safe to receive traffic (extend when you add a DB)."""
    return {"status": "ready", "service": SERVICE_NAME}


@app.get("/v1/info")
def info() -> dict[str, str]:
    return {
        "service": SERVICE_NAME,
        "phase": "06",
        "path": "golden-path",
        "hint": "Scaffolded from the platform template — don't invent a new Dockerfile.",
    }
