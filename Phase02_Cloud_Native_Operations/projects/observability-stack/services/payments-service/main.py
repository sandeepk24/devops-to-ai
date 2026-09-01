"""
payments-service — Phase 02 capstone.

TODO for learners:
- Extend readiness to check downstream deps if you add any
- Add custom business metrics (e.g. payments_processed_total)
- Tune slow/error percentages for demo alerts
"""

from __future__ import annotations

import os
import random
import time
import uuid
from datetime import datetime

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
from pydantic import BaseModel, Field

SERVICE_NAME = "payments-service"
OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
SLOW_RATE = float(os.getenv("SLOW_RATE", "0.10"))
ERROR_RATE = float(os.getenv("ERROR_RATE", "0.02"))

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
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

app = FastAPI(title=SERVICE_NAME)
FastAPIInstrumentor.instrument_app(app)

_PAYMENTS: dict[str, dict] = {}


class PaymentCreate(BaseModel):
    user_id: str = Field(min_length=1)
    amount: float = Field(gt=0)


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


@app.post("/payments")
def create_payment(body: PaymentCreate):
    with tracer.start_as_current_span("create_payment") as span:
        span.set_attribute("user.id", body.user_id)
        span.set_attribute("payment.amount", body.amount)

        roll = random.random()
        if roll < ERROR_RATE:
            log.error("payment_failed", user_id=body.user_id, amount=body.amount, reason="simulated")
            raise HTTPException(status_code=500, detail="simulated payment processor error")

        if roll < ERROR_RATE + SLOW_RATE:
            delay = random.uniform(2.0, 5.0)
            log.warning("payment_slow_path", user_id=body.user_id, delay_s=round(delay, 2))
            time.sleep(delay)

        payment_id = str(uuid.uuid4())
        record = {
            "payment_id": payment_id,
            "user_id": body.user_id,
            "amount": body.amount,
            "status": "captured",
            "created_at": datetime.utcnow().isoformat(),
        }
        _PAYMENTS[payment_id] = record
        log.info("payment_captured", **record)
        span.set_attribute("payment.id", payment_id)
        return record


@app.get("/payments/{payment_id}")
def get_payment(payment_id: str):
    payment = _PAYMENTS.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="payment not found")
    return payment


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
