# Tool calling & allowlists

**Use this when:** an LLM (or mock planner) is about to call functions on behalf of ops.  
**Rule of thumb:** if the tool isn't on the allowlist, it doesn't exist — even if the model begs.

---

## Mental model

```
Planner picks:  name=get_recent_logs  args={service: "payments-api"}
     ↓
Your runtime:  is name allowed? → run function → return JSON to planner
```

The model proposes. **Your code disposes.**

---

## Read vs write tools

| Kind | Examples | Default |
|---|---|---|
| Read | metrics, logs, runbook search, list pods | Auto OK after allowlist |
| Write | restart, rollback, scale, delete | Approval required |

Never hide a write behind a friendly name like `heal_service` without an approval check inside.

---

## Allowlist sketch

```text
ALLOWED_TOOLS=get_service_metrics,get_recent_logs,search_runbook,propose_rollback
# execute_rollback is separate and requires approval_id
```

Adding a tool = PR + threat review, not a prompt tweak.

---

## Schema tips

- Tight argument types (`service` enum / pattern, not free text paths)
- Cap log line counts and time ranges
- Return structured JSON; don't return raw shell output as “success”

---

## Lab pointer

Phase 08: `services/ops-agent/tools.py` + `ALLOWED_TOOLS` in `.env.example`
