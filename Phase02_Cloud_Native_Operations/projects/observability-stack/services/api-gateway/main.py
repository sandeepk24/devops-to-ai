"""
api-gateway — Phase 02 capstone starter service.

Receives incoming requests and fans out to payments-service and user-service.
Instrumented with:
  - Prometheus metrics (/metrics endpoint on port 8001)
  - OpenTelemetry tracing (sent to OTel Collector)
  - Structured JSON logging

Usage:
    pip install -r requirements.txt
    uvicorn main:app --host 0.0.0.0 --port 8000
"""

import logging
import os
import random
import time
from datetime import datetime

import httpx
import structlog
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# ── configuration ──────────────────────────────────────────────────────────────
PAYMENTS_SERVICE_URL = os.getenv("PAYMENTS_SERVICE_URL", "http://payments-service:8000")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
SERVICE_NAME = "api-gateway"
PORT = int(os.getenv("PORT", "8000"))

# ── structured logging ─────────────────────────────────────────────────────────
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

# ── opentelemetry setup ────────────────────────────────────────────────────────
resource = Resource.create({"service.name": SERVICE_NAME})
provider = TracerProvider(resource=resource)
exporter = OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(SERVICE_NAME)

# ── prometheus metrics ─────────────────────────────────────────────────────────
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)
ACTIVE_REQUESTS = Gauge(
    "http_requests_active",
    "Currently active HTTP requests",
)

# ── app ────────────────────────────────────────────────────────────────────────
app = FastAPI(title=SERVICE_NAME)

FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track request count, duration, and active requests for every endpoint."""
    if request.url.path in ("/metrics", "/health", "/ready"):
        return await call_next(request)

    start = time.time()
    ACTIVE_REQUESTS.inc()

    try:
        response = await call_next(request)
        duration = time.time() - start
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path,
        ).observe(duration)
        log.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )
        return response
    except Exception as e:
        duration = time.time() - start
        REQUEST_COUNT.labels(
            method=request.method, endpoint=request.url.path, status=500
        ).inc()
        log.error("request_failed", path=request.url.path, error=str(e), duration_ms=round(duration * 1000, 2))
        return JSONResponse(status_code=500, content={"error": "internal server error"})
    finally:
        ACTIVE_REQUESTS.dec()


@app.get("/health")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME, "timestamp": datetime.utcnow().isoformat()}


@app.get("/ready")
async def ready():
    # TODO: add actual readiness checks (e.g. can we reach downstream services?)
    return {"status": "ready"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/checkout")
async def checkout(user_id: str, amount: float):
    """
    Main checkout endpoint — calls user-service to validate user,
    then payments-service to process payment.
    Demonstrates distributed tracing across services.
    """
    with tracer.start_as_current_span("checkout") as span:
        span.set_attribute("user.id", user_id)
        span.set_attribute("checkout.amount", amount)

        log.info("checkout_started", user_id=user_id, amount=amount)

        async with httpx.AsyncClient() as client:
            # Step 1: validate user
            with tracer.start_as_current_span("validate_user"):
                user_response = await client.get(
                    f"{USER_SERVICE_URL}/users/{user_id}",
                    timeout=5.0,
                )
                if user_response.status_code != 200:
                    log.error("user_not_found", user_id=user_id)
                    span.set_attribute("checkout.status", "user_not_found")
                    return JSONResponse(status_code=404, content={"error": "user not found"})

            # Step 2: process payment
            with tracer.start_as_current_span("process_payment"):
                payment_response = await client.post(
                    f"{PAYMENTS_SERVICE_URL}/payments",
                    json={"user_id": user_id, "amount": amount},
                    timeout=10.0,
                )
                if payment_response.status_code != 200:
                    log.error("payment_failed", user_id=user_id, amount=amount)
                    span.set_attribute("checkout.status", "payment_failed")
                    return JSONResponse(status_code=502, content={"error": "payment failed"})

        result = payment_response.json()
        log.info("checkout_completed", user_id=user_id, amount=amount, payment_id=result.get("payment_id"))
        span.set_attribute("checkout.status", "success")
        span.set_attribute("payment.id", result.get("payment_id", ""))
        return {"status": "success", "payment_id": result.get("payment_id")}


# TODO: add more endpoints for your own practice
# Suggestions:
#   GET /orders/{order_id}    — fetch order details
#   GET /users/{user_id}/orders — list user's orders
#   POST /refund              — process a refund


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
