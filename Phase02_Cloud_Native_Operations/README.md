# Phase 02 — Cloud Native Operations

> **"Anyone can deploy an app. An engineer can tell you why it's slow at 2am without waking up."**
>
> Phase 01 got your app running. Phase 02 makes it observable, reliable, and automatically delivered. This is where you stop being someone who deploys things and start being someone who operates them. The difference between a junior and intermediate engineer is almost always observability — juniors wait for users to report problems, intermediates know about problems before users do.

---

## What this phase is

Cloud native operations is the discipline of running distributed systems in production. It means your application has eyes (metrics), ears (logs), and a nervous system (traces) so you always know what's happening inside it. It means deployments happen automatically through GitOps, not manually through humans. It means you define reliability targets and measure against them.

By the end of Phase 02, you will have built a complete observability stack from scratch — the kind of setup real engineering teams pay thousands of dollars a month for on hosted platforms.

**Estimated time:** 6–8 weeks  
**Target audience:** Anyone who completed Phase 01 or already works with Docker and Kubernetes daily  
**Skippable if:** You've built Prometheus/Grafana stacks, configured GitOps with ArgoCD, and written SLOs professionally

---

## Learning objectives

When you finish this phase, you should be able to answer yes to all of these:

- [ ] Can you explain the difference between metrics, logs, and traces — and when to use each one?
- [ ] Can you set up Prometheus to scrape a custom application and write a PromQL query to answer a real operational question?
- [ ] Can you build a Grafana dashboard from scratch that shows the four golden signals for a service?
- [ ] Can you instrument a Python or Go application with OpenTelemetry and see traces in a UI?
- [ ] Can you set up ArgoCD and explain how it detects and reconciles drift?
- [ ] Can you write an SLO for a service and create an alerting rule based on an error budget?
- [ ] Can you explain what a service mesh does and why you might — or might not — need one?

If you can say yes to all seven, you're ready for Phase 03.

---

## Topics

### 1. The three pillars of observability

Before touching any tools, understand what you're trying to achieve. Observability is the ability to understand the internal state of a system from its external outputs. There are three types of output — and each answers a different question.

```
Metrics  → "Is something wrong?"       Numbers over time. CPU at 94%. Error rate at 2.3%.
Logs     → "What happened?"            Events with context. "Payment failed for user 4421: timeout after 30s"
Traces   → "Where did it go slow?"     Request journeys across services. Step 3 of 7 took 800ms.
```

The mistake most engineers make is using only logs and then wondering why production is hard to debug. Metrics tell you that something is wrong. Logs tell you what happened. Traces tell you where in a chain of services the problem lives. You need all three.

**The four golden signals** — if you instrument nothing else, instrument these four things for every service:

| Signal | What it measures | Example metric |
|---|---|---|
| Latency | How long requests take | p50, p95, p99 response time |
| Traffic | How much demand exists | Requests per second |
| Errors | How often things fail | HTTP 5xx rate |
| Saturation | How full the system is | CPU %, memory %, queue depth |

These four signals, on a single dashboard, will tell you 80% of what you need to know about a service's health.

---

### 2. Prometheus — metrics collection

Prometheus is the industry standard for metrics in cloud native environments. It works by scraping — pulling metrics from your applications and infrastructure on a schedule — and storing them as time series data.

**How it works:**

```
Your app exposes metrics at /metrics
         ↓
Prometheus scrapes /metrics every 15 seconds
         ↓
Stores as time series: metric_name{labels} value timestamp
         ↓
You query with PromQL
         ↓
Grafana visualises the results
```

**What to cover:**

- Prometheus architecture — server, exporters, Alertmanager, Pushgateway
- The data model — metric names, labels, timestamps, samples
- Metric types:
  - `Counter` — only goes up (requests total, errors total)
  - `Gauge` — goes up and down (current memory, active connections)
  - `Histogram` — distribution of values (request duration buckets)
  - `Summary` — like histogram but calculated client-side
