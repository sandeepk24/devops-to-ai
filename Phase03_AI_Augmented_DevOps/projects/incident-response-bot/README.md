# Capstone: AI-powered incident response bot

> **Phase 03 project** — finish this before [Phase 04](../../../Phase04_MLOps_LLMOps/README.md).  
> Phase guide: [Phase 03 README](../../README.md)

When an alert fires, on-call usually spends the first ten minutes *gathering context*. This bot does that for you: webhook in → logs/metrics/deploys → LLM diagnosis → terminal or Slack.

---

## Paths (pick one, then level up)

| Path | Needs | What you prove |
|---|---|---|
| **A — Local mock** | API key *or* `LLM_PROVIDER=mock-llm` | Webhook → diagnosis in your terminal |
| **B — Real observability** | Phase 02 Compose (Prom + Loki) | Same bot, real context |
| **C — Slack ChatOps** | Slack app + token | Posts to `#incidents`, slash commands |

**Start with Path A.** Don't block yourself on Slack or a cluster.

---

## What's in this folder

```
incident-response-bot/
├── bot.py                 ← webhook + context gather + LLM + console/Slack
├── requirements.txt
├── .env.example
├── sample-alert.json      ← curl this at /webhook
├── prompts/
│   ├── incident-analysis.txt
│   └── log-analysis.txt
├── scripts/
│   └── ai_review.py       ← AI PR review for GitHub Actions
└── .github/workflows/
    └── ai-review.yml
```

---

## Path A — 10 minutes to first diagnosis

```bash
cd Phase03_AI_Augmented_DevOps/projects/incident-response-bot

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Option 1: no API spend — leave keys empty, set LLM_PROVIDER=mock-llm
# Option 2: set ANTHROPIC_API_KEY=sk-ant-...  (or OPENAI_API_KEY)

# defaults: MOCK_MODE=true
python bot.py
```

In another terminal:

```bash
curl -s -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d @sample-alert.json | jq .
```

You should see a printed incident report in the bot terminal (summary, likely cause, top checks).

Health check: `curl -s http://localhost:8000/health | jq .`

---

## Path B — real Prometheus / Loki

1. Start the Phase 02 observability stack (`docker compose up` there).
2. In `.env`:
   ```bash
   MOCK_MODE=false
   PROMETHEUS_URL=http://localhost:9090
   LOKI_URL=http://localhost:3100
   ```
3. Restart the bot and fire a real or sample alert whose `job` label matches a scraped service (`payments-service`, etc.).

If Loki/Prometheus are down, the bot **must still respond** (it returns "unavailable" strings — never crash).

---

## Path C — Slack

1. Create a Slack app → Bot Token Scopes: `chat:write`, `commands`
2. Invite the bot to `#incidents`
3. Set `SLACK_BOT_TOKEN` and `SLACK_INCIDENT_CHANNEL` in `.env`
4. Re-run the webhook — message should appear in Slack
5. Implement slash commands in `handle_slash_command` (`/status`, `/logs`, `/deploys`, `/rollback` with confirmation)

Public URL tip: use [ngrok](https://ngrok.com/) while learning so Slack can reach your laptop.

---

## AI PR review (Part 2)

1. Add `ANTHROPIC_API_KEY` to your GitHub repo secrets
2. Copy `.github/workflows/ai-review.yml` and `scripts/ai_review.py` into the repo you want reviewed (adjust paths if the repo root *is* this project)
3. Open a PR that touches `.tf` / `.yaml` / `.py` — the Action posts a review comment

---

## Your remaining tasks

Working Path A is provided. Level up:

- [ ] Path B: confirm real PromQL / LogQL results show up in the diagnosis
- [ ] Improve `prompts/incident-analysis.txt` after a few real (or mock) runs — prompts are code
- [ ] Path C: Slack post + `/status` returning live metrics
- [ ] `/rollback` two-step confirmation (never auto-execute)
- [ ] AI PR review on a throwaway PR
- [ ] Document in your fork README how someone else runs Path A

---

## Definition of done

- [ ] Webhook produces a diagnosis within ~30 seconds (console counts)
- [ ] Diagnosis has summary + at least one specific check
- [ ] Bot survives Loki/Prometheus failure
- [ ] Prompts versioned under `prompts/`
- [ ] AI PR review posts a comment *or* you document a dry-run of `ai_review.py` with a sample diff
- [ ] `.env.example` lists every variable you used

---

## Sharing

Open `[Phase 03] Done` on [devops-to-ai](https://github.com/sandeepk24/devops-to-ai) with a screenshot of the console/Slack diagnosis and the prompt you like best.

→ [Phase 04 — MLOps & LLMOps](../../../Phase04_MLOps_LLMOps/README.md)
