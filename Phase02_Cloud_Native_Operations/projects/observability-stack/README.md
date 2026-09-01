# Capstone: Observability stack

> **Phase 02 project** — finish this before [Phase 03](../../../Phase03_AI_Augmented_DevOps/README.md).  
> Phase guide: [Phase 02 README](../../README.md)

Three tiny services that simulate checkout (`api-gateway` → `user-service` + `payments-service`), wired into Prometheus, Grafana, Loki, and Tempo. Run it all on your laptop first. Kubernetes + ArgoCD come after you can explain a graph.

---

## What's here

```
observability-stack/
├── services/
│   ├── api-gateway/       ← fully instrumented example (read this first)
│   ├── payments-service/  ← slow + error simulation built in
│   └── user-service/      ← ten fake users
├── config/                ← prometheus, grafana, loki, tempo, otel, promtail
├── dashboards/            ← export your Grafana JSON here
├── scripts/               ← traffic generator
├── k8s/                   ← ArgoCD notes (stretch)
└── docker-compose.yml
```

---

## Quick start (15 minutes)

```bash
cd Phase02_Cloud_Native_Operations/projects/observability-stack

docker compose up --build -d
docker compose ps          # everything should be running

# UIs
open http://localhost:3000   # Grafana — admin / admin
open http://localhost:9090   # Prometheus

# Smoke test checkout
curl -X POST "http://localhost:8000/checkout?user_id=user-1&amount=49.99"

# Generate traffic (errors + slow payments on purpose)
./scripts/generate-traffic.sh
```

**Prometheus targets:** http://localhost:9090/targets — all three apps should be **UP**.

---

## Your tasks (in order)

### Part 1 — Read the code, then break things on purpose

- [ ] Read `services/api-gateway/main.py` — metrics middleware, tracing spans, JSON logs
- [ ] Hit checkout with valid users (`user-1` … `user-10`) and invalid (`bad-user`)
- [ ] Watch `payments-service` logs for `payment_slow_path` and `payment_failed`
- [ ] Optional TODO: add readiness checks that call downstream services

### Part 2 — Prometheus & PromQL

- [ ] Confirm targets UP
- [ ] In Prometheus UI, run:
  - Request rate per service
  - Error rate for `payments-service`
  - p99 latency for `payments-service`
- [ ] Open **Alerts** — rules from `config/prometheus/alerts.yml` (may need traffic to fire)

### Part 3 — Grafana dashboards

Build from scratch (don't just import):

1. **Service health** — four golden signals, variable `$service`
2. **Container health** — CPU/memory if you have cAdvisor (stretch) or app metrics
3. **SLO panel** — payments error budget sketch (see [SLO cheatsheet](../../cheatsheets/slo-error-budgets.md))

Export each to `dashboards/` as JSON when done.

### Part 4 — Logs in Loki

Grafana → Explore → Loki:

```logql
{compose_service="payments-service"}
{compose_service="payments-service"} | json | level="error"
```

Add a log panel to your service dashboard.

### Part 5 — Traces in Tempo

- [ ] Run `./scripts/generate-traffic.sh`
- [ ] Grafana → Explore → Tempo → search `api-gateway`
- [ ] Open a slow trace — find the long `create_payment` span

### Part 6 — Alerts

- [ ] Read `config/prometheus/alerts.yml`
- [ ] Generate errors: run traffic script or loop checkout with bad data
- [ ] See alert go Pending → Firing in Prometheus → Alerts

### Part 7 — Kubernetes + ArgoCD (stretch)

See [k8s/argocd/install.md](./k8s/argocd/install.md). Only after local stack feels boring.

---

## Definition of done

- [ ] `docker compose up` healthy
- [ ] Prometheus scraping all services
- [ ] Grafana dashboard with four golden signals (real data)
- [ ] One end-to-end trace in Tempo
- [ ] Loki logs filterable by service + level
- [ ] ≥3 alert rules verified
- [ ] Dashboard JSON committed under `dashboards/`

---

## When you finish

Open `[Phase 02] Done` on [devops-to-ai](https://github.com/sandeepk24/devops-to-ai) with a Grafana screenshot and repo link.

→ [Phase 03 — AI-Augmented DevOps](../../../Phase03_AI_Augmented_DevOps/README.md)
