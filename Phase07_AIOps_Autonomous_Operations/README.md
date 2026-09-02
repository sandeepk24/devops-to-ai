# Phase 07 — AIOps & Autonomous Operations

> **"Alerting is not operating. Operating is closing the loop — detect, decide, act, verify — without waiting for a human to notice every blip."**
>
> Phases 00–06 made you dangerous at shipping, observing, securing, and productizing platforms. Phase 07 is where the system starts to **help itself**: anomaly detection that cuts noise, remediation playbooks with guardrails, and predictive scaling before the pager sings.

---

## Who this is for

| You are... | Do this |
|---|---|
| Finished Phase 02 (observability) and ideally 03–06 | Build the self-healing lab |
| Junior DevOps — tired of flappy alerts | Start with noise reduction + one safe auto-remediation |
| Already run custom operators + anomaly pipelines in prod | Take the [self-check](#self-check--can-you-skip) |

**Time:** 5–7 weeks part-time  
**Goal:** One vertical slice: bad signal → automated diagnosis context → **safe** action → verification + audit log.

**Prereqs:** Phase 02 required. Phase 03 (LLM diagnosis) and Phase 05 (policy) strongly recommended before you auto-execute anything.

---

## Start here — four steps

```
1. Self-check     →  Already shipping self-healing in prod? Maybe skip
2. Learn          →  Noise → anomalies → correlation → remediation → verify
3. Practice       →  On kind: detect CrashLoop → restart/rollback with approval mode first
4. Capstone       →  Self-healing demo with Slack/console audit trail
```

**Safety rule for this whole phase:** build **suggest mode** before **act mode**. Never start with auto-rollback in production.

---

## Self-check — can you skip?

- Explain alert fatigue and how burn-rate / anomaly alerts differ from static thresholds
- Correlate metrics + logs + deploys into one incident hypothesis
- Describe a Kubernetes operator at a high level (reconcile loop)
- Design a remediation with preconditions, action, and verification
- Know when automation must stop (data loss risk, security boundary, unknown blast radius)
- Measure whether an auto-action improved MTTR or made things worse

---

## Learning objectives

- [ ] Reduce noisy alerts with better signals (SLOs, anomalies, grouping)
- [ ] Detect a class of failures automatically (e.g. CrashLoopBackOff, error spike)
- [ ] Run a remediation playbook with explicit allowlist of actions
- [ ] Verify post-action health (same golden signals you trust)
- [ ] Emit an audit trail (who/what/why/when — even if "who" is the controller)
- [ ] Add a human approval gate for destructive actions
- [ ] Document a kill switch

---

## Topics

### 1. From monitoring to AIOps

Classic monitoring: threshold → page human.  
AIOps adds: pattern detection, correlation, suggested (then automated) response.

Don't buy a magic box on day one. Start with **good telemetry** (Phase 02) + **narrow automation**.

### 2. Alert noise reduction

- Grouping, inhibition, severities that match user impact
- SLO burn alerts vs raw CPU pages
- Anomaly detection basics (seasonality, baselines) — even simple rolling z-scores teach the idea
- If everything is critical, nothing is

### 3. Correlation & context

Reuse Phase 03 skills: attach logs, recent deploys, change events to the alert. Automation without context is a coin flip.

### 4. Remediation patterns

| Pattern | Example | Risk |
|---|---|---|
| Restart | Delete pod / rollout restart | Low if stateless |
| Scale | +N replicas on latency SLO burn | Medium (cost) |
| Rollback | Helm/Argo revert | Medium–high |
| Mitigate | Feature flag off, traffic shift | Needs prep |
| Page human | Unknown / high blast radius | Default fallback |

Allowlist actions. Denylist anything that touches data destruction or IAM.

### 5. Kubernetes automation building blocks

- Controllers / operators — desired state loops
- CronJobs for periodic health sweeps
- Admission vs background remediation
- Event-driven hooks (Alertmanager webhook → remediator service)

### 6. Predictive operations

- Forecast traffic from weekly patterns
- Schedule scale-up before known peaks
- Capacity headroom for LLM/GPU pools (Phase 04) — queue depth beats CPU alone

### 7. Feedback loops & safety

- Shadow mode: log what you *would* have done
- Canary remediations on non-prod first
- Auto-disable after N failures (circuit breaker for the automator)
- Keep Phase 05 policy in the path — automation must not bypass admission controls

---

## Capstone

### Self-healing service demo

**Scenario:** payments-api starts CrashLooping or burning error budget after a bad deploy.

**Build:**
1. Detector — watches metrics/events (Prom alert webhook or controller)
2. Context pack — recent logs + last deploy SHA (Phase 03 style)
3. Decider — rule engine *or* LLM suggestion with strict JSON schema
4. Actuator — allowlisted actions only (`rollout restart`, `rollback` with approval flag)
5. Verifier — check error rate / ready replicas for N minutes
6. Audit — console + Slack/file log of every decision

**Modes:**
- `SUGGEST` — post recommendation only (default)
- `AUTO` — execute low-risk actions
- Approval required for rollback

**Definition of done:**
- [ ] Inject failure; system detects within your SLO (e.g. 2 minutes)
- [ ] Suggest mode produces a clear recommended action
- [ ] Auto mode performs one low-risk remediation and verifies recovery
- [ ] Kill switch disables actuation instantly
- [ ] Audit log tells the story without screenshots of your brain

**Stretch:** Predictive scale demo; integrate Phase 03 incident bot as the "context" stage.

> Project starter planned at `projects/self-healing-ops/`.

---

## Ready for Phase 08?

You can close a detect→act→verify loop safely on a narrow failure class. Phase 08 adds **tool-using agents** — more flexible reasoning, same safety religion.

---

## Resources

| Resource | Why |
|---|---|
| Google SRE Workbook — eliminating toil | Automation philosophy |
| [Kubernetes operators pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/) | Reconcile loops |
| Prometheus Alerting + Alertmanager | Detection plumbing |
| Your Phase 02 + 03 projects | Telemetry + LLM context |

---

## Track your progress

```
[Phase 07] Starting — your-handle
[Phase 07] Done — your-handle
```

---

*← [Phase 06 — Platform Engineering](../Phase06_Platform_Engineering/README.md) | [Phase 08 — Agentic Infrastructure →](../Phase08_Agentic_Infrastructure/README.md)*
