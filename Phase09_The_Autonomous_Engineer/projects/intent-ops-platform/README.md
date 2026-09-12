# Capstone: Intent ops platform

> **Phase 09 project** — the last capstone in the roadmap.
> Phase guide: [Phase 09 README](../../README.md)

You state an outcome ("keep checkout-api's error rate under 5%"), not a
command. The platform plans a bounded response, a human approves the whole
plan once, and the system executes, verifies, retries a bounded number of
times, and either succeeds or hands back to a human — never loops forever.
Path A is a fully mocked world: no cluster, no LLM key, no cost.

---

## Paths

| Path | Needs | What you prove |
|---|---|---|
| **A — Mock world (start here)** | Docker | Intent → policy → awaiting approval → approve → bounded execute/verify loop → succeeded or escalated |
| **B — Real infra** | Cluster/GitOps, optional LLM planner | Same contract, real executor and planner underneath — see `docs/path-b-real-infra.md` |

**Do Path A completely first.** Don't skip the escalation case — watching the system correctly give up is as important as watching it succeed.

---

## What's in this folder

```
intent-ops-platform/
├── docker-compose.yml
├── .env.example
├── services/orchestrator/   ← API + policy + planner + mock world
│   ├── main.py
│   ├── policy.py
│   ├── planner.py
│   └── world.py
├── data/
│   └── services.json        ← three pretend services, two different causes
├── fixtures/
│   ├── intents/              ← one JSON file per scenario below
│   └── eval/cases.jsonl
├── scripts/
│   ├── smoke_test.sh
│   ├── submit_intent.sh
│   ├── approve_episode.sh
│   ├── deny_episode.sh
│   ├── set_kill_switch.sh
│   └── run_evals.py
└── docs/
    ├── episode-trail.md
    └── path-b-real-infra.md
```

---

## Path A — first win (~20 minutes)

```bash
cd Phase09_The_Autonomous_Engineer/projects/intent-ops-platform

cp .env.example .env
docker compose up --build -d

./scripts/smoke_test.sh
```

That one script runs every scenario below end to end. To walk through it by hand instead:

```bash
curl -sf -X POST http://localhost:8200/v1/reset >/dev/null

# 1. A bad deploy — rollback fixes it in one approved attempt
./scripts/submit_intent.sh bad-deploy
# note the "id" from the response
./scripts/approve_episode.sh <episode_id>
# status: succeeded, plan has 1 attempt

curl -sf -X POST http://localhost:8200/v1/reset >/dev/null

# 2. Overload — the first scale-up isn't enough, the second one is
./scripts/submit_intent.sh overload-recoverable
./scripts/approve_episode.sh <episode_id>
# status: succeeded, plan has 2 attempts

curl -sf -X POST http://localhost:8200/v1/reset >/dev/null

# 3. Same overload, a target it genuinely can't reach in 2 attempts
./scripts/submit_intent.sh overload-unreachable
./scripts/approve_episode.sh <episode_id>
# status: escalated_needs_human — it stopped instead of looping forever

# 4. Refused before approval ever exists — no episode gets to awaiting_approval
./scripts/submit_intent.sh blast-radius-cap   # doubling replicas would break the cap
./scripts/submit_intent.sh prod-not-allowed   # prod isn't enabled in this lab
./scripts/submit_intent.sh unknown-goal       # goal was never added to the allowlist

# 5. Hostile notes don't buy an approval they weren't given
./scripts/submit_intent.sh hostile-notes
# status: awaiting_approval — same as any other well-formed intent, notes ignored

# 6. Kill switch pauses an approval, it doesn't drop it
./scripts/set_kill_switch.sh on
./scripts/submit_intent.sh bad-deploy
./scripts/approve_episode.sh <episode_id>   # 403 — but the episode is still awaiting_approval
./scripts/set_kill_switch.sh off
./scripts/approve_episode.sh <episode_id>   # goes through now, same approval

python3 scripts/run_evals.py
```

**Port:** orchestrator http://localhost:8200

---

## Stuck? Quick fixes

| Symptom | Try this |
|---|---|
| Docker daemon errors | Start Docker Desktop; `docker info` |
| `submit_intent.sh` says "Usage" | Check the fixture name against `ls fixtures/intents` |
| Approve returns 400 | The episode isn't `awaiting_approval` anymore — `GET /v1/episodes/{id}` to see its current status |
| Approve returns 403 | Kill switch is on — `./scripts/set_kill_switch.sh off` |
| Evals fail after tinkering | `./scripts/set_kill_switch.sh off` then `docker compose down && docker compose up --build -d`; don't loosen a policy cap just to make a test pass |

---

## What already works (Path A)

- [x] Intent schema with a typed, allowlisted goal/environment/target and a free-text field the planner never reads
- [x] Two-gate policy checks (intent-level, then action-level) before an episode ever reaches `awaiting_approval`
- [x] A bounded execute → verify → replan loop that always ends in `succeeded` or `escalated_needs_human`
- [x] Full episode records plus a flat audit log
- [x] A kill switch that pauses an approval instead of dropping it
- [x] Eval suite covering success-in-one, success-in-two, escalation, and every refusal path
- [x] Smoke test that walks every scenario end to end

---

## Your tasks (level up)

- [ ] Read `world.py` — find the line where `overload_k` makes scaling math deterministic
- [ ] Read `main.py`'s `_run_bounded_loop` — trace exactly where it decides "retry" vs "escalate"
- [ ] Lower `MAX_ATTEMPTS_CAP` to `1` in `.env`, recreate the container, and watch `overload-recoverable` escalate instead of succeed
- [ ] Add a fourth mock service with its own `cause`, and decide honestly whether the planner should know what to do with it (if not, that's `no_safe_action_escalated`, and that's fine)
- [ ] Deny an episode instead of approving it, and confirm the world never changed
- [ ] Stretch: read `docs/path-b-real-infra.md` and swap one mock piece for something real

---

## Definition of done

- [ ] `./scripts/smoke_test.sh` passes
- [ ] `python3 scripts/run_evals.py` passes
- [ ] You can explain, in one minute, the difference between `rejected_by_policy` and `no_safe_action_escalated`
- [ ] You can point at the exact line that stops the retry loop from running forever
- [ ] Notes say mock vs any real-infra attempt

---

## Sharing

Open `[Phase 09] Done` with two episode records: one that succeeded, one that escalated. That contrast is the whole capstone in two JSON blobs.

You've now got a finished capstone for every phase, 00 through 09. That's worth a post, not just an issue.
