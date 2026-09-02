# Phase 09 — The Autonomous Engineer

> **"The destination isn't 'no humans.' It's humans declaring intent — and systems that carry it out within policy, with receipts."**
>
> This is the end of the roadmap. You combine everything: delivery, observability, security, platform product thinking, AIOps loops, and agents — into an **intent-driven AI ops platform**. Not a slide deck. A working thin slice you can demo.

---

## Who this is for

| You are... | Do this |
|---|---|
| Worked through Phases 02–08 (or equivalent experience) | Build the intent platform capstone |
| Strong engineer aiming at staff/platform + AI ops roles | Treat this as your portfolio centerpiece |
| Already run intent/agents in production | Use this as a checklist; skip what you can prove |

**Time:** 6–8 weeks part-time  
**Goal:** Natural-language intent → plan → (approval) → change → verify → learn — with auditability.

**Prereqs:** Phase 07 + 08 conceptually required. Skipping earlier phases is fine if you can pass their self-checks.

---

## Start here — four steps

```
1. Self-check     →  Already built this at work? Document and skip
2. Learn          →  Intent models → control planes → policy → feedback
3. Practice       →  One intent type end-to-end (e.g. "reduce error rate")
4. Capstone       →  Minimal AI ops platform demo
```

---

## Self-check — can you skip?

- Translate a business/reliability intent into measurable SLIs and allowed actions
- Architecture: intake → planner → policy check → executor → verifier → memory
- Prove every change has an audit receipt (who/what/why/evidence)
- Show evals that prevent unsafe intents ("delete all prod") from executing
- Explain human accountability when the agent is wrong
- Know when to leave autonomy off

---

## Learning objectives

- [ ] Define an intent schema (goal, constraints, environment, urgency)
- [ ] Plan multi-step changes with explicit pre/post conditions
- [ ] Enforce policy (Phase 05/06) before execution
- [ ] Reuse agents/tools from Phase 08 inside a platform API
- [ ] Verify outcomes against SLOs, not just "command succeeded"
- [ ] Store outcomes for future retrieval (success/failure memory)
- [ ] Present a demo narrative a hiring manager follows in 10 minutes

---

## Topics

### 1. What "autonomous engineer" actually means

Not sci-fi. A system that:
1. Accepts goals in human language or tickets
2. Grounds on live state + docs
3. Proposes a plan
4. Executes only what's allowed
5. Checks whether the goal was met
6. Records the episode for learning

Humans still own policy, risk appetite, and exceptions.

### 2. Intent schemas

Example:

```yaml
intent: restore_reliability
service: payments-api
slo: success_rate >= 99.5%
window: 30m
constraints:
  - no_database_migrations
  - prod_requires_approval
allowed_actions: [restart, rollback, scale_up]
```

Ambiguous intents ("make it better") must be rejected or clarified.

### 3. Control plane architecture

```
UI / Slack / API
      ↓
Intent API (authn/z)
      ↓
Planner (LLM + rules)
      ↓
Policy engine (OPA/Kyverno/custom)
      ↓
Executor (GitOps PR, Argo sync, cloud APIs)
      ↓
Verifier (Prom/SLO checks)
      ↓
Episode store (RAG memory)
```

Prefer **PR-based execution** (open GitOps PR) over direct cluster mutation when you can — reviewability is a feature.

### 4. Policy & governance

- Environments, change windows, blast-radius limits
- Separation of duties (planner ≠ approver)
- Break-glass with mandatory post-incident review
- Compliance mapping (who approved prod rollback?)

### 5. Feedback & learning

- Did verification pass?
- Was the plan edited by a human? Capture diffs
- Weekly digest: intents attempted, success rate, unsafe blocks
- Feed failures into eval suites (Phase 08)

### 6. Product & org reality

- Start with one team and one intent class
- Platform SLO for the autonomy service itself
- On-call for the automator — irony accepted
- Communication: engineers must trust the system or they'll bypass it

### 7. Ethics & accountability

When the agent rolls back prod wrongly, **a human still owns the outcome**. Design for that: clear identity, approvals, and easy disable.

---

## Capstone

### Intent-driven AI ops platform (thin slice)

Pick **one** intent class, e.g. `mitigate_high_error_rate` for a demo service.

**Build:**
1. Intent API (`POST /intents`) with auth token
2. Planner that outputs a structured plan (JSON)
3. Policy check (reject disallowed actions)
4. Execution path: suggest-only **and** GitOps PR or approved webhook action
5. Verifier polling golden signals for 10–15 minutes
6. Episode record stored and queryable ("what did we do last time?")
7. Demo script + architecture diagram in README

**Definition of done:**
- [ ] Happy path: injected failure → intent → plan → approve → recover → verify pass
- [ ] Unsafe intent blocked with a clear reason
- [ ] Full audit trail exportable
- [ ] Kill switch stops execution globally
- [ ] 10-minute demo video or written walkthrough

**Stretch:** UI; multi-intent catalog; automatic RFC comment on the GitOps PR; cost/latency dashboard for the planner.

> Starter planned at `projects/intent-ops-platform/`.

---

## After Phase 09

You've walked the path from shell basics to intent-driven systems. Keep going by:
- Running your platform for a real team (even a small one)
- Hardening evals and policy packs
- Contributing improvements back to this repo's Phase 05–09 starters as they land

The metric that matters: **other engineers trust your paved, autonomous paths enough to use them.**

---

## Resources

| Resource | Why |
|---|---|
| SRE books (Google) | Reliability as product |
| Team Topologies | How platform + stream teams interact |
| Your Phase 03–08 projects | Components to assemble |
| OWASP LLM Top 10 + supply-chain guides | Keep autonomy safe |

---

## Track your progress

```
[Phase 09] Starting — your-handle
[Phase 09] Done — your-handle
```

Share architecture + demo when you open Done.

---

*← [Phase 08 — Agentic Infrastructure](../Phase08_Agentic_Infrastructure/README.md) | [Back to roadmap →](../README.md)*
