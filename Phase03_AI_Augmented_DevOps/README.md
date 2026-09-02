# Phase 03 — AI-Augmented DevOps

> **"The best DevOps engineers aren't the ones who know the most tools. They're the ones who know how to think alongside AI."**
>
> Phases 00–02 taught you to build and operate infrastructure. Phase 03 is the bridge: use AI to do that work faster — then build small AI tools that help on-call. Phases 04–06 go deeper into *running* AI as infrastructure.

---

## Who this is for

| You are... | Do this |
|---|---|
| Finished Phase 02 (or comfortable with Prom/Loki and basic Python APIs) | Work the topics, then the capstone |
| Junior DevOps — use ChatGPT/Copilot already, never shipped an AI bot | Focus on prompts + trust, then build the bot with **mock mode** first |
| Already ship LLM-backed ops tools in production | Take the [self-check](#self-check--can-you-skip) — skip to Phase 04 if you pass |

**Time:** 4–5 weeks part-time  
**Goal:** Write prompts that produce *safe* infra output, and ship a small bot that turns an alert into a useful diagnosis.

---

## Start here — four steps

```
1. Self-check     →  Already building LLM ops tooling? Maybe skip to Phase 04
2. Learn          →  Mindset → prompts → daily AI → CI review → trust
3. Practice       →  Write prompts, run the mock bot, then wire real Prom/Loki
4. Capstone       →  Incident bot + AI PR review (required before Phase 04)
```

**You do not need Slack or a full cluster on day one.** The capstone has a **mock mode** that prints analysis to your terminal. Add Slack / Phase 02 observability when you're ready.

**Cheatsheets:**

| Topic | Cheatsheet |
|---|---|
| Prompt patterns for DevOps | [cheatsheets/prompt-engineering.md](./cheatsheets/prompt-engineering.md) |
| When to trust AI output | [cheatsheets/trusting-ai-output.md](./cheatsheets/trusting-ai-output.md) |

**What you need:**

| Thing | Why | Notes |
|---|---|---|
| Python 3.11+ | Run the bot | Same as Phase 01/02 |
| Anthropic or OpenAI API key | LLM calls | Start with a small paid/credits account |
| Phase 02 stack (optional at first) | Real logs/metrics | Mock mode works without it |
| Slack workspace (optional) | Post alerts to a channel | Console output is fine for Path A |

---

## Self-check — can you skip?

If you can do **all** of these without looking things up, skip to [Phase 04](../Phase04_MLOps_LLMOps/README.md):

- Write a prompt that generates a production-safe Kubernetes Deployment (limits, probes, non-root)
- Explain zero-shot vs few-shot vs chain-of-thought with a DevOps example for each
- Call an LLM API from Python and parse structured JSON back
- Name three red flags in AI-generated Terraform or K8s YAML
- Explain prompt injection and why it matters when bots read logs
- Sketch how an alert webhook → context gather → LLM → Slack flow works

Otherwise stay here. Phase 04 assumes you're comfortable with the **API layer** before you run GPUs.

---

## Learning objectives

By the end of Phase 03, answer **yes** to all of these:

- [ ] Write prompts that reliably produce correct Terraform / Actions / K8s YAML
- [ ] Fix a vague prompt that produces bad infra code
- [ ] Build a CI step that reviews a PR with an LLM
- [ ] Build (or complete) a bot that diagnoses an alert with logs + metrics context
- [ ] Explain zero-shot, few-shot, and chain-of-thought — and when each helps
- [ ] Call Claude or OpenAI from Python and get structured output
- [ ] Decide when AI output is safe to apply vs needs a human

---

## Topics

Work in order. Don't jump to the Slack bot before you can write a good prompt — you'll just automate bad questions.

### 1. Mindset — AI as a force multiplier

AI doesn't replace knowing Linux, K8s, or Prometheus. It replaces the *boring translation work*: intention → YAML, logs → summary, alert → first hypothesis.

```
Generate   →  "Draft this Terraform"     — you review and own it
Analyse    →  "What's wrong in these logs?" — you validate the conclusion
Automate   →  "On alert, gather context + post diagnosis" — you design guardrails
```

**Good at:** boilerplate, explaining errors, summarising logs, translating Jenkins→Actions, drafting runbooks.  
**Bad at:** your exact environment, security judgment, final "ship to prod" decisions.

Your job shifts up a level: decide what to build, evaluate what AI produced, know when to trust it.

---

### 2. Prompt engineering for DevOps

Vague prompts produce vague (or dangerous) infra. The pattern that works:

```
[Context]     env, constraints, conventions
[Task]        exactly what to produce
[Format]      YAML only / JSON schema / bullet list
[Guardrails]  no *, no 0.0.0.0/0, non-root, resource limits…
```

**Bad:** `Write a Kubernetes deployment`  
**Good:** image, replicas, requests/limits, probes, ConfigMap, non-root, rolling update strategy, "output YAML only."

Techniques you'll use constantly:
- **Zero-shot** — straightforward explain/fix
- **Few-shot** — show one example of the format you want
- **Chain-of-thought** — "reason through causes before the fix" (debugging)
- **Role** — "senior SRE at a regulated fintech…" for security reviews

→ [Prompt cheatsheet](./cheatsheets/prompt-engineering.md)

**Try this:** Take a real service from Phase 01/02. Ask an LLM for a Deployment. Reject anything missing limits or running as root. Rewrite the prompt until the output is something you'd actually merge.

---

### 3. AI in your daily workflow

Copilot / Cursor / Claude Chat are the fastest ROI. Steer them; don't rubber-stamp.

- Comments that describe intent beat hoping tab-complete guesses right
- Paste errors with "explain like I'm debugging at 3am"
- `git diff` → AI review before you open the PR
- Always ask: "what would break in production if this is wrong?"

---

### 4. AI in CI/CD

Move review from "when I remember" to "every PR."

Typical flow: checkout → diff → LLM review prompt → post comment on the PR. Flag security issues, missing limits, hardcoded secrets, obvious bugs. Capstone Part 2 does exactly this.

Keep it **advisory** at first — don't fail the build on AI opinion until you trust the prompts.

---

### 5. Incident response with LLMs

At 2am the first ten minutes are usually *gathering context*. A bot can do that in seconds:

```
Alertmanager webhook
    → fetch logs (Loki) + metrics (Prometheus) + deploys + pod events
    → structured prompt → LLM
    → Slack (or console): summary, likely cause, top 3 checks
```

Rules of the road:
- Never crash if Loki is down — post what you have
- Prefer JSON from the model, not free-form essays
- AI suggests; humans approve rollbacks

---

### 6. ChatOps (slash commands)

Once the webhook path works, add `/status`, `/logs`, `/deploys`, `/rollback`. Rollback must be **two-step** (show plan → confirm). Never auto-execute destructive actions from a model suggestion alone.

---

### 7. Trust — the part people skip

Confident nonsense takes down prod.

| Stakes | Rule |
|---|---|
| Low (docs, explanations) | Light review |
| Medium (Terraform, manifests) | `plan` / dry-run / validate |
| High (IAM, prod deploy, irreversible) | Human sign-off always |

**Red flags:** `*` IAM, `0.0.0.0/0`, hardcoded secrets, `force_destroy`, missing limits, `privileged: true`.

**Prompt injection:** if the bot feeds logs into an LLM, malicious log lines can try to hijack the model. Sanitize inputs; never let the bot run arbitrary shell from model output.

→ [Trust cheatsheet](./cheatsheets/trusting-ai-output.md)

---

## Capstone project

### AI-powered incident response bot

Build a bot that turns an Alertmanager webhook into a useful diagnosis. Interview gold — it's a real problem, not a toy.

**Starter:** [projects/incident-response-bot/](./projects/incident-response-bot/)

| Path | What you need | Outcome |
|---|---|---|
| **A — Local / mock (start here)** | API key only | Webhook → mock metrics/logs → LLM → terminal output |
| **B — Real observability** | Phase 02 Compose stack | Same bot, real Loki/Prometheus |
| **C — Slack + slash commands** | Slack app | Posts to `#incidents`, `/status` etc. |

**Parts:**
1. Webhook + context gather + LLM analysis (+ mock mode)
2. AI PR review GitHub Action
3. Slash commands (Path C)
4. Version-controlled prompts under `prompts/`

**Definition of done:**
- [ ] `curl` the webhook and get a diagnosis (console or Slack) within ~30s
- [ ] Diagnosis includes summary + at least one concrete next check
- [ ] Downstream failure (mock Loki down) does not crash the bot
- [ ] AI PR review posts a comment on a test PR
- [ ] Prompts live in `prompts/` as files you can diff in Git
- [ ] README explains Path A / B / C

Full walkthrough → [projects/incident-response-bot/README.md](./projects/incident-response-bot/README.md)

---

## Ready for Phase 04?

Don't move on until you can do these **without googling**:

1. Prompt a safe K8s Deployment for a service you describe
2. Explain few-shot with a DevOps example
3. Call an LLM API and parse JSON
4. List three AI infra red flags
5. Explain prompt injection for ops bots
6. Demo webhook → diagnosis (even if Slack is still mock/console)

Phase 04 is GPUs and model serving. Get comfortable calling models first.

---

## Resources

| Resource | What it's for |
|---|---|
| [Anthropic prompt guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) | Prompt patterns |
| [OpenAI prompt guide](https://platform.openai.com/docs/guides/prompt-engineering) | Same, OpenAI flavour |
| [Claude API](https://docs.anthropic.com/en/api/getting-started) / [OpenAI API](https://platform.openai.com/docs/api-reference) | Capstone calls |
| [Slack Bolt Python](https://slack.dev/bolt-python/concepts) | Path C Slack apps |
| [Prompt injection](https://learnprompting.org/docs/prompt_hacking/injection) | Security must-read |
| Repo cheatsheets | Day-to-day lookup |

---

## Track your progress

```
[Phase 03] Starting — your-handle
[Phase 03] Done — your-handle
```

When Done, share: bot output screenshot, PR review comment, and the prompt you're proudest of.

---

*← [Phase 02 — Cloud Native Operations](../Phase02_Cloud_Native_Operations/README.md) | [Phase 04 — MLOps & LLMOps →](../Phase04_MLOps_LLMOps/README.md)*
