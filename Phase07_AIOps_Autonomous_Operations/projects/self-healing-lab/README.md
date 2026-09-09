# Capstone: Self-healing lab

> **Phase 07 project** — finish this before [Phase 08](../../../Phase08_Agentic_Infrastructure/README.md).  
> Phase guide: [Phase 07 README](../../README.md)

You're closing the loop on a tiny mock platform: an alert comes in, a healer **suggests** or **auto**-runs a safe restart, then verifies and writes an audit line. Same instincts you'll want before any LLM agent gets a kubectl allowlist.

---

## Paths

| Path | Needs | What you prove |
|---|---|---|
| **A — Mock (start here)** | Docker running | Suggest → auto → kill switch → audit |
| **B — Cluster** | kind/k3d + kubectl | Optional: flappy Deployment + scripted restart notes |

**Do Path A completely.** Don't skip suggest mode.

---

## What's in this folder

```
self-healing-lab/
├── docker-compose.yml
├── .env.example
├── services/
│   ├── control-plane/   ← mock services + actions + audit API
│   └── healer/          ← detect/decide/act/verify loop
├── fixtures/alerts/     ← sample alert JSON
├── scripts/
│   ├── smoke_test.sh
│   ├── inject_alert.sh
│   └── set_mode.sh
└── docs/
    ├── audit-trail.md
    └── path-b-kind.md
```

---

## Path A — first win (~20 minutes)

```bash
cd Phase07_AIOps_Autonomous_Operations/projects/self-healing-lab

cp .env.example .env
docker compose up --build -d

# Full Path A drill (suggest → auto → kill switch)
./scripts/smoke_test.sh
```

Manual walkthrough:

```bash
# 1) Suggest mode (default) — should NOT restart, only audit a suggestion
./scripts/set_mode.sh suggest
./scripts/inject_alert.sh crashloop
curl -s http://localhost:8090/v1/audit | jq .

# 2) Auto mode — should restart flappy and verify healthy
./scripts/set_mode.sh auto
./scripts/inject_alert.sh crashloop
curl -s http://localhost:8090/v1/services/flappy | jq .
curl -s http://localhost:8090/v1/audit | jq '.[-3:]'

# 3) Kill switch — auto on, but no acts
./scripts/set_mode.sh auto kill
./scripts/inject_alert.sh crashloop
curl -s http://localhost:8090/v1/audit | jq '.[-1]'
```

**UIs / ports:** control plane http://localhost:8090 · healer http://localhost:8091/health

---

## Stuck? Quick fixes

| Symptom | Try this |
|---|---|
| Docker daemon errors | Start Docker Desktop; `docker info` |
| Inject works but nothing in audit | Wait 2–3s (healer polls); check `docker compose logs healer` |
| Auto doesn't heal | `HEALER_MODE=auto` and `KILL_SWITCH=false` in `.env`; recreate healer |
| Port 8090 busy | Change ports in `docker-compose.yml` |

---

## What already works (Path A)

- [x] Mock control plane with service health + restart action  
- [x] Healer with suggest/auto, allowlist, cooldown, kill switch  
- [x] Alert fixtures (`crashloop`, `high_latency`)  
- [x] Audit log API + smoke test  

---

## Your tasks (level up)

- [ ] Read `services/healer/main.py` — find allowlist + kill switch checks  
- [ ] Inject `high_latency` — confirm it stays suggest-only (no restart)  
- [ ] Lower `COOLDOWN_SECONDS` and watch duplicate CrashLoops get skipped  
- [ ] Skim `docs/audit-trail.md` and paste one real audit line into your notes  
- [ ] Stretch: Path B notes in `docs/path-b-kind.md`  

---

## Definition of done

- [ ] `./scripts/smoke_test.sh` passes  
- [ ] You can explain suggest vs auto without hand-waving  
- [ ] Kill switch test leaves an audit `skipped:kill_switch` (or equivalent)  
- [ ] You know one alert you would *not* auto-remediate  
- [ ] Notes say whether you tried Path B  

---

## Sharing

Open `[Phase 07] Done` with a suggest audit line and an auto audit line.

→ [Phase 08 — Agentic Infrastructure](../../../Phase08_Agentic_Infrastructure/README.md)
