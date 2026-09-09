# Phase 07 — AIOps & Autonomous Operations

> **"Alerting is not operating. Operating is closing the loop — detect, decide, act, verify — without waiting for a human to notice every blip."**
>
> Phases 00–06 got you shipping, observing, securing, and paving roads. Phase 07 is where the system starts to **help itself**: fewer flappy alerts, remediations with seatbelts, and an audit trail you can defend in a postmortem. Start in **suggest** mode. Auto comes later — on purpose.

---

## Who this is for

| You are... | Do this |
|---|---|
| Finished Phase 02 (observability) and ideally 05–06 | Work the topics, then the self-healing lab |
| Junior DevOps — buried in pages, curious about "auto restart" | Start **Path A (mock control plane)**; kind is Path B |
| Already run operators / auto-remediation in prod | Take the [self-check](#self-check--can-you-skip) — skip to Phase 08 if you pass |

**Time:** 4–6 weeks part-time  
**Goal:** One vertical slice — detect a CrashLoop-style signal, suggest or auto a safe restart, verify, and log everything. Kill switch included.

---

## Start here — four steps

```
1. Self-check     →  Already closing the loop safely in prod? Maybe skip to Phase 08
2. Learn          →  Noise → detect/decide/act/verify → guardrails → audit
3. Practice       →  compose up → inject alert → suggest mode → then auto
4. Capstone       →  Self-healing lab with allowlists + kill switch (+ kind stretch)
```

**You do not need Prometheus or a real cluster on day one.** Path A uses a mock control plane + healer in Docker Compose. Wire real alerts later when the loop feels obvious.

**Cheatsheets:**

| Topic | Cheatsheet |
|---|---|
| Detect → decide → act → verify | [cheatsheets/detect-decide-act.md](./cheatsheets/detect-decide-act.md) |
| Guardrails, allowlists, kill switches | [cheatsheets/guardrails.md](./cheatsheets/guardrails.md) |
| Alert noise & when *not* to automate | [cheatsheets/alert-noise.md](./cheatsheets/alert-noise.md) |

**What you need:**

| Thing | Why | Notes |
|---|---|---|
| Docker (running) | Compose lab | `docker info` must work |
| curl / jq | Inject alerts, read audit | Same as earlier phases |
| Phase 02 comfort (optional) | Real metrics/alerts later | Mock path works without it |
| kind + kubectl (optional) | Path B | After Path A is solid |

---

## Self-check — can you skip?

If you can do **all** of these without looking things up, skip to [Phase 08](../Phase08_Agentic_Infrastructure/README.md):

- Draw detect → decide → act → verify and name where humans stay in the loop
- Explain why **suggest mode** should ship before **auto mode**
- Name three guardrails (allowlist, cooldown, kill switch, blast-radius limit — pick any three)
- Describe an alert you'd *never* auto-remediate on day one
- Say what belongs in an remediation audit log
- Sketch how you'd stop a runaway healer at 3am

Otherwise stay here. Phase 08 adds tool-using agents — you want boring, safe loops first.

---

## Learning objectives

By the end of Phase 07, answer **yes** to all of these:

- [ ] Reduce at least one class of noisy alerts (or explain how you would)
- [ ] Implement suggest-then-auto for one safe action (e.g. restart)
- [ ] Enforce an action allowlist and a kill switch
- [ ] Verify after acting (don't assume the restart worked)
- [ ] Produce an audit trail another engineer can read cold
- [ ] Know when automation should refuse and page a human instead

---

## Topics

Work in order. Don't jump to "fully autonomous" before suggest mode is boring.

### 1. AIOps without the hype

Ignore the vendor slides. For this phase, AIOps means: **use signals + policy to close the ops loop**. ML anomaly models are optional candy. A clear state machine with guardrails is the meal.

```
Signal (alert / probe)
   → Decide (policy: suggest vs auto, allowlist)
   → Act (restart / scale / rollback — only if allowed)
   → Verify (health / error rate)
   → Audit (who/what/when/why + outcome)
```

### 2. Noise first

If everything pages, nothing pages. Fix duplicate alerts, missing ownership, and flappy thresholds before you auto-restart anything. Automation on noise just fails faster.

→ [alert-noise cheatsheet](./cheatsheets/alert-noise.md)

### 3. The loop: detect → decide → act → verify

**Detect** can be Prometheus, a webhook, or (in the lab) an injected JSON alert.  
**Decide** is policy — not vibes.  
**Act** is a small, reversible change.  
**Verify** is mandatory; "we fired kubectl" is not success.

→ [detect-decide-act cheatsheet](./cheatsheets/detect-decide-act.md)

### 4. Guardrails or it doesn't ship

Allowlisted actions. Cooldowns. Max retries. Environment scopes (dev first). Kill switch. Blast radius ("one service," not "the cluster"). If you can't turn it off quickly, you don't turn it on.

→ [guardrails cheatsheet](./cheatsheets/guardrails.md)

### 5. Audit trails

Postmortems love liars and hate mysteries. Log: alert id, decision (suggest/auto/skip), action, actor (healer version), result, verification. JSON lines are fine.

### 6. Operators & real hooks (stretch)

Kubernetes operators, Alertmanager webhooks, Argo rollouts — same loop, sharper tools. Learn the loop in Path A before you write a CRD.

---

## Capstone project

### Self-healing lab

**Starter:** [projects/self-healing-lab/](./projects/self-healing-lab/)

| Path | Needs | Outcome |
|---|---|---|
| **A — Mock (start here)** | Docker | Inject CrashLoop alert → suggest → auto restart → audit |
| **B — Cluster** | kind/k3d | Same ideas against a flappy Deployment (manual/scripted) |

**Already wired for Path A:** mock control plane, healer (suggest/auto), allowlist, kill switch, cooldown, audit log, smoke test.

**Your job:** run suggest first, prove auto recovers a service, prove the kill switch stops everything, and read the audit like a skeptic.

Full walkthrough → [projects/self-healing-lab/README.md](./projects/self-healing-lab/README.md)

---

## Ready for Phase 08?

Don't move on until you can do these **without googling**:

1. Explain the loop and where suggest mode sits  
2. Name your allowlist and kill switch for the lab  
3. Show an audit line from a real run  
4. Give one example of "detect but do not act"  
5. Say what you'd verify after a restart  

Phase 08 (agentic infra) adds LLMs that *choose tools*. You want those tools gated by the same instincts you build here.

---

## Resources

| Resource | What it's for |
|---|---|
| [Google SRE — Eliminating toil](https://sre.google/sre-book/eliminating-toil/) | Why automate carefully |
| [Kubernetes operators pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/) | Stretch: real controllers |
| [Alertmanager webhook receiver](https://prometheus.io/docs/alerting/latest/configuration/#webhook_config) | Hooking real alerts |
| Repo cheatsheets | Day-to-day lookup |

---

## Track your progress

```
[Phase 07] Starting — your-handle
[Phase 07] Done — your-handle
```

When Done, share: one audit log snippet (suggest + auto) and whether the kill switch test passed.

---

*← [Phase 06 — Platform Engineering](../Phase06_Platform_Engineering/README.md) | [Phase 08 — Agentic Infrastructure →](../Phase08_Agentic_Infrastructure/README.md)*
