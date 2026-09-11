# Capstone: Gated ops agent

> **Phase 08 project** — finish this before [Phase 09](../../../Phase09_The_Autonomous_Engineer/README.md).  
> Phase guide: [Phase 08 README](../../README.md)

You're building a small ops agent that **investigates** with read-only tools, **proposes** a rollback, and only **executes** after you approve. Path A uses a mock planner — no API key — so you learn the gates before you add a real model.

---

## Paths

| Path | Needs | What you prove |
|---|---|---|
| **A — Mock planner (start here)** | Docker | Investigate → pending approval → approve → verify + evals |
| **B — Real LLM** | API key + stretch wiring | Same gates; planner can be model-backed later |

**Do Path A completely.** Don't skip the “execute without approval must fail” check.

---

## What's in this folder

```
gated-ops-agent/
├── docker-compose.yml
├── .env.example
├── services/ops-agent/     ← API + tools + mock planner
├── data/
│   ├── metrics.json
│   ├── logs.jsonl
│   └── runbooks/
├── fixtures/
│   ├── incidents/
│   └── eval/
├── prompts/
├── scripts/
│   ├── smoke_test.sh
│   ├── investigate.sh
│   ├── approve.sh
│   └── run_evals.py
└── docs/path-b-llm.md
```

---

## Path A — first win (~20 minutes)

```bash
cd Phase08_Agentic_Infrastructure/projects/gated-ops-agent

cp .env.example .env
docker compose up --build -d

./scripts/smoke_test.sh
```

Manual flow:

```bash
# Investigate — should propose rollback, NOT execute it
./scripts/investigate.sh high-error-rate
# note approval_id from the JSON

# This must FAIL or refuse
curl -s -X POST http://localhost:8100/v1/actions/execute_rollback \
  -H "Content-Type: application/json" \
  -d '{"service":"payments-api"}' | jq .

# Approve, then execute happens inside approve (or follow response)
./scripts/approve.sh <approval_id>

curl -s http://localhost:8100/v1/audit | jq '.[-5:]'
python3 scripts/run_evals.py
```

**Port:** agent http://localhost:8100

---

## Stuck? Quick fixes

| Symptom | Try this |
|---|---|
| Docker daemon errors | Start Docker Desktop; `docker info` |
| Investigate returns empty tools | `docker compose logs ops-agent` |
| Approve 404 | Use the `approval_id` from the investigate response |
| Evals fail after tinkering | `docker compose down` && up; don't weaken allowlists to “fix” tests |

---

## What already works (Path A)

- [x] Allowlisted tools (metrics, logs, runbook, propose/execute rollback)  
- [x] Mock planner for a high-error-rate incident  
- [x] Approval gate for mutations  
- [x] Audit log  
- [x] Eval suite + smoke test  

---

## Your tasks (level up)

- [ ] Read `tools.py` — find where disallowed tools die  
- [ ] Read `planner.py` — see the deterministic tool order  
- [ ] Inject the hostile log incident and confirm still no ungated rollback  
- [ ] Deny an approval and confirm execute stays blocked  
- [ ] Stretch: Path B notes in `docs/path-b-llm.md`  

---

## Definition of done

- [ ] `./scripts/smoke_test.sh` passes  
- [ ] `python3 scripts/run_evals.py` passes  
- [ ] You can explain read vs write tools + approval in one minute  
- [ ] Notes say mock vs any LLM attempt  

---

## Sharing

Open `[Phase 08] Done` with an audit snippet (tools + approval) and eval output.

→ [Phase 09 — Autonomous Engineer](../../../Phase09_The_Autonomous_Engineer/README.md)
