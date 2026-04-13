# Project: Full observability stack

> Phase 02 capstone project — build this before moving to Phase 03.

A three-service application fully instrumented with metrics, logs, and traces. Deployed locally with Docker Compose and to Kubernetes with Helm + ArgoCD.

---

## What's in this project

```
observability-stack/
├── services/
│   ├── api-gateway/          ← starter code provided (instrumented)
│   ├── payments-service/     ← TODO: you build this
│   └── user-service/         ← TODO: you build this
├── config/
│   ├── prometheus/           ← Prometheus config and alert rules
│   ├── grafana/              ← Grafana provisioning (data sources, dashboards)
│   ├── loki/                 ← Loki config
│   ├── tempo/                ← Tempo config
│   ├── promtail/             ← Promtail config
│   └── otel/                 ← OpenTelemetry Collector config
├── dashboards/               ← Grafana dashboard JSON files (export here)
├── k8s/                      ← Kubernetes manifests
│   ├── apps/                 ← Helm charts for your services
│   └── argocd/               ← ArgoCD Application manifests
└── docker-compose.yml        ← full stack for local development
```

---

## Quick start (local)

```bash
# 1. Start everything
docker compose up -d

# 2. Check all services are healthy
docker compose ps

# 3. Open Grafana
open http://localhost:3000
# Login: admin / admin

# 4. Open Prometheus
open http://localhost:9090

# 5. Generate some traffic
./scripts/generate-traffic.sh   # or run manually:
curl -X POST "http://localhost:8000/checkout?user_id=user-1&amount=49.99"
curl -X POST "http://localhost:8000/checkout?user_id=user-2&amount=149.99"
```

---

## Your tasks

Work through these in order. Each builds on the previous.

### Part 1 — Build the missing services

The `api-gateway` service is provided as a working example. Your job is to build `payments-service` and `user-service` following the same patterns.

**payments-service must:**
- [ ] Expose `POST /payments` — accepts `{user_id, amount}`, returns `{payment_id, status}`
- [ ] Have a `GET /payments/{payment_id}` endpoint
- [ ] Expose `/metrics`, `/health`, `/ready` endpoints
- [ ] Emit structured JSON logs for every payment attempt
- [ ] Be instrumented with OpenTelemetry tracing
- [ ] Simulate a slow path: 10% of requests take 2–5 seconds (to make latency alerts interesting)
- [ ] Simulate errors: 2% of requests return 500 (to make error alerts interesting)

**user-service must:**
- [ ] Expose `GET /users/{user_id}` — returns `{user_id, name, email}` or 404
- [ ] Have a hardcoded set of 10 test users (no database required)
- [ ] Expose `/metrics`, `/health`, `/ready` endpoints
- [ ] Emit structured JSON logs
- [ ] Be instrumented with OpenTelemetry tracing

### Part 2 — Wire up Prometheus

- [ ] Start the stack with `docker compose up -d`
- [ ] Verify Prometheus is scraping all three services: go to `http://localhost:9090/targets`
- [ ] All targets should show State: UP
- [ ] Write and verify these PromQL queries in the Prometheus UI:
  - Request rate for each service
  - Error rate for payments-service
  - p99 latency for payments-service
  - Active requests across all services

### Part 3 — Build Grafana dashboards

In Grafana (`http://localhost:3000`), build these dashboards from scratch:

**Dashboard 1 — Service health overview**
- [ ] Four golden signals (traffic, errors, latency, saturation) for each service
- [ ] Use dashboard variables so one dashboard works for all services: `$service`
- [ ] Colour thresholds: green < 1%, yellow < 5%, red > 5% for error rate

**Dashboard 2 — Node / container health**
- [ ] CPU usage per container
- [ ] Memory usage per container
- [ ] Network I/O per container

**Dashboard 3 — SLO dashboard**
- [ ] Current SLO compliance % for payments-service (target: 99.5%)
- [ ] Error budget remaining (%)
- [ ] Error budget burn rate (alert if > 14.4x)

When you're happy with each dashboard, export it as JSON and save to `dashboards/`.

### Part 4 — Set up Loki and verify logs

- [ ] In Grafana, go to Explore → select Loki data source
- [ ] Run: `{compose_service="payments-service"}` — you should see logs
- [ ] Run: `{compose_service="payments-service"} | json | level="error"`
- [ ] Build a log panel on your service dashboard showing recent errors

### Part 5 — Verify traces in Tempo

- [ ] Make a few checkout requests to generate traces
- [ ] In Grafana → Explore → select Tempo data source
- [ ] Search for traces from `api-gateway`
- [ ] Click on a trace — you should see spans for api-gateway → payments-service and api-gateway → user-service
- [ ] Find a slow trace (one where payments-service took > 1s) and identify which span was slow

### Part 6 — Configure alerting

Edit `config/prometheus/alerts.yml` and add these alert rules:
- [ ] Error rate > 5% for 5 minutes → critical
- [ ] p99 latency > 2 seconds for 10 minutes → warning
- [ ] Error budget burn rate > 14.4x → critical

Test your alerts:
```bash
# Trigger high error rate by hitting the error endpoint
for i in {1..100}; do curl -s http://localhost:8000/checkout?user_id=bad-user&amount=1 ; done
# Watch Prometheus → Alerts — your alert should go to PENDING then FIRING
```

### Part 7 — Deploy to Kubernetes with ArgoCD

- [ ] Install ArgoCD on your cluster (see `k8s/argocd/install.md`)
- [ ] Create Helm charts for all three services under `k8s/apps/`
- [ ] Create ArgoCD Application manifests under `k8s/argocd/`
- [ ] Push everything to a Git repo
- [ ] Verify ArgoCD detects and syncs all applications
- [ ] Test self-healing: manually `kubectl edit` a deployment and watch ArgoCD revert it

---

## Definition of done

Before moving to Phase 03, you must be able to demonstrate:

- [ ] All three services running and healthy
- [ ] Prometheus targets all showing UP
- [ ] At least one Grafana dashboard showing real data with all four golden signals
- [ ] At least one end-to-end trace visible in Grafana Tempo
- [ ] Loki showing logs from all services, filterable by level
- [ ] At least 3 alert rules configured (verify with `promtool check rules`)
- [ ] All dashboards exported to `dashboards/` as JSON files
- [ ] ArgoCD managing all deployments in Kubernetes

---

## Sharing your work

When done, open a `[Phase 02] Done` issue on the devops-to-ai repo. Include:
- A screenshot of your four golden signals dashboard
- Your GitHub repo link
- One thing that surprised you
