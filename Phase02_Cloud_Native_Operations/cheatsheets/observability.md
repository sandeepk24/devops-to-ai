# Observability cheatsheet

PromQL, LogQL, and the patterns you'll use every day running production systems.

---

## The golden signals — always instrument these first

| Signal | What it measures | Prometheus metric type |
|---|---|---|
| Latency | How long requests take | Histogram |
| Traffic | Request volume | Counter |
| Errors | Failure rate | Counter |
| Saturation | How full/loaded the system is | Gauge |

---

## PromQL — Prometheus query language

### Selectors

```promql
# Select a metric
http_requests_total

# Filter by label (exact match)
http_requests_total{job="api-gateway"}

# Filter by multiple labels
http_requests_total{job="api-gateway", status="200"}

# Regex match — status codes starting with 5
http_requests_total{status=~"5.."}

# Regex NOT match — everything except 2xx
http_requests_total{status!~"2.."}
```

### Rate and increase

```promql
# Rate — per-second average over a time window (use for counters)
rate(http_requests_total[5m])

# irate — instantaneous rate, last two data points (spikier, more responsive)
irate(http_requests_total[1m])

# increase — total increase over a window (rate * duration)
increase(http_requests_total[1h])

# Rule of thumb:
# rate() for dashboards and alerts (smoothed)
# irate() when you need to detect short spikes
```

### Aggregation

```promql
# Sum across all instances
sum(rate(http_requests_total[5m]))

# Sum, grouped by job
sum by (job) (rate(http_requests_total[5m]))

# Sum, grouped by status code
sum by (status) (rate(http_requests_total[5m]))

# Average
avg(rate(http_requests_total[5m]))

# Maximum across all instances
max(rate(http_requests_total[5m]))

# Count of time series
count(up{job="api-gateway"})
```

### The four golden signal queries

```promql
# ── Traffic ──────────────────────────────────────────────────────────────────
# Requests per second (all status codes)
sum(rate(http_requests_total{job="your-service"}[5m]))

# ── Errors ────────────────────────────────────────────────────────────────────
# Error rate as a percentage
sum(rate(http_requests_total{job="your-service", status=~"5.."}[5m]))
  /
sum(rate(http_requests_total{job="your-service"}[5m]))
  * 100

# ── Latency ───────────────────────────────────────────────────────────────────
# p50 (median) latency
histogram_quantile(0.50,
  sum by (le) (
    rate(http_request_duration_seconds_bucket{job="your-service"}[5m])
  )
)

# p95 latency
histogram_quantile(0.95,
  sum by (le) (
    rate(http_request_duration_seconds_bucket{job="your-service"}[5m])
  )
)

# p99 latency
histogram_quantile(0.99,
  sum by (le) (
    rate(http_request_duration_seconds_bucket{job="your-service"}[5m])
  )
)

# ── Saturation ────────────────────────────────────────────────────────────────
# CPU usage per pod (%)
rate(container_cpu_usage_seconds_total{container="your-container"}[5m]) * 100

# Memory usage per pod (%)
container_memory_working_set_bytes{container="your-container"}
  /
container_spec_memory_limit_bytes{container="your-container"}
  * 100
```

### Infrastructure queries

```promql
# ── Node metrics (requires node_exporter) ────────────────────────────────────

# Node CPU usage (%)
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Node memory usage (%)
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)
  / node_memory_MemTotal_bytes * 100

# Node disk usage per mount (%)
(node_filesystem_size_bytes - node_filesystem_avail_bytes)
  / node_filesystem_size_bytes * 100

# Node disk I/O read rate (bytes/s)
rate(node_disk_read_bytes_total[5m])

# Node network receive rate (bytes/s)
rate(node_network_receive_bytes_total{device!="lo"}[5m])

# ── Kubernetes metrics (requires kube-state-metrics) ─────────────────────────

# Pods not in running state
kube_pod_status_phase{phase!="Running", phase!="Succeeded"}

# Deployments with unavailable replicas
kube_deployment_status_replicas_unavailable > 0

# Pods in CrashLoopBackOff
kube_pod_container_status_waiting_reason{reason="CrashLoopBackOff"}

# OOMKilled containers in the last hour
increase(kube_pod_container_status_restarts_total[1h]) > 0
  and on (pod, container)
  kube_pod_container_status_last_terminated_reason{reason="OOMKilled"}

# Persistent volume capacity remaining (%)
kubelet_volume_stats_available_bytes / kubelet_volume_stats_capacity_bytes * 100
```

