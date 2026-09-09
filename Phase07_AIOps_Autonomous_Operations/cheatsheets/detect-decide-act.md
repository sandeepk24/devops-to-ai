# Detect → decide → act → verify

**Use this when:** you're designing any auto-remediation (restart, scale, rollback).  
**Rule of thumb:** if you can't say how you'll **verify**, you don't get to **act**.

---

## The loop

```
DETECT   signal arrives (alert, probe fail, anomaly)
DECIDE   policy: ignore / suggest / auto (+ which action)
ACT      smallest safe change (restart one service, not "fix prod")
VERIFY   health / error rate / saturation back in range?
AUDIT    write what happened either way
```

Skip verify and you get healing theater — green scripts, red users.

---

## Decision table (starter)

| Signal | Suggest | Auto (only after suggest is boring) |
|---|---|---|
| Single pod CrashLoop in *dev* | Restart deployment | Restart with cooldown + max 3/hour |
| Elevated p99 latency | Page + link dashboards | Rarely auto — often needs a human |
| Disk > 95% on one node | Suggest cleanup / scale | Maybe auto expand *if* runbook exists |
| Suspected security incident | Never auto-delete evidence | Page security; freeze if needed |

---

## Suggest mode vs auto mode

**Suggest:** write the action you'd take; humans (or a later gate) approve.  
**Auto:** execute allowlisted actions only.

Ship suggest first. You'll learn which signals are junk before the healer starts flapping your pods.

---

## Verification checks (examples)

- HTTP `/health` or `/ready` returns 200 within N seconds  
- Restart count stopped climbing  
- Error rate below threshold for M minutes  

Lab pointer: control plane marks a service `healthy` only after a successful restart action.

---

## Useful links

- Phase 07 lab: `projects/self-healing-lab/`
- [SRE workbook — alerting](https://sre.google/workbook/alerting-on-slos/)
