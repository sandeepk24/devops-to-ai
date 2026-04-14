# Phase 03 — AI-Augmented DevOps

> **"The best DevOps engineers of 2026 aren't the ones who know the most tools. They're the ones who know how to think alongside AI."**
>
> This is the turning point of the roadmap. Everything before this phase was about learning how infrastructure works. Everything after this phase is about building infrastructure that thinks. Phase 03 is the bridge — it's where you learn to use AI as a force multiplier in your daily work, before you learn to build AI systems in Phases 04–06.

---

## What this phase is

AI-augmented DevOps means using AI tools to do your existing job dramatically faster and better — not replacing your skills, but amplifying them. A senior engineer with AI tools outperforms a team of junior engineers without them. That gap is only going to grow.

This phase covers two things:

1. **Using AI in your daily DevOps workflow** — coding assistants, prompt engineering, AI-powered pipelines
2. **Building AI-powered operational tools** — incident bots, automated runbooks, ChatOps integrations

By the end of this phase you'll have built a real AI-powered incident response system that would genuinely save a team hours per week.

**Estimated time:** 4–5 weeks  
**Target audience:** Anyone who completed Phase 02 or works as a DevOps/SRE engineer today  
**Skippable if:** You've built production LLM integrations, written prompt engineering guidelines for a team, and deployed AI-powered operational tooling professionally

---

## Learning objectives

When you finish this phase, you should be able to answer yes to all of these:

- [ ] Can you write a prompt that reliably generates correct Terraform, GitHub Actions, or Kubernetes YAML from a natural language description?
- [ ] Can you explain why a vague prompt produces bad infrastructure code — and fix it?
- [ ] Can you build a GitHub Actions pipeline that uses an LLM to review PRs and flag issues?
- [ ] Can you build a Slack bot that queries logs, metrics, and traces to diagnose an incident?
- [ ] Can you explain the difference between zero-shot, few-shot, and chain-of-thought prompting — and when to use each?
- [ ] Can you use the Claude or OpenAI API to build a tool that takes structured input and returns actionable output?
- [ ] Can you evaluate whether an LLM output is trustworthy enough to act on automatically?

If you can say yes to all seven, you're ready for Phase 04.

---

## Topics

### 1. The AI-augmented engineer mindset

Before touching any tools, understand the shift. AI doesn't replace your expertise — it replaces the time you spend on repetitive translation tasks: turning intentions into code, turning alerts into summaries, turning logs into diagnoses. Your job becomes higher-order: deciding what to build, evaluating what AI produces, and knowing when to trust it.

**The three modes of AI assistance:**

```
Mode 1 — Generate        "Write me a Terraform module for an S3 bucket with versioning"
                         You review, you own it. AI is a fast first draft.

Mode 2 — Analyse         "Here are 500 lines of logs from a failing pod. What's wrong?"
                         AI processes at scale. You validate the conclusion.

Mode 3 — Automate        "When this alert fires, query logs, generate a summary, post to Slack"
                         AI acts autonomously within a defined scope. You design the guardrails.
```

**What AI is genuinely good at in DevOps:**
- Generating boilerplate — Dockerfiles, Terraform, CI pipeline YAML, Helm charts
- Explaining error messages and stack traces
- Summarising long log files and incident timelines
- Writing documentation from code
- Translating between tools — "convert this Jenkins pipeline to GitHub Actions"
- Generating test cases for infrastructure code
- Drafting runbooks from incident history

**What AI is still bad at:**
- Understanding your specific environment and constraints
- Security-sensitive decisions (always review IAM policies, network rules)
- Anything requiring real-time data it doesn't have
- Making final operational decisions — that's always a human

---

### 2. Prompt engineering for DevOps

Prompt engineering is the skill of communicating with LLMs precisely enough to get useful output. For DevOps work, this means writing prompts that produce correct, safe, production-ready infrastructure code and operational analysis.

**The anatomy of a good DevOps prompt:**

```
[Context]    What environment, constraints, and conventions apply
[Task]       Exactly what you want the AI to produce
[Format]     How you want the output structured
[Guardrails] What to avoid or flag
```

**Example — bad prompt vs good prompt:**

```
# Bad prompt (too vague)
"Write a Kubernetes deployment"

# Good prompt (specific context + constraints + format)
"Write a Kubernetes Deployment manifest for a Python FastAPI application with these requirements:
- Image: ghcr.io/myorg/payments-service:latest
- 3 replicas
- Resource limits: 500m CPU, 512Mi memory. Requests: 100m CPU, 128Mi memory
- Liveness probe: GET /health, initial delay 10s, period 30s
- Readiness probe: GET /ready, initial delay 5s, period 10s
- Environment variables from a ConfigMap named payments-config
- Runs as non-root user (UID 1000)
- Rolling update strategy with maxSurge 1, maxUnavailable 0

Output only the YAML manifest, no explanation."
```

