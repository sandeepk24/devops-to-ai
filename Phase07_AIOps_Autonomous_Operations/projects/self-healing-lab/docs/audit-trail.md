# Reading the audit trail

Every interesting thing the lab does should show up on:

```bash
curl -s http://localhost:8090/v1/audit | jq .
```

## Kinds you'll see

| `kind` / `outcome` | Meaning |
|---|---|
| `alert_received` | Control plane accepted an alert |
| `decision` + `suggest` | Healer would act but mode is suggest |
| `decision` + `auto_executing` | Healer is taking an allowlisted action |
| `action_executed` | Restart (or other action) ran |
| `verify` | Post-action health check |
| `skipped_kill_switch` | Act blocked on purpose |
| `skipped_cooldown` / `skipped_rate_limit` | Seatbelts engaged |
| `suggest_only_no_safe_action` | e.g. high_latency — page a human |

## Postmortem habit

Grab two lines for your notes: one **suggest**, one **auto** (with `verified_healthy: true`). That's the story interviewers want — not "we turned on auto-remediation."
