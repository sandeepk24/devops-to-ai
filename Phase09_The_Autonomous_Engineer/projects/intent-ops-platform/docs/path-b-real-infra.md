# Path B — wiring this to real infrastructure

Path A proves the contract: intent → policy → bounded plan → approval →
execute/verify → episode. Path B swaps out the pieces underneath that
contract without changing the contract itself. Do this only after Path A's
smoke test and evals are green — you want to know the loop is correct
before you also debug real infra underneath it.

## What changes, and what doesn't

| Stays the same | Gets swapped |
|---|---|
| Intent schema, `IntentIn` | `world.py` — replace the in-memory dict with real calls |
| `policy.py` allowlists and caps | The values in those allowlists (add real environments/actions deliberately) |
| Episode shape, audit log | Nothing — this is your operational memory either way |
| Bounded retry/verify loop | The verify step — real metrics instead of a mock error rate |

## Suggested real backends, smallest first

1. **Real metrics for verification** — point the verify step at a real Prometheus query (reuse Phase 02 instincts) instead of reading `world.error_rate`. Keep the mock executor for now. This is the lowest-risk first step: you're only changing what "met the target" means, not what can act.
2. **Real rollback via GitOps** — swap `world.rollback()` for a call that reverts a Git ref and lets ArgoCD/Flux sync it (Phase 02 territory again). The action is still allowlisted, still policy-checked, still only reachable from inside an approved episode.
3. **Real scaling via the Kubernetes API or an HPA nudge** — swap `world.scale_replicas()` for a real `kubectl scale` or a patch to an HPA's min/max. Keep `MAX_REPLICAS` as a hard cap in your policy layer even though Kubernetes has its own — defense in depth, same principle as Phase 05/08.
4. **A real planner** — replace `planner.plan_step()` with an LLM call that reads real metrics/logs/runbooks (bring back Phase 08's tool-calling patterns here) and proposes an action. The policy layer doesn't care where the proposal came from — it checks the same way either way. This is deliberately last: get the boring, deterministic version fully trustworthy before you hand the "what should we try" question to a model.

## Non-negotiables when you go real

- Never expand `ALLOWED_ENVIRONMENTS` to include `prod` casually — that decision should involve more than one person and probably a separate, stricter policy file.
- Keep the "no raw execute endpoint" property. If Path B needs a way to trigger actions outside the approve handler for testing, gate it behind a very obviously-named debug flag that's off by default and never set in anything resembling production.
- Real infra means real cost to being wrong — consider dropping `MAX_ATTEMPTS_CAP` to 1 until you trust the new executor, then raise it back once you've watched it succeed a few times.
- Add real identity to `approver` — "local-dev" was fine for a lab; a real system should record who actually clicked approve.
