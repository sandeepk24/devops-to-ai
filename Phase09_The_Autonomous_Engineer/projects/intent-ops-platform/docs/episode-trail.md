# Reading an episode record

Every intent produces exactly one episode, whether it succeeds, gets denied,
or never even makes it past policy. `GET /v1/episodes/{id}` returns the
whole thing. Here's how to read one.

## Shape

```json
{
  "id": "ep-1737840000000-a1b2c3",
  "intent": {
    "goal": "reduce_error_rate",
    "service": "checkout-api",
    "target_error_rate": 0.05,
    "environment": "dev",
    "max_attempts": null,
    "notes": "no recent deploy, looks like a traffic spike",
    "effective_max_attempts": 2
  },
  "status": "succeeded",
  "plan": [
    {
      "attempt": 1,
      "action": "scale_replicas",
      "args": {"service": "checkout-api", "replicas": 4},
      "rationale": "Error rate tracks load, not a bad deploy — doubling replicas to 4 to spread it out.",
      "execution_result": {"replicas": 4, "error_rate": 0.1, "...": "..."},
      "verification": {"error_rate": 0.1, "target_error_rate": 0.05, "met": false}
    },
    {
      "attempt": 2,
      "action": "scale_replicas",
      "args": {"service": "checkout-api", "replicas": 8},
      "rationale": "Error rate tracks load, not a bad deploy — doubling replicas to 8 to spread it out.",
      "execution_result": {"replicas": 8, "error_rate": 0.05, "...": "..."},
      "verification": {"error_rate": 0.05, "target_error_rate": 0.05, "met": true}
    }
  ],
  "created_at": 1737840000.0,
  "approver": "local-dev",
  "approved_at": 1737840001.2
}
```

## The fields that matter most

- **`intent`** — exactly what was asked, plus `effective_max_attempts` so you can see the policy-clamped budget without cross-referencing anything else.
- **`status`** — the terminal states are `succeeded`, `denied`, `rejected_by_policy`, `no_safe_action_escalated`, and `escalated_needs_human`. Non-terminal: `submitted`, `awaiting_approval`, `executing`.
- **`plan`** — one entry per attempt. Each entry carries its own rationale, execution result, and verification — you never have to guess why a given attempt was made.
- **`rejection_reason`** — present whenever `status` is one of the rejected/escalated-before-approval states. Plain English, not an error code.

## Terminal states, at a glance

| Status | What it means | Where it stops |
|---|---|---|
| `rejected_by_policy` | The intent or its first proposed action broke a rule | Before `awaiting_approval` |
| `no_safe_action_escalated` | The planner had no known-safe move for this cause | Before `awaiting_approval` |
| `denied` | A human said no | After `awaiting_approval` |
| `succeeded` | An attempt met the target | Inside the bounded loop |
| `escalated_needs_human` | The attempt cap ran out before the target was met | Inside the bounded loop |

Two different states both mean "the system didn't act" — `rejected_by_policy` and `no_safe_action_escalated` — and that's on purpose. One means "this broke a rule," the other means "this didn't break any rule, the planner just doesn't know what to do." Worth telling those apart when you're deciding whether to fix a policy or add a new planner case.
