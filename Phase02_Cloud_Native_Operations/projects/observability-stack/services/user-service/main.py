"""
user-service — Phase 02 capstone.

Ten hardcoded users — no database on purpose. Focus on observability, not CRUD.
"""

from __future__ import annotations

import os
import time

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

SERVICE_NAME = "user-service"
OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")

USERS = {
    f"user-{i}": {"user_id": f"user-{i}", "name": f"Test User {i}", "email": f"user{i}@example.com"}
    for i in range(1, 11)
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

resource = Resource.create({"service.name": SERVICE_NAME})
provider = TracerProvider(resource=resource)
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True))
)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(SERVICE_NAME)

REQUEST_COUNT = Counter("http_requests_total", "HTTP requests", ["method", "endpoint", "status"])
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP latency",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)

app = FastAPI(title=SERVICE_NAME)
FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    if request.url.path in ("/metrics", "/health", "/ready"):
        return await call_next(request)
    start = time.time()
    response = await call_next(request)
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    REQUEST_DURATION.labels(request.method, request.url.path).observe(time.time() - start)
    return response


@app.get("/health")
def health():
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/users/{user_id}")
def get_user(user_id: str):
    with tracer.start_as_current_span("get_user") as span:
        span.set_attribute("user.id", user_id)
        user = USERS.get(user_id)
        if not user:
            log.warning("user_not_found", user_id=user_id)
            raise HTTPException(status_code=404, detail="user not found")
        log.info("user_lookup", user_id=user_id)
        return user


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
