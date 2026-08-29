# Multi-stage production-ish image for the Phase 01 API.
# Read the comments — this is the pattern you'll reuse everywhere.

FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

# Non-root user (required for the capstone)
RUN useradd --create-home --uid 10001 appuser

COPY --from=builder /install /usr/local
COPY app ./app

USER appuser
EXPOSE 8080

# Stretch: add a real HEALTHCHECK instruction
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
