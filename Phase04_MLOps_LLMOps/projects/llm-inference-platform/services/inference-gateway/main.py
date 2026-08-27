"""
inference-gateway — Phase 04 capstone.

OpenAI-compatible front door for model serving:
  - API key auth
  - per-key rate limiting
  - proxy to stable / canary upstreams
  - Prometheus metrics

Usage:
    pip install -r requirements.txt
    uvicorn main:app --host 0.0.0.0 --port 8080
"""

import os
import time
from collections import defaultdict, deque
from typing import Any, Optional

import httpx
import structlog
from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

# ── configuration ──────────────────────────────────────────────────────────────
INFERENCE_URL = os.getenv("INFERENCE_URL", "http://mock-inference:8000").rstrip("/")
CANARY_INFERENCE_URL = os.getenv("CANARY_INFERENCE_URL", INFERENCE_URL).rstrip("/")
API_KEYS = {k.strip() for k in os.getenv("API_KEYS", "dev-key").split(",") if k.strip()}
RATE_LIMIT_RPM = int(os.getenv("RATE_LIMIT_RPM", "60"))
CANARY_PERCENT = int(os.getenv("CANARY_PERCENT", "10"))
PORT = int(os.getenv("PORT", "8080"))
UPSTREAM_TIMEOUT = float(os.getenv("UPSTREAM_TIMEOUT", "60"))

# ── logging ────────────────────────────────────────────────────────────────────
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

# ── metrics ────────────────────────────────────────────────────────────────────
REQUEST_COUNT = Counter(
    "llm_gateway_requests_total",
    "Total gateway requests",
    ["endpoint", "status", "upstream"],
)
REQUEST_LATENCY = Histogram(
    "llm_gateway_request_duration_seconds",
    "End-to-end gateway latency",
    ["endpoint", "upstream"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)
TOKEN_COUNT = Counter(
    "llm_gateway_tokens_total",
    "Tokens reported by upstream usage blocks",
    ["type", "upstream"],
)
RATE_LIMIT_HITS = Counter(
    "llm_gateway_rate_limit_hits_total",
    "Requests rejected by rate limiting",
    ["api_key_suffix"],
)
UPSTREAM_UP = Gauge(
    "llm_gateway_upstream_up",
    "1 if upstream health check succeeds",
    ["upstream"],
)

# ── rate limiter (in-memory sliding window) ────────────────────────────────────
_windows: dict[str, deque[float]] = defaultdict(deque)


def _check_rate_limit(api_key: str) -> None:
    """
    Reject with 429 when a key exceeds RATE_LIMIT_RPM.

    TODO (stretch): replace in-memory windows with Redis so limits work
    across multiple gateway replicas.
    """
    now = time.time()
    window = _windows[api_key]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= RATE_LIMIT_RPM:
        RATE_LIMIT_HITS.labels(api_key_suffix=api_key[-4:]).inc()
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    window.append(now)


def _extract_api_key(authorization: Optional[str]) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return token


def _pick_upstream(model_version: Optional[str], api_key: str) -> tuple[str, str]:
    """
    Return (upstream_url, upstream_label).

    Explicit header wins; otherwise send CANARY_PERCENT of traffic to canary
    using a stable hash of the API key so a given key sticks to one pool.
    """
    if model_version and model_version.lower() == "canary":
        return CANARY_INFERENCE_URL, "canary"
    if model_version and model_version.lower() == "stable":
        return INFERENCE_URL, "stable"

    # Deterministic percentage split without extra dependencies.
    bucket = sum(ord(c) for c in api_key) % 100
    if bucket < CANARY_PERCENT and CANARY_INFERENCE_URL != INFERENCE_URL:
        return CANARY_INFERENCE_URL, "canary"
    return INFERENCE_URL, "stable"


app = FastAPI(title="inference-gateway", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> JSONResponse:
    """Ready only when the stable upstream answers /health."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{INFERENCE_URL}/health")
            ok = resp.status_code == 200
    except Exception:
        ok = False

    UPSTREAM_UP.labels(upstream="stable").set(1 if ok else 0)
    if not ok:
        return JSONResponse({"status": "not_ready", "upstream": INFERENCE_URL}, status_code=503)
    return JSONResponse({"status": "ready"})


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/chat/completions")
async def chat_completions(
    request: Request,
    authorization: Optional[str] = Header(default=None),
    x_model_version: Optional[str] = Header(default=None, alias="X-Model-Version"),
) -> JSONResponse:
    api_key = _extract_api_key(authorization)
    _check_rate_limit(api_key)

    try:
        payload: dict[str, Any] = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON body") from exc

    upstream_url, upstream_label = _pick_upstream(x_model_version, api_key)
    started = time.time()
    status_code = 500

    try:
        async with httpx.AsyncClient(timeout=UPSTREAM_TIMEOUT) as client:
            upstream = await client.post(
                f"{upstream_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
        status_code = upstream.status_code
        body = upstream.json()

        usage = body.get("usage") or {}
        if "prompt_tokens" in usage:
            TOKEN_COUNT.labels(type="prompt", upstream=upstream_label).inc(usage["prompt_tokens"])
        if "completion_tokens" in usage:
            TOKEN_COUNT.labels(type="completion", upstream=upstream_label).inc(
                usage["completion_tokens"]
            )

        log.info(
            "chat_completion",
            upstream=upstream_label,
            status=status_code,
            model=payload.get("model"),
            # Never log the raw Authorization header.
            api_key_suffix=api_key[-4:],
        )
        return JSONResponse(body, status_code=status_code)

    except httpx.RequestError as exc:
        status_code = 502
        log.error("upstream_unreachable", upstream=upstream_label, error=str(exc))
        return JSONResponse(
            {"error": {"message": f"Upstream unreachable: {upstream_label}", "type": "gateway_error"}},
            status_code=502,
        )
    finally:
        REQUEST_COUNT.labels(
            endpoint="/v1/chat/completions",
            status=str(status_code),
            upstream=upstream_label,
        ).inc()
        REQUEST_LATENCY.labels(
            endpoint="/v1/chat/completions",
            upstream=upstream_label,
        ).observe(time.time() - started)
