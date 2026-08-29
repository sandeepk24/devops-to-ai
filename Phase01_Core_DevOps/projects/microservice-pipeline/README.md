# Capstone: Microservice pipeline

> **Phase 01 project** — finish this before [Phase 02](../../../Phase02_Cloud_Native_Operations/README.md).  
> Full phase guide: [Phase 01 README](../../README.md)

You're going to take a small API from "runs on my laptop" to "builds and deploys from GitHub Actions." That's the core DevOps loop. Everything else in your career is a variation of this.

---

## Two paths (pick one)

| Path | Cluster | Best if you... |
|---|---|---|
| **A — Local (recommended first)** | kind or k3d on your machine + GHCR | Want to finish without cloud bills or IAM rabbit holes |
| **B — Cloud (stretch)** | GKE Autopilot or EKS via Terraform + remote state | Already comfortable with Path A and want CV cloud signal |

Do Path A completely. Add Path B if you have time.

---

## What you're building

```
microservice-pipeline/
├── app/                    ← FastAPI starter (your code lives here)
├── tests/                  ← unit tests
├── Dockerfile              ← multi-stage, non-root
├── compose.yaml            ← local app + Postgres
├── helm/api/               ← chart to deploy the app
├── terraform/              ← optional Path B starter
├── .github/workflows/ci.yml
└── README.md               ← this file (extend it with how to run YOUR fork)
```

---

## Before you start

You need **Python 3.11 or 3.12** for local pytest (3.13 usually fine; very new versions can break pydantic wheels). CI uses 3.12.

```bash
docker --version
kubectl version --client
helm version
python3 --version

# Local cluster (Path A)
kind create cluster --name phase01
# or: k3d cluster create phase01

kubectl get nodes   # should show Ready
```

---

## Setup

```bash
cd Phase01_Core_DevOps/projects/microservice-pipeline

# Local app + DB
docker compose up --build

# In another terminal
curl -s http://localhost:8080/health
curl -s http://localhost:8080/v1/items
```

App deps:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

---

## Your tasks (in order)

Work top to bottom. Each step unlocks the next.

### 1. Application
- [ ] Read `app/main.py` — understand the three endpoints
- [ ] Add or improve unit tests until coverage feels honest (aim ≥ 70%)
- [ ] Keep `/health` and `/ready` — Kubernetes will need them

### 2. Docker
- [ ] Read the multi-stage `Dockerfile` — know why builder vs final stage exists
- [ ] Confirm the image runs as non-root (`docker run` + `whoami` / inspect)
- [ ] `docker build -t api:dev .` and run it without Compose once
- [ ] Tweak `.dockerignore` if your build context is bloated
- [ ] Stretch: shrink further or add an image HEALTHCHECK

### 3. Compose
- [ ] `docker compose up --build` brings up api + db
- [ ] App reads `DATABASE_URL` (or works without DB for health — your call, document it)

### 4. Helm
- [ ] Fill in chart templates under `helm/api/`
- [ ] Probes, resources, image repository/tag via values
- [ ] `values-dev.yaml` and `values-prod.yaml` differ (replicas, resources)
- [ ] Deploy to kind/k3d:
  ```bash
  helm upgrade --install api ./helm/api -n demo --create-namespace -f helm/api/values-dev.yaml
  kubectl port-forward -n demo svc/api 8080:80
  ```

### 5. CI (GitHub Actions)
- [ ] Complete `.github/workflows/ci.yml` TODOs (GHCR login + push, real deploy)
- [ ] `lint` → `test` → `build` (push image to GHCR)
- [ ] `deploy` only on `main` (Path A: document a manual helm step if the runner can't reach your laptop cluster — that's fine; Path B can do real deploy)
- [ ] **If this folder becomes its own repo:** move `.github/workflows/ci.yml` to the repo root and remove the `working-directory` / nested paths

### 6. Terraform (Path B only)
- [ ] Remote state backend
- [ ] Cluster module or resources
- [ ] Never commit state files

---

## Definition of done

- [ ] Someone else can clone your repo and follow your README to run Compose
- [ ] Multi-stage image builds; container user is not root
- [ ] Helm deploy works on kind/k3d (screenshot or notes of `kubectl get pods` is enough)
- [ ] CI runs on PRs for lint + test (+ build if you've set GHCR permissions)
- [ ] No secrets in Git

**Stretch:** Trivy scan job, Infracost on Terraform PRs, staging vs prod environments with approval.

---

## Sharing your work

Open `[Phase 01] Done` on the [devops-to-ai](https://github.com/sandeepk24/devops-to-ai) repo and link your GitHub project.

Then → [Phase 02 — Cloud Native Operations](../../../Phase02_Cloud_Native_Operations/README.md)