**Prompting techniques:**

**Zero-shot** — ask directly, no examples
```
"Explain what this Terraform error means and how to fix it: [error]"
```

**Few-shot** — give examples of what good output looks like
```
"Convert these alert rules to the new format.

Example input:
  - alert: HighCPU
    expr: cpu_usage > 80

Example output:
  - alert: HighCPU
    expr: cpu_usage_percent > 80
    for: 5m
    labels:
      severity: warning

Now convert these: [your rules]"
```

**Chain-of-thought** — ask AI to reason step by step before answering
```
"A pod is stuck in Pending state. Before giving me the fix, walk through the possible causes
in order of likelihood, check each one against these pod events: [events].
Then tell me the most likely cause and the exact kubectl command to fix it."
```

**Role prompting** — give AI a specific expert persona
```
"You are a senior SRE at a fintech company with strict compliance requirements.
Review this Terraform IAM policy and flag any permissions that violate least-privilege.
Be specific about which permissions are too broad and suggest alternatives."
```

**Recommended resources:**
- [Anthropic prompt engineering guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [OpenAI prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Prompt injection attacks](https://learnprompting.org/docs/prompt_hacking/injection) — understand the security risks

---

### 3. AI-assisted coding in your daily workflow

The coding assistants — GitHub Copilot, Cursor, Claude — are the fastest way to see ROI from AI in DevOps. The engineers who get the most value aren't the ones who use them blindly, they're the ones who know how to steer them.

**What to cover:**

**GitHub Copilot / Cursor:**
- Tab completion vs inline chat vs multi-file edits
- Writing comments that guide Copilot to the right output
- Using Copilot for Terraform — it's exceptionally good at resource boilerplate
- Copilot for writing tests — describe what you want to test, get the test
- When to reject suggestions — learning to read AI output critically

**Claude / ChatGPT for DevOps:**
- Pasting error messages and getting structured diagnoses
- "Explain this like I'm debugging it at 3am" — getting operational context
- Converting between formats: Ansible → Terraform, Jenkins → GitHub Actions
- Generating multiple variations — "give me 3 different approaches to this"
- Asking for the security implications of infrastructure code

**Building personal AI workflows:**
- Shell aliases that pipe commands to AI: `kubectl describe pod failing-pod | ai-explain`
- A `git diff | ai-review` alias that reviews your changes before committing
- An `explain-error` function that formats compiler/runtime errors for LLM input

**Recommended resources:**
- [GitHub Copilot docs](https://docs.github.com/en/copilot)
- [Cursor docs](https://cursor.sh/docs)

---

### 4. AI in CI/CD pipelines

Embedding AI into your pipelines moves assistance from manual to automatic. Instead of remembering to ask an AI to review your code, the pipeline does it on every PR.

**What to cover:**

**AI code review in CI:**
- Using the Claude or OpenAI API in a GitHub Actions step
- Reviewing Terraform plans for security issues and cost implications
- Reviewing Kubernetes manifests for best practice violations
- Posting AI review comments directly to GitHub PRs via the API

**AI-generated test coverage:**
- Using LLMs to generate Terratest cases from Terraform modules
- Generating unit tests for Python automation scripts
- Identifying untested code paths and generating tests for them

**AI-powered documentation:**
- Automatically generating module documentation from Terraform code
- Generating runbooks from deployment pipeline definitions
- Keeping `CHANGELOG.md` updated from conventional commits

**Security scanning with AI:**
- Combining static analysis (Trivy, Checkov) with AI explanation
- "This Trivy scan found 3 HIGH vulnerabilities — explain each and prioritise fixes"
- AI-assisted CVE triage: is this vulnerability actually exploitable in our context?

**Example — AI PR review GitHub Action:**

```yaml
name: AI code review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Get diff
        id: diff
        run: |
          git diff origin/main...HEAD > diff.txt
          echo "diff_size=$(wc -c < diff.txt)" >> $GITHUB_OUTPUT

      - name: AI review
        if: steps.diff.outputs.diff_size > 0
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python .github/scripts/ai_review.py
```

---

### 5. LLM-powered incident response

This is where AI moves from assistant to collaborator. When an alert fires at 2am, the first 10 minutes are usually spent gathering context — pulling logs, checking metrics, reading recent deploys. An AI bot can do all of that in seconds.

**The anatomy of an AI incident response system:**

```
Alert fires (PagerDuty / Alertmanager)
        ↓
Bot receives webhook
        ↓
Bot gathers context automatically:
  - Recent logs from Loki (last 30 mins, error level)
  - Metrics from Prometheus (error rate, latency, saturation)
  - Recent deployments (git log or ArgoCD history)
  - Pod events from Kubernetes
        ↓
Bot sends context to LLM with a structured prompt:
  "Given these logs, metrics, and recent changes,
   what is the most likely root cause?
   What are the top 3 things to check?
   Which runbook applies?"
        ↓
LLM returns structured analysis
        ↓
Bot posts to Slack incident channel:
  - Summary of what's wrong
  - Likely root cause
  - Recommended next steps
  - Link to relevant runbook
        ↓
On-call engineer joins with context already assembled
```

**What to cover:**

- Designing prompts for incident analysis — what context to include, how to structure it
- Handling rate limits and timeouts gracefully (incidents happen at bad times)
- Structured output — getting JSON back from LLMs, not freeform text
- Knowing when to trust AI diagnosis vs escalate to a human
- Feedback loops — collecting engineer ratings on AI suggestions to improve prompts

---

### 6. ChatOps — LLM bots in Slack and Teams

ChatOps is the practice of doing operational work through chat. With LLMs, your Slack bot goes from "show me pod status" to "what's wrong with payments and what should I do about it?"

**What to cover:**

- Slack Bot API — event subscriptions, slash commands, interactive components
- Building a bot that responds to natural language operational queries
- Slash commands for common ops tasks: `/deploy`, `/rollback`, `/status`
- Modal forms for structured actions (safer than freeform text)
- Approval workflows — bot proposes action, human approves, bot executes
- Audit logging — every action taken through the bot, by whom, when

**Example interactions your bot should handle:**

```
Engineer: "what's wrong with the payments service?"
Bot: queries Prometheus + Loki, asks LLM, responds:
     "Payments service is showing elevated error rate (4.2%, threshold 5%).
      Root cause appears to be timeouts to the Stripe API — 47 timeout errors
      in the last 30 minutes. No recent deployments. Recommend checking
      Stripe status page and reviewing circuit breaker configuration."

Engineer: "show me the last 5 deploys to production"
Bot: queries ArgoCD or git log, formats response as a table

Engineer: "rollback payments-service to the previous version"
Bot: shows what the rollback would do, asks for confirmation
     After approval: executes ArgoCD rollback, confirms success
```

**Recommended resources:**
- [Slack API docs](https://api.slack.com/docs)
- [Slack Bolt for Python](https://slack.dev/bolt-python/concepts) — the easiest way to build Slack bots

---

### 7. Evaluating and trusting AI output

This is the most important section in the phase and the one most people skip. AI makes confident-sounding mistakes. In DevOps, a confident mistake can take down production.

**A framework for trusting AI output:**

```
Low stakes — auto-trust:
  Documentation, explanations, first drafts of non-critical code
  → Review quickly, apply if it looks reasonable

Medium stakes — verify before applying:
  Terraform code, pipeline YAML, Kubernetes manifests
  → Run terraform plan, dry-run the pipeline, validate the manifest
  → Check for obvious security issues (overly permissive IAM, exposed ports)

High stakes — always human review:
  IAM policies and security group rules
  Database schema changes
  Production deployment approvals
  Anything that can't be easily rolled back
  → AI can assist and draft, but a human must sign off
```

**Red flags in AI-generated infrastructure code:**
- IAM policies with `*` actions or resources
- `0.0.0.0/0` in security group ingress rules
- Hardcoded credentials or secrets (even as examples)
- `force_destroy = true` on storage resources
- Missing resource limits on Kubernetes containers
- `privileged: true` in pod security contexts

**Prompt injection in operational contexts:**  
If your AI bot reads logs or user input before passing to an LLM, an attacker can craft log entries that manipulate the LLM. Always sanitise inputs and never give AI bots the ability to execute arbitrary commands.

---

## Capstone project

### AI-powered incident response system

Build a Slack bot that automatically assembles incident context and provides AI-powered diagnosis when an alert fires. This is the project that will genuinely impress in interviews — it's a real system that solves a real problem.

---

**Architecture:**

```
Alertmanager/Prometheus
        ↓ webhook
  Incident Bot (Python)
        ↓ queries
  ┌─────────────────────────┐
  │  Loki  Prometheus  k8s  │  ← context gathering
  └─────────────────────────┘
        ↓ structured prompt
    Claude / OpenAI API
        ↓ analysis
    Slack channel
        ↓ human approves
  Optional: ArgoCD rollback
```

---

**Part 1 — Build the incident bot**

The bot lives in `projects/incident-response-bot/`. It must:

- [ ] Expose a `/webhook` endpoint that receives Alertmanager webhook payloads
- [ ] On receiving an alert, automatically gather:
  - Last 30 minutes of error-level logs from Loki for the affected service
  - Current error rate and p99 latency from Prometheus for the affected service
  - Last 5 deployments from ArgoCD or git log
  - Recent pod events from Kubernetes (`kubectl get events`)
- [ ] Send assembled context to the Claude API with a structured prompt
- [ ] Post the AI analysis to a Slack channel with:
  - Alert name and severity
  - AI-generated summary (2–3 sentences)
  - Top 3 likely causes (ranked)
  - Recommended immediate actions
  - Link to the relevant runbook (if one exists)
- [ ] Handle failures gracefully — if Loki is down, post without logs, don't crash

---

**Part 2 — Add the AI PR review pipeline**

- [ ] Add a GitHub Actions workflow that runs on every PR
- [ ] The workflow diffs the PR, sends it to the Claude API with a review prompt
- [ ] Posts the review as a PR comment via the GitHub API
- [ ] The review must flag: security issues, missing resource limits, hardcoded values, and obvious bugs

---

**Part 3 — Add slash commands to the bot**

Extend the Slack bot with these slash commands:

- [ ] `/status <service>` — shows current health (error rate, latency, pod count)
- [ ] `/logs <service> <minutes>` — shows last N minutes of error logs
- [ ] `/deploys <service>` — shows last 5 deployments with timestamps and authors
- [ ] `/rollback <service>` — shows what a rollback would do, asks for confirmation before executing

---

**Part 4 — Prompt library**

Create a `prompts/` folder with the prompt templates your bot uses, as plain text files. Each prompt should have:
- A comment explaining what it does
- The actual prompt template with `{variable}` placeholders
- An example of good output

This matters because prompts are code — they should be version controlled, reviewed, and improved over time.

---

**Definition of done:**

- [ ] Bot receives Alertmanager webhook and posts to Slack within 30 seconds
- [ ] Slack message includes AI-generated diagnosis with at least one specific recommendation
- [ ] `/status` slash command works and returns real data
- [ ] AI PR review posts a comment on a test PR
- [ ] All prompts are in `prompts/` as version-controlled files
- [ ] Bot handles downstream failures gracefully (Loki down, Prometheus timeout)
- [ ] A `README.md` explains how to run the bot locally and how to deploy it

**Stretch goals:**
- Add feedback buttons to the Slack message ("Was this helpful? 👍 👎") and log responses
- Build a weekly digest: "Last week's incidents — AI summary of patterns and recurring issues"
- Add `/ask` command: freeform natural language question about your infrastructure

---

## How to know you're ready for Phase 04

Do not move on until you can do all of the following:

- Write a prompt that generates a correct, production-safe Kubernetes Deployment manifest for a service you describe
- Explain what few-shot prompting is and give an example of when it produces better results than zero-shot
- Build a Python script that calls the Claude or OpenAI API, sends context, and parses a structured JSON response
- Identify at least three red flags to look for in AI-generated Terraform or Kubernetes code
- Explain prompt injection and why it matters specifically in operational AI bots
- Demo a working Slack command that queries real infrastructure data and returns a useful response

If any of those trips you up, go back and spend more time. Phase 04 involves running actual LLM workloads as infrastructure — you need to be comfortable with the API layer before you manage the GPU layer.

---

## Resources summary

| Resource | Type | Cost | Link |
|---|---|---|---|
| Anthropic prompt engineering guide | Docs | Free | [docs.anthropic.com](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) |
| OpenAI prompt engineering guide | Docs | Free | [platform.openai.com/docs](https://platform.openai.com/docs/guides/prompt-engineering) |
| Claude API docs | Docs | Free | [docs.anthropic.com](https://docs.anthropic.com/en/api/getting-started) |
| OpenAI API docs | Docs | Free | [platform.openai.com](https://platform.openai.com/docs/api-reference) |
| GitHub Copilot docs | Docs | Free | [docs.github.com/copilot](https://docs.github.com/en/copilot) |
| Slack Bolt for Python | Docs | Free | [slack.dev/bolt-python](https://slack.dev/bolt-python/concepts) |
| Prompt injection explained | Article | Free | [learnprompting.org](https://learnprompting.org/docs/prompt_hacking/injection) |
| LangChain docs | Docs | Free | [python.langchain.com](https://python.langchain.com/docs/get_started/introduction) |

---

## Community & tracking

Open an issue with `[Phase 03] Starting` when you begin and `[Phase 03] Done` when you complete the capstone. When you post Done, share:
- A screenshot of your Slack bot responding to an alert
- A screenshot of the AI PR review comment on a pull request
- The GitHub repo link
- The prompt you're most proud of — paste it in the issue

---

*← [Phase 02 — Cloud Native Operations](../Phase02_Cloud_Native_Operations/README.md) | [Phase 04 — MLOps & LLMOps →](../Phase04_MLOps_LLMOps/README.md)*