### SLO and error budget queries

```promql
# ── SLO: 99.5% of requests succeed in <500ms ────────────────────────────────

# Good requests (2xx and under 500ms)
sum(rate(http_request_duration_seconds_bucket{
  job="payments-service",
  status=~"2..",
  le="0.5"
}[5m]))

# Total requests
sum(rate(http_requests_total{job="payments-service"}[5m]))

# Current SLO compliance (%)
sum(rate(http_request_duration_seconds_bucket{job="payments-service", le="0.5", status=~"2.."}[30d]))
  /
sum(rate(http_requests_total{job="payments-service"}[30d]))
  * 100

# Error budget remaining (%)
# SLO target is 99.5% → error budget is 0.5%
(
  sum(rate(http_requests_total{job="payments-service", status=~"5.."}[30d]))
    /
  sum(rate(http_requests_total{job="payments-service"}[30d]))
)
  / 0.005  # error budget fraction
  * 100

# Burn rate (how fast you're consuming the error budget)
# >1 = burning faster than allowed
# >14.4 = will exhaust budget in 1 hour
sum(rate(http_requests_total{job="payments-service", status=~"5.."}[1h]))
  /
sum(rate(http_requests_total{job="payments-service"}[1h]))
  / 0.005
```

### Alert rules

```yaml
# prometheus-alerts.yaml
groups:
  - name: service-alerts
    rules:

      # High error rate — fires immediately
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) by (job)
            /
          sum(rate(http_requests_total[5m])) by (job)
          > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.job }}"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"

      # High latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.99,
            sum by (le, job) (rate(http_request_duration_seconds_bucket[5m]))
          ) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High p99 latency on {{ $labels.job }}"
          description: "p99 latency is {{ $value | humanizeDuration }} (threshold: 2s)"

      # CrashLoopBackOff
      - alert: PodCrashLooping
        expr: kube_pod_container_status_waiting_reason{reason="CrashLoopBackOff"} == 1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pod {{ $labels.pod }} is crash looping"

      # Disk space warning
      - alert: DiskSpaceLow
        expr: |
          (node_filesystem_size_bytes - node_filesystem_avail_bytes)
            / node_filesystem_size_bytes * 100 > 85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Disk space low on {{ $labels.instance }}"
          description: "{{ $labels.mountpoint }} is {{ $value | humanize }}% full"

      # Error budget burn rate — critical (exhausts in 1 hour)
      - alert: ErrorBudgetBurnRateCritical
        expr: |
          sum(rate(http_requests_total{job="payments-service", status=~"5.."}[1h]))
            /
          sum(rate(http_requests_total{job="payments-service"}[1h]))
            / 0.005 > 14.4
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Error budget burning too fast — payments-service"
          description: "At current rate, error budget will be exhausted in under 1 hour"
```

---

## LogQL — Loki query language

### Basic queries

```logql
# All logs from a service (label selector — always required)
{app="payments-service"}

# Filter by namespace
{namespace="production", app="payments-service"}

# All logs from a node
{node="worker-01"}

# Text filter — lines containing "error"
{app="payments-service"} |= "error"

# Text filter — lines NOT containing "healthcheck"
{app="payments-service"} != "healthcheck"

# Regex filter
{app="payments-service"} |~ "error|fatal|panic"

# Case-insensitive
{app="payments-service"} |~ "(?i)error"
```

### JSON parsing

```logql
# Parse JSON log entries
{app="payments-service"} | json

# Parse and filter by extracted field
{app="payments-service"} | json | level="error"

# Parse and filter by numeric field
{app="payments-service"} | json | duration_ms > 1000

# Parse, filter, and display specific fields
{app="payments-service"} | json | level="error"
  | line_format "{{.timestamp}} {{.user_id}} {{.message}}"

# Pattern parsing (for non-JSON logs)
{app="nginx"} | pattern `<ip> - <user> [<timestamp>] "<method> <path> <proto>" <status> <bytes>`
```

### Metrics from logs

