# Guardrails cheatsheet

**Use this when:** you're about to flip a healer from suggest → auto.  
**Rule of thumb:** if you can't kill it in one env var or one button, don't enable it.

---

## Minimum seatbelts

| Guardrail | What it does |
|---|---|
| **Action allowlist** | Only `restart_service` (etc.) — no free-form shell |
| **Kill switch** | `KILL_SWITCH=true` → decide may run, act never does |
| **Cooldown** | Don't restart the same target every 10 seconds |
| **Max retries** | After N failures, suggest/page — stop looping |
| **Scope** | Dev first; prod later with tighter limits |
| **Blast radius** | One service / one namespace — never "all Deployments" |

---

## Allowlist example

```text
ALLOWED_ACTIONS=restart_service
# not: delete_namespace, kubectl_anything, run_shell
```

If a new action is needed, it's a PR to the allowlist — not a clever prompt.

---

## Kill switch drill

1. Put service in CrashLoop (or inject alert)  
2. Enable auto — confirm recovery  
3. Flip kill switch — inject again — confirm **no** act in audit  
4. Document where the switch lives (Compose env, Feature flag, ConfigMap)

Practice this like a fire drill. 3am-you will thank noon-you.

---

## What never goes on the allowlist on day one

- Delete PVC / mass pod delete  
- Change IAM / firewall  
- "Run this LLM-generated kubectl"  
- Anything irreversible without a clear rollback  

---

## Lab pointer

Phase 07: `HEALER_MODE`, `ALLOWED_ACTIONS`, `KILL_SWITCH`, `COOLDOWN_SECONDS` in `.env.example`
