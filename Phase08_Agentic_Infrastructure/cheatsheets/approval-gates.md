# Approval gates cheatsheet

**Use this when:** the agent wants to change production (rollback, restart, scale).  
**Rule of thumb:** investigate freely (within read allowlist); mutate only with an approval id.

---

## Happy path

```
investigate alert
  → tools (read-only)
  → propose_rollback  → status=pending
  → human POST /approve
  → execute_rollback(approval_id)
  → verify
  → audit
```

Deny path: mark pending action `denied` — execute must refuse.

---

## What the approval record should store

- Who/what requested it (agent run id)
- Exact action + args (immutable snapshot)
- Environment (dev/stage/prod)
- Expiry (stale approvals die)
- Approver identity (even if “local-dev” in the lab)

---

## Anti-patterns

- “Auto-approve if confidence > 0.9” on day one  
- Reusing one approval for a different service  
- Executing from the model's prose (“User approved”) instead of your API  
- Skipping verify after mutate  

---

## Phase 07 → Phase 08

| Phase 07 | Phase 08 |
|---|---|
| Fixed policy chooses restart | Agent chooses tools, then proposes |
| Suggest / auto modes | Read auto / write gated |
| Kill switch on healer | Kill switch still belongs on the agent |

---

## Lab pointer

`POST /v1/approvals/{id}/approve` and `deny` in the gated-ops-agent project
