# Capstone: Golden-path service template

> **Phase 06 project** — finish this before [Phase 07](../../../Phase07_AIOps_Autonomous_Operations/README.md).  
> Phase guide: [Phase 06 README](../../README.md)

You're building a **paved road**: a skeleton other engineers can scaffold into a real service, run on a laptop, and (optionally) deploy to kind. That's platform engineering in miniature — not a 40-page wiki and a hope.

---

## Paths

| Path | Needs | What you prove |
|---|---|---|
| **A — Laptop (start here)** | Docker running | `new_service.sh` → Compose → `/health` |
| **B — Cluster** | kind/k3d + kubectl | Deploy the scaffolded service into its own namespace |

**Do Path A completely.** Path B is the stretch that makes the interview story stronger.

---

## What's in this folder

```
golden-path-template/
├── skeleton/                 ← the paved road (copy source)
│   ├── app/
│   ├── Dockerfile
│   ├── compose.yaml
│   ├── requirements.txt
│   ├── k8s/
│   ├── catalog-info.yaml     ← IDP-shaped ownership stub
│   ├── .github/workflows/ci.yml.example
│   └── docs/runbook.md
├── services/                 ← your scaffolded apps land here (gitignored examples ok)
├── scripts/
│   ├── new_service.sh
│   ├── smoke_test.sh
│   └── deploy_kind.sh
├── docs/
│   ├── day1-for-app-teams.md
│   └── platform-metrics.md
└── SCORECARD.md              ← is this path actually good?
```

---

## Path A — first win (~15 minutes)

```bash
# From the devops-to-ai repo root:
cd Phase06_Platform_Engineering/projects/golden-path-template

# Scaffold a service (creates services/demo-api/ ...)
./scripts/new_service.sh demo-api

# Run it
cd services/demo-api
docker compose up --build -d

# Prove it
curl -s http://localhost:8080/health | jq .
curl -s http://localhost:8080/v1/info | jq .
```

Or from the template root:

```bash
./scripts/smoke_test.sh demo-api
```

Stop when done: `docker compose -f services/demo-api/compose.yaml down`

---

## Stuck? Quick fixes

| Symptom | Try this |
|---|---|
| `docker: command not found` / daemon errors | Start Docker Desktop; `docker info` |
| Port 8080 busy | Set `HOST_PORT=8081` in `services/<name>/compose.yaml` or stop the other container |
| `services/foo already exists` | Pick a new name or remove the old folder |
| Scaffold looks unchanged | Re-run `new_service.sh` with a fresh name; don't edit only `skeleton/` expecting live services to update |

---

## What already works (Path A)

- [x] Skeleton FastAPI app with `/health` + `/v1/info`  
- [x] Non-root multi-stage Dockerfile  
- [x] Compose for laptop day-1  
- [x] `new_service.sh` placeholder replacement  
- [x] K8s Deployment/Service stubs + catalog stub  
- [x] Runbook + metrics worksheet + scorecard  

---

## Your tasks (level up)

### Understand & operate
- [ ] Read `scripts/new_service.sh` — know what gets replaced  
- [ ] Scaffold a second service (`checkout-api`) without breaking `demo-api`  
- [ ] Skim `docs/day1-for-app-teams.md` and edit it so it matches *your* steps  
- [ ] Fill `docs/platform-metrics.md` with two metrics you'd track at a fake company  

### Platform product thinking
- [ ] Complete `SCORECARD.md` honestly after Path A  
- [ ] Add one improvement to the skeleton (e.g. `/ready`, or a CI note) and re-scaffold to a third name  

### Stretch
- [ ] Path B: `./scripts/deploy_kind.sh demo-api` and curl via port-forward  
- [ ] Add a ResourceQuota to the namespace  
- [ ] Point a real Backstage (or just keep `catalog-info.yaml` as the contract)  

---

## Path B — kind (optional)

```bash
kind create cluster --name phase06   # if you don't have one

# From golden-path-template/
./scripts/new_service.sh demo-api    # if you don't have it yet
./scripts/deploy_kind.sh demo-api

kubectl -n demo-api port-forward svc/demo-api 8080:8080
curl -s http://localhost:8080/health
```

---

## Definition of done

- [ ] At least one service scaffolded under `services/`  
- [ ] `curl /health` works via Compose  
- [ ] You can explain golden path vs snowflake in plain language  
- [ ] `docs/day1-for-app-teams.md` is something you'd hand a teammate  
- [ ] `SCORECARD.md` filled  
- [ ] Notes say whether you did Path B  

---

## Sharing

Open `[Phase 06] Done` on [devops-to-ai](https://github.com/sandeepk24/devops-to-ai) with a `/health` screenshot and one sentence: who is the customer of your platform?

→ [Phase 07 — AIOps](../../../Phase07_AIOps_Autonomous_Operations/README.md)