- Scrape configuration — `prometheus.yml`, `scrape_configs`, `job_name`, `static_configs`
- Service discovery — Kubernetes SD, how Prometheus finds pods automatically
- Exporters — `node_exporter` (host metrics), `kube-state-metrics` (k8s object metrics), `blackbox_exporter` (external checks)
- Instrumentation — adding metrics to your own application using the Prometheus client library

**PromQL — the query language:**

```promql
# Current HTTP request rate (per second, 5m window)
rate(http_requests_total[5m])

# Error rate as a percentage
rate(http_requests_total{status=~"5.."}[5m])
  /
rate(http_requests_total[5m]) * 100

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Memory usage as a percentage
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)
  /
node_memory_MemTotal_bytes * 100

# Alert: error rate above 5% for 5 minutes
ALERT HighErrorRate
  IF rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
  FOR 5m
  LABELS { severity="critical" }
  ANNOTATIONS { summary="High error rate on {{ $labels.job }}" }
```

**Recommended resources:**
- [Prometheus docs — getting started](https://prometheus.io/docs/introduction/overview/)
- [PromQL cheatsheet](https://promlabs.com/promql-cheat-sheet/) — bookmark this
- [Prometheus: Up & Running](https://www.oreilly.com/library/view/prometheus-up/9781492034131/) — O'Reilly book, the definitive reference

---

### 3. Grafana — visualisation

Prometheus stores and queries. Grafana visualises. You'll use Grafana to build dashboards that make your metrics human-readable and to set up alerting rules.

**What to cover:**

- Connecting Prometheus as a data source
- The dashboard model — dashboards, rows, panels, variables
- Panel types — time series, stat, gauge, bar chart, table, heatmap
- Dashboard variables — make one dashboard work for all services/namespaces
- Template variables — `$namespace`, `$service`, `$instance`
- Annotations — mark deployments, incidents on your graphs
- Alerting in Grafana — alert rules, contact points, notification policies
- Dashboard as code — JSON export, Grafana provisioning via ConfigMaps

**The dashboard you should build first — four golden signals:**

```
┌─────────────────────────┬─────────────────────────┐
│  Request rate (RPS)     │  Error rate (%)         │
│  [Time series graph]    │  [Time series graph]    │
├─────────────────────────┼─────────────────────────┤
│  p99 Latency (ms)       │  CPU Saturation (%)     │
│  [Time series graph]    │  [Time series graph]    │
└─────────────────────────┴─────────────────────────┘
```

**Recommended resources:**
- [Grafana docs — dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
- [Grafana Play](https://play.grafana.org/) — live demo environment, explore without installing
- [Awesome Grafana Dashboards](https://grafana.com/grafana/dashboards/) — import community dashboards to learn from them

---

### 4. Structured logging with Loki

Logs are only useful if you can search them. Loki is Prometheus for logs — it stores log streams and lets you query them with LogQL. Paired with Grafana, you get logs and metrics in the same interface.

**Why structured logging matters:**

```
# Unstructured log — hard to query
ERROR payment failed for user 4421 after 30 seconds timeout

# Structured log (JSON) — queryable, filterable, aggregatable
{"level":"error","event":"payment_failed","user_id":4421,"duration_ms":30421,"reason":"timeout"}
```

**What to cover:**

- Why JSON logs beat plain text logs at scale
- Loki architecture — Promtail (log collector), Loki (storage/query), Grafana (UI)
- LogQL — Loki's query language
- Log labels — what to label and what not to (high-cardinality label anti-pattern)
- Promtail configuration — scraping logs from Kubernetes pods
- Correlating logs with metrics in Grafana using exemplars

**LogQL basics:**

```logql
# All logs from the payments service
{app="payments"}

# Filter to errors only
{app="payments"} |= "error"

# Parse JSON and filter by field
{app="payments"} | json | level="error"

# Count error rate over time
rate({app="payments"} |= "error" [5m])

# Extract a field and filter
{app="payments"} | json | duration_ms > 1000
```

**Recommended resource:**
- [Loki docs — getting started](https://grafana.com/docs/loki/latest/get-started/)

---

### 5. Distributed tracing with Tempo

When a user request touches five services and something goes wrong, logs tell you each service's perspective but not the full picture. Traces show you the complete journey of a single request — every service it touched, how long each step took, where it failed.

**The mental model:**

```
User clicks "Pay"
    │
    ├── [API Gateway]        12ms
    │       │
    │       ├── [Auth Service]      8ms   ✓
    │       │
    │       └── [Payment Service]  820ms  ← THIS IS SLOW
    │               │
    │               ├── [DB query]         15ms  ✓
    │               │
    │               └── [Stripe API]      800ms  ← ROOT CAUSE
    │
Total: 832ms
```

Without tracing you'd have four separate logs saying "I was called and I returned." With tracing you see the entire picture in one view.

**What to cover:**

- Trace anatomy — spans, trace ID, span ID, parent span, baggage
- OpenTelemetry — the vendor-neutral standard for instrumentation
  - The OTel SDK — instrumenting your application
  - Auto-instrumentation vs manual instrumentation
  - The OTel Collector — receiving, processing, exporting telemetry
- Tempo — Grafana's trace storage backend
- Connecting traces to logs (trace ID in logs) and metrics (exemplars)

**Recommended resources:**
- [OpenTelemetry docs](https://opentelemetry.io/docs/) — start with the getting started guide for your language
- [Tempo docs](https://grafana.com/docs/tempo/latest/)

---

### 6. GitOps with ArgoCD

In Phase 01 you deployed to Kubernetes by running `kubectl` or `helm` commands from a CI pipeline. GitOps is a better model: your Git repository is the single source of truth for what should be running, and a controller in the cluster continuously reconciles reality with what Git says.

**The GitOps model:**

```
Developer pushes to Git
        ↓
ArgoCD detects the change (polls every 3 minutes, or webhook)
        ↓
ArgoCD compares Git state vs cluster state
        ↓
If they differ → ArgoCD syncs the cluster to match Git
        ↓
If sync fails → ArgoCD marks app as degraded and alerts
```

**Why this is better than CI-triggered kubectl:**

- The cluster will self-heal if someone makes manual changes — ArgoCD will revert them
- Git is the audit log — every change has a commit, author, and timestamp
- Rollback is `git revert` — you don't need special pipeline logic
- ArgoCD works even when your CI system is down

**What to cover:**

- ArgoCD architecture — API server, repo server, application controller, dex
- Applications and App of Apps pattern
- Sync policies — manual vs automatic, self-heal, prune
- Health checks — how ArgoCD determines if a deployment is healthy
- Sync waves and hooks — controlling deployment order
- ArgoCD Image Updater — automatically updating image tags when new images are pushed
- RBAC in ArgoCD — who can deploy to which environments
- Notifications — Slack/email alerts on sync success/failure

**Recommended resources:**
- [ArgoCD docs](https://argo-cd.readthedocs.io/en/stable/)
- [GitOps with ArgoCD by Kostis Kapelonis](https://codefresh.io/gitops/) — free book

---

### 7. SRE principles — SLOs, SLAs, and error budgets

Site Reliability Engineering gives you a framework for thinking about reliability as a product decision, not just an engineering one. The core insight: **reliability has a cost, and that cost must be balanced against the cost of moving fast.**

**Key concepts:**

**SLI (Service Level Indicator)** — a metric that measures reliability
```
"The percentage of HTTP requests that return a 2xx response in under 500ms"
```

**SLO (Service Level Objective)** — your reliability target
```
"99.5% of requests should be successful and under 500ms, measured over a 30-day rolling window"
```

**SLA (Service Level Agreement)** — a contract with consequences
```
"We guarantee 99.5% availability. If we fall below this, customers get service credits."
```

**Error budget** — the allowed unreliability
```
99.5% SLO over 30 days = 0.5% budget = 3.6 hours of downtime allowed per month

If you've used 3 hours this month: you have 36 minutes left — move carefully
If you've used 0 hours this month: you have 3.6 hours — ship that risky feature
```

**What to cover:**

- Writing SLIs that actually measure what users care about
- Setting realistic SLOs — not 99.999% by default
- Error budget policy — what happens when you burn through the budget
- Toil — what it is, why it's the enemy, how to measure and reduce it
- The SRE workload model — 50% engineering, 50% operations, toil cap
- Alerting on burn rate instead of raw error rate (dramatically reduces false positives)

**Recommended resources:**
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/) — free online, chapters 4 and 5 are essential
- [The SRE Workbook](https://sre.google/workbook/table-of-contents/) — practical implementation guide, also free

---

### 8. Service mesh basics

A service mesh is a dedicated infrastructure layer that handles service-to-service communication. It gives you mutual TLS, traffic management, and observability for free — without changing application code.

**Do you actually need one?** Be honest here. Most teams don't need a service mesh until they have 10+ services and are struggling with one of these:

- mTLS between every service (zero-trust networking)
- Fine-grained traffic control (canary deployments, circuit breakers)
- Consistent observability across all services without touching application code

If you're not hitting those problems yet, a service mesh is complexity you don't need.

**What to cover:**

- The sidecar proxy pattern — how Envoy intercepts all traffic without application changes
- Istio vs Linkerd — capability vs simplicity tradeoff
- What a mesh gives you for free: mTLS, retries, circuit breaking, traffic metrics
- Traffic management — weighted routing, header-based routing, fault injection
- How to decide if you need one

**Recommended resource:**
- [Istio docs — getting started](https://istio.io/latest/docs/setup/getting-started/)
- [Linkerd docs](https://linkerd.io/2.15/getting-started/) — easier to start with than Istio

---

## Capstone project

### Full observability stack from scratch

This is the most technically satisfying project in the roadmap so far. By the end you'll have a production-quality observability setup running on your own Kubernetes cluster.

**What you're building:**

A three-service application (API gateway + payments service + user service) fully instrumented with metrics, logs, and traces — with dashboards, alerts, and GitOps-driven deployments.

---

**Part 1 — The application**

Deploy three services to Kubernetes:

- `api-gateway` — receives requests, calls the other two services
- `payments-service` — handles payment logic, has a simulated slow endpoint
- `user-service` — handles user lookups, has a simulated error endpoint

Each service must:
- Expose a `/metrics` endpoint in Prometheus format
- Emit structured JSON logs
- Be instrumented with OpenTelemetry for distributed tracing
- Have a `/health` and `/ready` endpoint

You can use the starter code in `projects/observability-stack/` or write your own.

---

**Part 2 — Metrics with Prometheus**

- Deploy Prometheus using the `kube-prometheus-stack` Helm chart
- Configure scraping for all three services
- Write PromQL queries for all four golden signals for each service
- Set up `node_exporter` and build a node health dashboard

---

**Part 3 — Logs with Loki**

- Deploy Loki and Promtail using the `loki-stack` Helm chart
- Configure Promtail to collect logs from all pods
- Write LogQL queries to:
  - Find all errors in the last hour
  - Calculate error rate per service
  - Extract request duration from structured logs

---

**Part 4 — Traces with Tempo**

- Deploy Tempo using its Helm chart
- Configure the OpenTelemetry Collector to receive traces and send to Tempo
- Verify end-to-end traces appear in Grafana showing the full request chain

---

**Part 5 — Dashboards**

Build these dashboards in Grafana:

1. **Service health overview** — all three services, four golden signals each
2. **Node health** — CPU, memory, disk, network per node
3. **SLO dashboard** — error budget burn rate for the payments service

Export all dashboards as JSON and store them in your Git repo under `dashboards/`.

---

**Part 6 — Alerting**

Configure these alerts in Prometheus Alertmanager:

- Error rate > 5% for 5 minutes → page immediately
- p99 latency > 2 seconds for 10 minutes → warning
- Pod in CrashLoopBackOff → critical
- Node disk usage > 85% → warning
- Error budget burn rate > 14.4x → critical (this means you'll exhaust budget in 1 hour)

---

**Part 7 — GitOps with ArgoCD**

- Install ArgoCD on your cluster
- Move all Kubernetes manifests and Helm values into a Git repo
- Create an ArgoCD Application for each service
- Verify: when you `git push` a change to a Helm values file, ArgoCD automatically deploys it
- Verify: when you manually `kubectl edit` something ArgoCD manages, ArgoCD reverts it within 3 minutes

---

**Definition of done:**

- [ ] All three services running and healthy in Kubernetes
- [ ] Prometheus scraping all services — verify with `kubectl port-forward` to Prometheus UI
- [ ] Grafana dashboards showing real data for all four golden signals
- [ ] At least one trace visible end-to-end in Grafana Tempo
- [ ] Loki showing logs from all pods in Grafana
- [ ] ArgoCD managing all deployments — nothing deployed manually
- [ ] At least 3 alert rules configured and tested (use `amtool` to verify)
- [ ] All dashboards exported to JSON and committed to Git

**Stretch goals:**
- Add Grafana OnCall or PagerDuty integration for alert routing
- Configure ArgoCD Image Updater to automatically bump image tags on new builds
- Write a runbook for each alert rule — what to do when it fires
- Add k6 load testing scripts that generate realistic traffic patterns

---

## How to know you're ready for Phase 03

Do not move on until you can do all of the following without googling:

- Explain the difference between a counter and a gauge in Prometheus and when to use each
- Write a PromQL query that calculates the error rate for a service over the last 5 minutes
- Explain what ArgoCD does when it detects drift between Git and the cluster
- Define SLO, SLI, and error budget in plain language that a non-engineer would understand
- Explain what a distributed trace is and why you can't get the same information from logs alone
- Look at a Grafana dashboard and identify which of the four golden signals is degraded
- Explain what happens to an existing ArgoCD-managed deployment when you `kubectl edit` it directly

If any of those trips you up, go back and spend more time. Phase 03 builds on the assumption that you can operate a real production system, not just deploy one.

---

## Resources summary

| Resource | Type | Cost | Link |
|---|---|---|---|
| Prometheus docs | Docs | Free | [prometheus.io/docs](https://prometheus.io/docs/introduction/overview/) |
| PromQL cheatsheet | Reference | Free | [promlabs.com](https://promlabs.com/promql-cheat-sheet/) |
| Prometheus: Up & Running | Book | Paid | [O'Reilly](https://www.oreilly.com/library/view/prometheus-up/9781492034131/) |
| Grafana Play | Sandbox | Free | [play.grafana.org](https://play.grafana.org/) |
| Grafana dashboard library | Reference | Free | [grafana.com/dashboards](https://grafana.com/grafana/dashboards/) |
| Loki docs | Docs | Free | [grafana.com/docs/loki](https://grafana.com/docs/loki/latest/get-started/) |
| OpenTelemetry docs | Docs | Free | [opentelemetry.io/docs](https://opentelemetry.io/docs/) |
| Tempo docs | Docs | Free | [grafana.com/docs/tempo](https://grafana.com/docs/tempo/latest/) |
| ArgoCD docs | Docs | Free | [argo-cd.readthedocs.io](https://argo-cd.readthedocs.io/en/stable/) |
| Google SRE Book | Book | Free | [sre.google/sre-book](https://sre.google/sre-book/table-of-contents/) |
| The SRE Workbook | Book | Free | [sre.google/workbook](https://sre.google/workbook/table-of-contents/) |
| Istio getting started | Docs | Free | [istio.io/docs](https://istio.io/latest/docs/setup/getting-started/) |

---

## Community & tracking

Open an issue with the title `[Phase 02] Starting` when you begin and `[Phase 02] Done` when you complete the capstone. When you post Done, share:
- A screenshot of your Grafana dashboard
- The GitHub repo link for your observability stack
- One thing that was harder than you expected

---

*← [Phase 01 — Core DevOps](../Phase01_Core_DevOps/README.md) | [Phase 03 — AI-Augmented DevOps →](../Phase03_AI_Augmented_DevOps/README.md)*
