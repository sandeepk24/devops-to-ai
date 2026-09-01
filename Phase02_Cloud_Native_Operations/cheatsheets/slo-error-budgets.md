# SLOs & error budgets cheatsheet

**Use this when:** deciding if a release is safe, writing alerts that aren't noise, or explaining reliability to a PM.  
**Remember:** 99.99% sounds impressive until you're on-call for it.

---

## Vocabulary (plain English)

| Term | Means |
|---|---|
| **SLI** | The number you measure — "2xx responses under 500ms" |
| **SLO** | The target — "99.5% of requests meet the SLI over 30 days" |
| **SLA** | Contract with customers — miss it, credits/refunds |
| **Error budget** | Allowed failure — `(100% - SLO)` over the window |

Example:

```
SLO: 99.5% success over 30 days
Error budget: 0.5% ≈ 3.6 hours of bad requests (roughly)
Budget half gone → ship carefully
Budget gone → reliability work, not features
```

---

## Pick an SLI that users feel

Good SLIs:
- Successful checkout completion rate
- API latency p99 under a threshold
- Job processed within N minutes

Bad SLIs:
- CPU under 80% (users don't care about your CPU)
- Pod count = 3 (that's your implementation, not user happiness)

---

## Error budget math (sketch)

```
allowed_bad = (1 - SLO) × total_requests_in_window

burn_rate = (bad_requests_in_last_hour) / (allowed_bad_per_hour)

burn_rate > 1  →  burning budget too fast
burn_rate > 14.4 for 1h  →  budget gone in ~2 days (classic multi-window alert)
```

You don't need to memorise 14.4 — know that **burn rate alerts** beat raw "error rate > 1%" for paging.

---

## PromQL starters (payments-service example)

```promql
# Error rate (5m) as ratio 0–1
sum(rate(http_requests_total{job="payments-service", status=~"5.."}[5m]))
/
clamp_min(sum(rate(http_requests_total{job="payments-service"}[5m])), 1e-9)

# p99 latency
histogram_quantile(0.99,
  sum by (le) (rate(http_request_duration_seconds_bucket{job="payments-service"}[5m]))
)
```

Wire alerts to **user-visible** pain, not every blip.

---

## Alert severity guide

| Alert | Page? | Example |
|---|---|---|
| SLO burn rate critical | Yes | Budget exhausted in < 1 day at current rate |
| Error rate high 5m | Maybe | After confirming not a deploy canary |
| Disk 85% | Ticket | Plan cleanup |
| Single pod restart | Often no | If Deployment keeps desired count |

Write a **runbook line** per alert: "If this fires, check X, then Y."

---

## Policy one-pager (team template)

```
If error budget > 50% left:
  → normal releases OK

If error budget 10–50%:
  → no risky Friday deploys; extra review

If error budget < 10%:
  → freeze feature work; fix reliability
```

---

## Phase 02 capstone

Build dashboard 3 in the observability project:
- Current SLO compliance % for `payments-service`
- Error budget remaining
- Burn rate panel + one alert rule you trigger on purpose

---

*Part of [devops-to-ai](../../README.md) — Phase 02: Cloud Native Operations*