```logql
# Count log lines per minute
sum(rate({app="payments-service"}[1m]))

# Count error lines per minute
sum(rate({app="payments-service"} |= "error" [1m]))

# Error rate (errors / total)
sum(rate({app="payments-service"} |= "error" [5m]))
  /
sum(rate({app="payments-service"}[5m]))

# Average request duration extracted from JSON logs
avg_over_time(
  {app="payments-service"} | json | unwrap duration_ms [5m]
)

# 95th percentile from logs
quantile_over_time(0.95,
  {app="payments-service"} | json | unwrap duration_ms [5m]
)
```

---

## Prometheus metric naming conventions

```
# Format: namespace_subsystem_name_unit
http_requests_total                   ← counter (always _total suffix)
http_request_duration_seconds         ← histogram (always include unit)
process_memory_bytes                  ← gauge (always include unit)
go_goroutines                         ← gauge (dimensionless, no unit suffix)

# Good names
payments_processed_total              ← counter
payments_processing_duration_seconds  ← histogram
payments_queue_depth                  ← gauge
db_connections_active                 ← gauge

# Bad names (missing units, ambiguous)
payment_count
request_time
memory_usage
```

---

## Instrumenting your Python app

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Counters — only go up, track totals
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Histograms — track distributions, great for latency
REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# Gauges — current value, can go up or down
ACTIVE_CONNECTIONS = Gauge(
    'http_connections_active',
    'Currently active HTTP connections'
)

# Usage in a FastAPI endpoint
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    ACTIVE_CONNECTIONS.inc()

    response = await call_next(request)

    duration = time.time() - start
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    ACTIVE_CONNECTIONS.dec()

    return response

# Expose metrics endpoint
start_http_server(8001)   # metrics available at :8001/metrics
```

---

## OpenTelemetry — instrumenting your app for tracing

```python
# Install: pip install opentelemetry-sdk opentelemetry-exporter-otlp

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Setup
provider = TracerProvider()
exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317")
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

# Auto-instrument FastAPI and outgoing HTTP requests
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

# Manual span for custom operations
tracer = trace.get_tracer(__name__)

async def process_payment(payment_id: str, amount: float):
    with tracer.start_as_current_span("process_payment") as span:
        span.set_attribute("payment.id", payment_id)
        span.set_attribute("payment.amount", amount)

        try:
            result = await charge_card(payment_id, amount)
            span.set_attribute("payment.status", "success")
            return result
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.StatusCode.ERROR, str(e))
            raise
```

---

## ArgoCD quick reference

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Get initial admin password
argocd admin initial-password -n argocd

# Login
argocd login localhost:8080

# Create an application
argocd app create payments-service \
  --repo https://github.com/yourorg/gitops-repo \
  --path apps/payments-service \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace production \
  --sync-policy automated \
  --auto-prune \
  --self-heal

# List applications
argocd app list

# Sync manually
argocd app sync payments-service

# Check sync status
argocd app get payments-service

# Rollback to previous version
argocd app rollback payments-service

# Get application history
argocd app history payments-service
```

**ArgoCD Application manifest:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: payments-service
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/yourorg/gitops-repo
    targetRevision: HEAD
    path: apps/payments-service
    helm:
      valueFiles:
        - values-production.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true        # delete resources removed from git
      selfHeal: true     # revert manual changes
    syncOptions:
      - CreateNamespace=true
```

---

## SLO worksheet

Use this template when defining an SLO for any service:

```
Service: ________________________

What do users actually care about?
  e.g. "Payments complete successfully and quickly"

SLI (how we measure it):
  e.g. "The percentage of /payment requests that return 2xx in under 500ms"

PromQL for the SLI:
  Good requests:  ____________________________________________
  Total requests: ____________________________________________

SLO target: ______%  over a ______ day rolling window

Error budget:
  (100 - SLO) % = ______% = ______ minutes/month of allowed failure

Alert thresholds (burn rate):
  Critical (page now):  ____x burn rate  (budget exhausted in 1 hour  → 14.4x)
  Warning  (ticket):    ____x burn rate  (budget exhausted in 6 hours →  6.0x)

Review cadence: monthly / quarterly
```

---

*Part of [devops-to-ai](../../README.md) — Phase 02: Cloud Native Operations*
