# Phase 02 — Cloud Native Operations

> **"Anyone can deploy an app. An engineer can tell you why it's slow at 2am without waking up."**
>
> Phase 01 got your app running. Phase 02 teaches you to **operate** it — metrics when something breaks, logs that explain what happened, traces that show where time went, and GitOps so deploys aren't a manual ritual.

---

## Who this is for

| You are... | Do this |
|---|---|
| Finished Phase 01 (Docker, K8s, CI/CD basics) | Work through every topic, then the capstone |
| Junior DevOps — deploy fine, debugging in prod is shaky | Focus on observability + SLOs, build the capstone locally first |
| Already run Prometheus/Grafana/ArgoCD in production | Take the [self-check](#self-check--can-you-skip) — skip to Phase 03 if you pass |

**Time:** 6–8 weeks part-time  
**Goal:** Know when your system is unhealthy **before** users tell you, and deploy from Git without kubectl heroics.

---

## Start here — four steps

```
1. Self-check     →  Already operating prod stacks? Maybe skip to Phase 03
2. Learn          →  Metrics → logs → traces → GitOps → SLOs (in that order)
3. Practice       →  Run the capstone locally with Docker Compose first
4. Capstone       →  Full observability stack, then Kubernetes + ArgoCD
```

**Local-first (recommended):** You can complete most of Phase 02 on your laptop with Docker Compose — no cloud bill required on day one. Add kind/k3d + ArgoCD when the local stack makes sense.

**Cheatsheets in this repo:**

| Topic | Cheatsheet |
|---|---|
| PromQL, LogQL, tracing | [cheatsheets/observability.md](./cheatsheets/observability.md) |
| ArgoCD & GitOps | [cheatsheets/gitops.md](./cheatsheets/gitops.md) |
| SLOs & error budgets | [cheatsheets/slo-error-budgets.md](./cheatsheets/slo-error-budgets.md) |

---

## Self-check — can you skip?

If you can do **all** of these without looking things up, skip to [Phase 03](../Phase03_AI_Augmented_DevOps/README.md):

- Explain metrics vs logs vs traces and when to use each
- Write a PromQL query for 5-minute error rate
- Build a Grafana panel for the four golden signals
- Describe what ArgoCD does when Git and the cluster disagree
- Define SLI, SLO, and error budget for a non-engineer
- Find a slow span in a distributed trace

Otherwise stay here. Phase 03 assumes you can **operate** a system, not just deploy one.

---

## Learning objectives

By the end of Phase 02, you should answer **yes** to all of these:

- [ ] Explain metrics, logs, and traces — and when to reach for each
- [ ] Scrape an app with Prometheus and write PromQL for a real question
- [ ] Build a Grafana dashboard with the four golden signals
- [ ] Instrument an app with OpenTelemetry and view traces in Grafana
- [ ] Explain how ArgoCD detects drift and syncs the cluster
- [ ] Write an SLO and an alert tied to error budget burn rate
- [ ] Explain what a service mesh is — and when you **don't** need one

---

## Topics

Work in this order. Metrics first — everything else hangs off knowing *something is wrong*.

### 1. The three pillars (read this before installing tools)

Three questions, three tools:

```
Metrics  →  "Is something wrong?"     CPU 94%, error rate 2.3%
Logs     →  "What happened?"          payment timeout for user 4421
Traces   →  "Where did it go slow?"   Stripe call took 800ms of 832ms total
```

Most juniors lean on logs alone and wonder why debugging hurts. Metrics flag the fire. Logs tell the story. Traces show the path through microservices.

**Four golden signals** — if you instrument nothing else, instrument these:

| Signal | Measures | Example |
|---|---|---|
| Latency | How long | p99 response time |
| Traffic | How much | Requests/sec |
| Errors | How often | 5xx rate |
| Saturation | How full | CPU, memory, queue depth |

One dashboard with those four tells you 80% of what you need.

→ [Observability cheatsheet](./cheatsheets/observability.md)

---

### 2. Prometheus — metrics that scrape themselves

Prometheus **pulls** metrics from your apps on a schedule (usually every 15s). Your app exposes `/metrics`; Prometheus stores time series; you query with PromQL; Grafana draws the graphs.

```
App /metrics  →  Prometheus scrape  →  PromQL  →  Grafana
```

**Learn:**
- Counter vs gauge vs histogram (requests total vs current memory vs latency buckets)
- `prometheus.yml` scrape configs
- PromQL: `rate()`, `histogram_quantile()`, label filters
- Alert rules (start simple — high error rate, pod down)

**Try this:** Hit `http://localhost:9090/targets` after starting the capstone stack. Every target should be **UP** before you build dashboards.

---

### 3. Grafana — make metrics readable

Prometheus is for machines. Grafana is for humans (and on-call engineers at 2am).

**Learn:**
- Connect Prometheus (and later Loki + Tempo) as data sources
- Build panels: time series, stat, gauge
- Dashboard variables — one dashboard, `$service` dropdown for all apps
- Export dashboard JSON to Git (dashboards as code)

**Build this first:**

```
┌──────────────┬──────────────┐
│  RPS         │  Error %     │
├──────────────┼──────────────┤
│  p99 latency │  CPU / mem   │
└──────────────┴──────────────┘
```

[Grafana Play](https://play.grafana.org/) is free if you want to click around before installing.

---

### 4. Loki — logs you can search

Plain text logs at scale are pain. **Structured JSON logs** + **Loki** = search like metrics.

```json
{"level":"error","event":"payment_failed","user_id":4421,"duration_ms":30421}
```

**Learn:**
- LogQL: `{app="payments"} | json | level="error"`
- Label what to label (service, env) — not high-cardinality stuff like `user_id`
- Promtail ships logs to Loki; Grafana queries them

---

### 5. Tempo + OpenTelemetry — follow one request

When a checkout hits three services, each service's logs only know its slice. **Traces** show the full hop-by-hop path.

**Learn:**
- Spans, trace ID, parent/child spans
- OpenTelemetry SDK in your app (or auto-instrumentation)
- OTel Collector receives spans → forwards to Tempo
- Grafana Explore: jump from trace → logs with the same trace ID

---

### 6. GitOps with ArgoCD

Phase 01 probably deployed with `helm upgrade` from CI. GitOps flips the model: **Git is the source of truth**, a controller in the cluster keeps reality matched.

```
git push  →  ArgoCD sees diff  →  cluster syncs  →  drift gets reverted
```

**Why teams bother:**
- Self-healing — someone `kubectl edit`s? ArgoCD puts it back
- Audit trail — every change is a commit
- Rollback = `git revert`, not a bespoke pipeline step

**Learn after** local observability works. ArgoCD on kind/k3d is enough for the capstone.

→ [GitOps cheatsheet](./cheatsheets/gitops.md)

---

### 7. SLOs and error budgets

Reliability is a product choice, not a default of 99.999%.

- **SLI** — what you measure ("requests under 500ms that return 2xx")
- **SLO** — your target ("99.5% over 30 days")
- **Error budget** — how much failure you're allowed (0.5% = ~3.6 hours/month at 99.5%)

Burn the budget too fast → slow down risky releases. Budget healthy → ship the scary feature.

→ [SLO cheatsheet](./cheatsheets/slo-error-budgets.md) · [Google SRE Book ch.4–5](https://sre.google/sre-book/table-of-contents/)

---

### 8. Service mesh — probably not yet

A mesh (Istio, Linkerd) adds mTLS, retries, and traffic metrics via sidecar proxies. Most teams **don't** need one until they have many services and real pain around security or traffic shaping.

Read the concept. Skip installing one for the capstone unless you're curious.

---

## Capstone project

### Full observability stack

Three small services (checkout flow), fully instrumented, with Prometheus + Grafana + Loki + Tempo locally — then Kubernetes + ArgoCD when you're ready.

**Starter code:** [projects/observability-stack/](./projects/observability-stack/)

| Part | What you do |
|---|---|
| 1 | Run `api-gateway` (provided), build or extend `payments-service` + `user-service` |
| 2 | Verify Prometheus targets UP, write golden-signal PromQL |
| 3 | Build Grafana dashboards, export JSON to `dashboards/` |
| 4 | Query logs in Loki, errors by service |
| 5 | Follow a checkout trace in Tempo |
| 6 | Configure alert rules, trigger one on purpose |
| 7 | Deploy to kind/k3d with ArgoCD (stretch after local works) |

**Definition of done:**
- [ ] `docker compose up` — all services healthy
- [ ] Prometheus scraping all three apps
- [ ] Grafana dashboard with four golden signals (real data)
- [ ] One end-to-end trace in Tempo
- [ ] Loki showing JSON logs from all services
- [ ] At least 3 alert rules tested
- [ ] Dashboards committed as JSON under `dashboards/`
- [ ] ArgoCD managing apps on Kubernetes (stretch OK to document manual deploy for local-only learners)

Full walkthrough → [projects/observability-stack/README.md](./projects/observability-stack/README.md)

---

## Ready for Phase 03?

Don't move on until you can do these **without googling**:

1. Counter vs gauge — when to use each
2. PromQL error rate over 5 minutes for one service
3. What ArgoCD does on drift
4. SLI / SLO / error budget in plain English
5. Why traces beat logs alone for cross-service latency
6. Spot the degraded golden signal on a dashboard
7. What happens if you `kubectl edit` an ArgoCD-managed Deployment

---

## Resources

| Resource | What it's for |
|---|---|
| [Prometheus docs](https://prometheus.io/docs/introduction/overview/) | Metrics fundamentals |
| [PromQL cheatsheet](https://promlabs.com/promql-cheat-sheet/) | Query reference |
| [Grafana Play](https://play.grafana.org/) | Click without installing |
| [Loki docs](https://grafana.com/docs/loki/latest/get-started/) | Log aggregation |
| [OpenTelemetry docs](https://opentelemetry.io/docs/) | Tracing |
| [ArgoCD docs](https://argo-cd.readthedocs.io/en/stable/) | GitOps |
| [Google SRE Book](https://sre.google/sre-book/table-of-contents/) | SLOs (free) |
| Repo cheatsheets | Day-to-day lookup |

---

## Track your progress

```
[Phase 02] Starting — your-handle
[Phase 02] Done — your-handle
```

When you mark Done, share a Grafana screenshot and your repo link.

---

*← [Phase 01 — Core DevOps](../Phase01_Core_DevOps/README.md) | [Phase 03 — AI-Augmented DevOps →](../Phase03_AI_Augmented_DevOps/README.md)*
