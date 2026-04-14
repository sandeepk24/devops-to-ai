# Project: AI-powered incident response bot

> Phase 03 capstone project — build this before moving to Phase 04.

A Slack bot that automatically gathers incident context from your observability stack, sends it to Claude for analysis, and posts a structured diagnosis to your incidents channel — all within 30 seconds of an alert firing.

---

## What's in this project

```
incident-response-bot/
├── bot.py                     ← main bot (webhook receiver + slash commands)
├── requirements.txt
├── .env.example               ← copy to .env and fill in your values
├── prompts/
│   ├── incident-analysis.txt  ← the core diagnosis prompt (version controlled)
│   └── log-analysis.txt       ← used by /logs slash command
├── scripts/
│   └── ai_review.py           ← AI PR review script (called from GitHub Actions)
└── .github/
    └── workflows/
        └── ai-review.yml      ← the PR review pipeline
```

---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys and URLs

# 3. Run the bot
python bot.py

# 4. Test the webhook locally
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "version": "4",
    "status": "firing",
    "alerts": [{
      "status": "firing",
      "labels": {
        "alertname": "HighErrorRate",
        "severity": "critical",
        "job": "payments-service"
      },
      "startsAt": "2024-01-15T02:34:00Z"
    }]
  }'
```

---

## Connecting to Alertmanager

Add this to your `alertmanager.yml`:

```yaml
receivers:
  - name: incident-bot
    webhook_configs:
      - url: http://incident-bot:8000/webhook
        send_resolved: false

route:
  receiver: incident-bot
  group_by: [alertname, job]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
```

---

## Setting up Slack

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → Create New App → From Scratch
2. Under **OAuth & Permissions**, add these Bot Token Scopes:
   - `chat:write`
   - `commands`
3. Under **Slash Commands**, create:
   - `/status` → `https://your-bot-url/slack/commands`
   - `/logs` → `https://your-bot-url/slack/commands`
   - `/deploys` → `https://your-bot-url/slack/commands`
   - `/rollback` → `https://your-bot-url/slack/commands`
4. Install the app to your workspace
5. Copy the Bot User OAuth Token to `SLACK_BOT_TOKEN` in `.env`

---

## Setting up the AI PR review

1. Add your `ANTHROPIC_API_KEY` to your GitHub repo secrets
2. Copy `.github/workflows/ai-review.yml` to your infrastructure repo
3. Open any PR that touches `.tf`, `.yaml`, or `.py` files — the review will post automatically

---

## Your tasks

The bot skeleton is provided. Implement the `TODO` sections in `bot.py`:

- [ ] `get_loki_logs()` — query Loki for recent error logs
- [ ] `get_prometheus_metrics()` — fetch golden signal metrics
- [ ] `get_recent_deployments()` — get ArgoCD or git deploy history
- [ ] `get_pod_events()` — fetch Kubernetes events
- [ ] `analyse_incident()` — call Claude API and parse response
- [ ] `format_slack_message()` — build Slack Block Kit message
- [ ] `/status` slash command
- [ ] `/logs` slash command
- [ ] `/deploys` slash command
- [ ] `/rollback` slash command (with confirmation step)

---

## Definition of done

- [ ] Webhook receives alert and posts to Slack within 30 seconds
- [ ] Slack message includes AI summary, likely cause, and top 3 checks
- [ ] `/status payments-service` returns real metric data
- [ ] AI PR review posts a comment on a test PR
- [ ] Bot handles Loki/Prometheus being unavailable without crashing
- [ ] All prompts in `prompts/` as version-controlled `.txt` files
- [ ] `.env.example` documents every required variable

---

## Sharing your work

When done, open a `[Phase 03] Done` issue on the devops-to-ai repo. Include a screenshot of your bot responding to a real (or simulated) alert in Slack.
