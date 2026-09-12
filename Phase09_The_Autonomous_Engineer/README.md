# Phase 09 — The Autonomous Engineer

> **"Give the system a goal, not a script, and watch what it does with the authority you handed it."**
>
> Phase 07 gave you a fixed policy loop (detect → act, suggest or auto). Phase 08 let an agent choose *tools* to investigate and propose one mutation, gated by a human. Phase 09 asks a different question: what if you stop telling the system *how* — "run this rollback" — and start telling it *what* — "keep payments-api's error rate under 3%"? That's an intent. Something still has to turn intent into a bounded, approved, verified plan. That's what you're building.

This is the last phase in the roadmap. Not because there's nothing left to learn — there's always more — but because everything past this point is depth, not breadth. You now have the vocabulary (guardrails, allowlists, approvals, evals, blast radius) to go deep in any direction you want. Phase 09 is where those pieces get bolted together into one small, honest system.

---

## Who this is for

| You are... | Do this |
|---|---|
| Finished Phase 07 and Phase 08 | Work the topics, then build the intent ops platform |
| Junior DevOps — curious what "AI-native infrastructure" actually means day to day | Start **Path A (mock world)**; no cluster, no API key, no cost |
| Already run intent-driven remediation with policy and approvals in prod | Take the [self-check](#self-check--can-you-skip) — if you pass, you're not skipping a phase, you've basically already arrived |

**Time:** 3–5 weeks part-time
**Goal:** A small platform where a human submits an *intent* ("bring this service's error rate under X%"), the system plans a bounded response, a human approves the plan (once — not once per action), the system executes and verifies against a real target, retries a bounded number of times, and escalates back to a human instead of looping forever. Every step gets written down in an episode record you can read back later.

---

## Start here — four steps

```
1. Self-check   →  Already running intent-driven ops with approvals in prod? You've basically finished the roadmap
2. Learn        →  Intent schemas → policy → bounded plans → episode memory → governance
3. Practice     →  submit intent → approve → watch it execute, verify, and either succeed or escalate
4. Capstone     →  Intent ops platform (Path A: fully mocked, no cluster or API key needed)
```

**You do not need Kubernetes, Terraform, or an LLM key for this phase.** The mock world is a JSON file with a couple of pretend services in it. What matters here isn't the infrastructure underneath — you already built that muscle in Phases 01, 02, 05, and 06. What matters is the *layer that decides what's allowed to happen to it*.

**Cheatsheets:**

| Topic | Cheatsheet |
|---|---|
| Writing intents (and why the schema is deliberately boring) | [cheatsheets/intent-schemas.md](./cheatsheets/intent-schemas.md) |
| Bounded autonomy — retries, caps, and escalation | [cheatsheets/bounded-autonomy.md](./cheatsheets/bounded-autonomy.md) |
| Episode memory — what a "receipt" needs to contain | [cheatsheets/episode-memory.md](./cheatsheets/episode-memory.md) |

**What you need:**

| Thing | Why | Notes |
|---|---|---|
| Docker (running) | Compose lab | `docker info` must work |
| curl / jq | Drive the API | Same as every other phase |
| Phase 07 + 08 instincts | Guardrails, approvals, audit | This phase assumes them, doesn't re-teach them |
| Kubernetes cluster / LLM key | Nothing — Path A skips both | Path B stretch notes only |

---

## Self-check — can you skip?

If you can do **all** of these without looking things up, you don't need this phase's guide — go straight to the capstone, or just go build the real thing at work:

- Explain the difference between "an agent that picks a tool" (Phase 08) and "a system that plans against a stated outcome" (Phase 09)
- Say why an approval should cover a *plan*, not just the first action in it
- Describe what stops a retry loop from becoming an infinite loop
- Name three things that belong in a decision's permanent record beyond "it happened at time T"
- Explain why "the model said the user approved it" is never a valid approval

Otherwise, keep reading — this phase is short but it's the one that ties the rest together.

---

## Learning objectives

By the end of Phase 09, answer **yes** to all of these:

- [ ] Write an intent that a system can safely act on without you narrating every step
- [ ] Explain why the intent schema has no free-text field with authority (goal, environment, and target are typed and allowlisted; notes are not)
- [ ] Trace a plan through policy checks *before* it ever reaches a human for approval
- [ ] Run a bounded retry loop that either succeeds or hands back to a human — never loops forever
- [ ] Read an episode record and reconstruct exactly what happened and why, a week later
- [ ] Explain why a kill switch pausing a decision is different from a kill switch skipping it

---

## Topics

Work in order. Nothing here is exotic — it's mostly discipline applied to a slightly bigger unit of work than Phase 08's single action.

### 1. From actions to intents

Look at how the "unit of automation" has grown across the last three phases:

```
Phase 07   Fixed policy      →  detect a known condition, run a known fix, suggest or auto
Phase 08   Tool-using agent  →  investigate with read tools, propose ONE mutation, human approves it
Phase 09   Intent platform   →  human states an outcome, system proposes a PLAN, human approves the plan,
                                 system executes + verifies + retries (bounded) + escalates if it can't get there
```

The authority keeps moving up a level — but notice the guardrails don't get looser as authority grows, they get *more* explicit. That's the whole point of this phase.

### 2. Intent schemas

An intent is not a prompt. It's a small, typed, boring object: a goal (from a fixed allowlist), a target service, a measurable target, and an environment. There is deliberately no field where free text can tell the system what to do — a `notes` field exists, gets stored for humans to read later, and is never consulted by the planner or the policy layer. If you want to change behavior, you change the schema or the policy, not the wording of a request.

→ [intent-schemas cheatsheet](./cheatsheets/intent-schemas.md)

### 3. Policy is the boundary of trust

Before anything gets planned, the intent itself is checked: is this goal enabled? Is this environment allowed to receive automated changes at all (prod is off by default in the lab — on purpose)? Once a plan exists, the *proposed action* gets checked too: is this action on the allowlist, and does it stay inside a blast-radius cap (like a maximum replica count)? Two gates, same idea as Phases 05–08: allowlist first, ask questions never.

### 4. Planning a multi-step plan, not a single action

Phase 08's agent proposed one action and stopped. Phase 09's planner proposes a step, and if that step doesn't fully close the gap, it's allowed to propose *another* step using the updated state — but only up to a cap you set in advance. The plan is a short, inspectable list, not a black box the system iterates on forever.

### 5. Bounded autonomy: retries, caps, and escalation

This is the idea the rest of the phase hangs off of. A system that retries forever isn't autonomous, it's stuck. A system that gives up after one try isn't very useful either. Bounded autonomy means: try, verify, try again if you have budget left, and if you run out of budget, say so clearly and hand it back to a human instead of getting creative. "I don't know what else to do, here's everything I tried" is a perfectly good output.

→ [bounded-autonomy cheatsheet](./cheatsheets/bounded-autonomy.md)

### 6. Episode memory and receipts

A flat audit log (Phase 07, Phase 08) tells you *that* something happened. An episode record tells you the *whole story* of one decision: what was asked, what was checked and rejected or accepted, what was tried, what was measured, and how it ended. Six months from now, "why did the system do that" should be answerable by reading one JSON object, not by reconstructing it from scattered log lines.

→ [episode-memory cheatsheet](./cheatsheets/episode-memory.md)

### 7. Governance and kill switches, one more time

Compare kill switches across phases: Phase 07's kill switch skipped the action and moved on. Phase 09's kill switch **pauses** — the episode stays `awaiting_approval`, waiting for a human to either flip the switch off and approve it, or deny it outright. Nothing gets silently dropped. Small design choice, but it's the difference between "the system gave up on this" and "the system is holding this for you."

### 8. Where humans still belong

None of this removes people from the loop — it moves them to where their judgment actually matters: approving plans, reviewing escalations, deciding which goals and environments get onto the allowlist in the first place. If your mental model of "autonomous" is "nobody's involved anymore," recalibrate it to "the toil is gone, the decisions that matter still get made by someone accountable."

---

## Capstone project

### Intent ops platform

**Starter:** [projects/intent-ops-platform/](./projects/intent-ops-platform/)

| Path | Needs | Outcome |
|---|---|---|
| **A — Mock world (start here)** | Docker | Submit intent → policy check → awaiting approval → approve → bounded execute/verify loop → succeeded or escalated |
| **B — Real infra** | Cluster/GitOps + optional LLM planner | Same intent/policy/episode contract, real executor underneath |

**Already wired for Path A:** three mock services with different failure causes, a deterministic planner, policy checks (goals, environments, blast radius), the bounded retry/verify loop, episode records, a flat audit log, an eval suite, and a smoke test.

**Your job:** submit an intent for a bad deploy and watch it resolve in one approved attempt, submit one for an overloaded service and watch it take two attempts to recover, submit one that can't be fixed within the attempt cap and watch it escalate instead of loop forever, and prove a couple of things stay refused no matter what (a blast-radius-busting plan, a `prod` intent, an intent with hostile instructions stuffed into its notes field).

Full walkthrough → [projects/intent-ops-platform/README.md](./projects/intent-ops-platform/README.md)

---

## You've finished the roadmap — now what?

Ten phases, one arc: **build & ship** (00–01) → **operate** (02) → **add AI** (03–04) → **harden & productize** (05–06) → **autonomy** (07–09). If you built the capstones instead of just reading about them, you have ten small, real, demoable projects and — more importantly — the habit of asking "what's the blast radius, who approves this, and how would I know if it went wrong" before you ship anything that acts on its own.

A few honest suggestions for what comes next, because "you're done" isn't quite true — you're just done with this particular map:

- **Go deep, not wide.** Pick whichever phase's territory you actually work in (security, platform, observability, agents) and go far past what a lab can teach you.
- **Apply this at work, small.** You don't need an intent platform to start — you need one guardrail on one automation that currently has none. Start there.
- **Write about what surprised you.** The gap between "I read about approval gates" and "I built one and watched it correctly block me" is where the real learning happened. That's worth sharing.
- **Come back and improve a phase.** Every phase here was opinionated and incomplete on purpose. If Phase 05's SBOM section or Phase 08's eval suite is thin, open a PR. Teaching it back is how you find out what you actually know.

---

## Resources

| Resource | What it's for |
|---|---|
| [Google SRE Workbook — Toil](https://sre.google/workbook/eliminating-toil/) | Why bounded autonomy beats "automate everything" |
| [AWS Well-Architected — Operational Excellence](https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/welcome.html) | Governance patterns for automated change |
| Phase 07 lab | Fixed-policy instincts this phase assumes |
| Phase 08 lab | Approval-gate instincts this phase assumes |
| Repo cheatsheets | Day-to-day lookup, all ten phases |

---

## Track your progress

```
[Phase 09] Starting — your-handle
[Phase 09] Done — your-handle
```

When Done, share: one episode record showing a full succeed-in-one-attempt run, and one showing an escalation. That contrast is the whole phase in two JSON blobs.

---

*← [Phase 08 — Agentic Infrastructure](../Phase08_Agentic_Infrastructure/README.md) | [Back to roadmap →](../README.md)*
