# Phase 01 — Core DevOps

> **"A pipeline that works once is a script. A pipeline that works every time is engineering."**
>
> Phase 00 made you comfortable on a server. Phase 01 is where you start shipping like a DevOps engineer — containers, Kubernetes, Terraform, and a CI/CD pipeline that actually deploys something.

---

## Who this is for

| You are... | Do this |
|---|---|
| Finished Phase 00 (or solid on Linux / Bash / Git / Python) | Work through every topic, then the capstone |
| Junior DevOps — used Docker a bit, fuzzy on K8s / Terraform | Skim what you know, go deep on the gaps, build the capstone |
| Already shipping Docker + K8s + Terraform from CI in a real job | Take the [self-check](#self-check--can-you-skip) — if you pass, jump to Phase 02 |

**Time:** 6–8 weeks part-time  
**Goal:** Take an app from your laptop → Docker → Kubernetes → automated deploy, with infra described as code.

---

## Start here — four steps

```
1. Self-check     →  Already doing this at work? Skip to Phase 02
2. Learn          →  Work the topics in order (Docker → Compose → K8s → Helm → Terraform → CI)
3. Practice       →  Run everything locally first (Docker Desktop + kind/k3d)
4. Capstone       →  Build the microservice pipeline (required before Phase 02)
```

You do **not** need a paid cloud account on day one. Start local. Add cloud later if you want the stretch path.

**Cheatsheets in this repo (bookmark these):**

| Topic | Cheatsheet |
|---|---|
| Docker & Compose | [cheatsheets/docker.md](./cheatsheets/docker.md) |
| Kubernetes & kubectl | [cheatsheets/kubernetes.md](./cheatsheets/kubernetes.md) |
| Terraform | [cheatsheets/terraform.md](./cheatsheets/terraform.md) |
| GitHub Actions | [cheatsheets/github-actions.md](./cheatsheets/github-actions.md) |

**Tools to install before you start:**

```bash
# Check what you already have
docker --version
kubectl version --client
helm version
terraform version
```

Missing something? Install as you hit that topic — don't block yourself installing everything up front.

| Tool | Why you need it | Install |
|---|---|---|
| Docker Desktop (or Docker Engine) | Build and run containers | [docs.docker.com](https://docs.docker.com/get-docker/) |
| kind or k3d | Local Kubernetes cluster | [kind](https://kind.sigs.k8s.io/) / [k3d](https://k3d.io/) |
| kubectl | Talk to the cluster | [kubernetes.io](https://kubernetes.io/docs/tasks/tools/) |
| Helm | Package K8s apps | [helm.sh](https://helm.sh/docs/intro/install/) |
| Terraform | Infrastructure as code | [developer.hashicorp.com](https://developer.hashicorp.com/terraform/install) |

---

## Self-check — can you skip?

If you can do **all** of these without looking things up, skip to [Phase 02](../Phase02_Cloud_Native_Operations/README.md):

- Write a multi-stage Dockerfile and explain why the final image is small
- Deploy an app to Kubernetes with a Deployment + Service, then debug a `CrashLoopBackOff`
- Write Terraform that creates a resource and stores state remotely
- Sketch a GitHub Actions pipeline: lint → test → build → deploy
- Explain what happens when you run `kubectl apply -f deployment.yaml`

Otherwise stay here. Fill the gaps — that's the whole point.

---

## Learning objectives

By the end of Phase 01, you should answer **yes** to all of these:

- [ ] Write a multi-stage Dockerfile that produces a small production image
- [ ] Explain pod, Deployment, Service, and Ingress in plain language
- [ ] Write a GitHub Actions workflow that lints, tests, builds, and deploys
- [ ] Write Terraform that provisions infra and manages state correctly
- [ ] Debug a failing container with only `docker logs` / `docker exec` / `kubectl`
- [ ] Explain what happens when a Kubernetes node dies
- [ ] Write a basic Helm chart from scratch

---

## Topics

Work these in order. Each one builds on the last. Don't jump to Kubernetes before Docker feels natural — you'll just be confused in two places at once.

### 1. Docker — containers that actually make sense

Most people learn Docker by pasting `docker run` commands. That works until something breaks at 2am and you have no idea why.

A container is just a process with isolation (namespaces + cgroups). An **image** is a frozen snapshot. A **container** is that snapshot running, with a writable layer on top that disappears when the container dies. Once that clicks, the rest is details.

**Learn:**
- Image layers — why order in a Dockerfile matters (caching)
- Multi-stage builds — build tools stay in one stage, final image stays small
- Base images — `alpine` vs `debian-slim` vs `distroless` (smaller ≠ always better)
- Volumes vs bind mounts
- `.dockerignore` — keep build context small
- Security basics — run as non-root, don't bake secrets into images
- Debug toolkit: `docker logs`, `docker exec`, `docker inspect`, `docker stats`

**Try this before moving on:**
1. Write a Dockerfile for a tiny Python or Node app
2. Make it multi-stage
3. Run it, break it on purpose, fix it with logs + exec
4. Push the image to GHCR or Docker Hub

→ [Docker cheatsheet](./cheatsheets/docker.md)

---

### 2. Docker Compose — more than one container

Before Kubernetes, get comfortable running an app + database together on your laptop. Compose is how most teams do local dev and a lot of CI integration tests.

**Learn:**
- `services`, `networks`, `volumes` in `compose.yaml`
- `.env` files for config
- Health checks and `depends_on` with conditions
- How service names become DNS names (`db`, `api`, etc.)
- One-off commands: `docker compose run`

**Try this:** Spin up your app + Postgres (or Redis) with Compose. Kill the DB container and watch what your app does. That's good instinct for production later.

→ Same [Docker cheatsheet](./cheatsheets/docker.md) — Compose section at the bottom

---

### 3. Kubernetes — enough to be useful, not enough to drown

Kubernetes has a reputation. Ignore the hype. Your goal here is **operational competence**: deploy an app, find out why it's broken, roll back when a deploy goes wrong.

Think of it like this:

```
You say: "I want 3 copies of my app running, always."
K8s says: "Okay. If one dies, I'll start another."
```

That's the reconciliation loop. Desired state vs actual state. Everything else is machinery around that idea.

**Core objects to know:**
- **Pod** — one or more containers that run together (usually one)
- **Deployment** — keeps N pods running, handles rollouts
- **Service** — stable network name / load balancer in front of pods
- **Ingress** — how traffic from outside reaches your Services
- **ConfigMap / Secret** — config and sensitive values (don't bake them into images)
- **Namespace** — a folder for related stuff

**Daily commands:**
```bash
kubectl get pods
kubectl describe pod <name>    # start here when something's broken
kubectl logs <name>
kubectl exec -it <name> -- sh
kubectl rollout undo deployment/<name>
```

**Skip for now:** CNI deep-dives, writing operators, cluster admin. Phase 02 goes deeper on ops.

**Practice cluster:** [kind](https://kind.sigs.k8s.io/) or [k3d](https://k3d.io/) on your laptop. Free, fast, no cloud bill.

→ [Kubernetes cheatsheet](./cheatsheets/kubernetes.md)

---

### 4. Helm — stop copy-pasting YAML

Raw Kubernetes YAML multiplies. Change the image tag in five files? No thanks. Helm packages an app as a **chart** with a `values.yaml` you can override per environment.

**Learn:**
- Install / upgrade / rollback a chart
- Chart layout: `Chart.yaml`, `templates/`, `values.yaml`
- `{{ .Values.something }}` and basic conditionals
- `helm template` and `helm lint` before you apply anything
- `values-dev.yaml` vs `values-prod.yaml`

**Try this:** Take the Deployment + Service you wrote by hand and turn them into a tiny Helm chart. Override replica count with a values file.

---

### 5. Terraform — stop clicking in the console

If you create infra by clicking, nobody can review it, recreate it, or remember why it exists. Terraform lets you describe infrastructure in files, plan the change, then apply it.

**The workflow you'll use forever:**

```
terraform init    →  download providers
terraform plan    →  show what would change (always read this)
terraform apply   →  make it real
terraform destroy →  tear it down when you're done learning
```

**Learn:**
- Resources, variables, outputs, modules
- State — Terraform's memory of what it created (never commit it to Git)
- Remote state (S3, GCS, Terraform Cloud) — required for anything real
- `terraform fmt` and `terraform validate`

**Rule:** If Terraform manages it, don't edit it in the cloud console. Drift will bite you.

**Junior-friendly path:** Start with a local `kind` cluster + Terraform only for things you need (or even skip cloud cluster at first — use kind manually, Terraform the registry / bucket later). Cloud GKE/EKS is optional stretch, not a blocker.

→ [Terraform cheatsheet](./cheatsheets/terraform.md)

---

### 6. CI/CD — GitHub Actions

This is the glue. You push code; the pipeline tests it, builds an image, and deploys it. No "it works on my machine" as the release process.

**A pipeline juniors can actually finish:**

```
push / PR
   → lint
   → test
   → build image + push to registry
   → deploy to Kubernetes (only on main)
```

**Learn:**
- Workflows, jobs, steps, `needs`
- Triggers: `push`, `pull_request`, `workflow_dispatch`
- Secrets (never put tokens in the repo)
- Caching and basic matrix builds
- Branch protection: CI must pass before merge

**Habit:** Add CI on day one of a repo, even if it's just lint + test. Empty promises of "we'll add CI later" age badly.

→ [GitHub Actions cheatsheet](./cheatsheets/github-actions.md)

---

## Capstone project

### Ship a microservice with a real pipeline

This ties the whole phase together. When you're done, you'll have something you can demo in an interview — not a tutorial screenshot.

**Starter code:** [projects/microservice-pipeline/](./projects/microservice-pipeline/)

**What you're building:**

A small REST API (Python FastAPI starter is included — Go is fine too if you prefer) with:

1. **App** — at least 3 endpoints, unit tests, multi-stage Dockerfile (< 100MB final image, non-root user)
2. **Local stack** — `docker compose` with the app + a database
3. **Kubernetes** — Helm chart with probes, resource limits, `values-dev.yaml` / `values-prod.yaml`
4. **CI** — GitHub Actions: lint → test → build/push → deploy on `main`
5. **Infra (pick a path)**  
   - **Path A (recommended for juniors):** local `kind`/`k3d` cluster + GHCR  
   - **Path B (stretch):** Terraform for a cloud cluster (GKE Autopilot / EKS) + remote state

**Rules (these are the point):**
- Pipeline green in under ~5 minutes if you can
- No secrets in Git — GitHub Secrets only
- Image runs as non-root
- Terraform state (if you use it) is remote, never local-only for "real" infra

**Definition of done:**
- [ ] `docker compose up` runs the app locally
- [ ] Image builds multi-stage and runs as non-root
- [ ] Helm chart deploys to kind/k3d (or cloud)
- [ ] CI runs lint + test + build on PRs
- [ ] Merge to `main` deploys (or documents the deploy job clearly)
- [ ] README in your project explains how someone else can run it

**Stretch:** Trivy image scan in CI, Infracost on Terraform PRs, staging auto-deploy + prod needs approval.

Full walkthrough → [projects/microservice-pipeline/README.md](./projects/microservice-pipeline/README.md)

---

## How to know you're ready for Phase 02

Don't move on until you can do these **without googling**:

1. Write a multi-stage Dockerfile from memory
2. Explain step-by-step what `kubectl apply -f deployment.yaml` does
3. Debug a `CrashLoopBackOff` — find the cause, fix it
4. Write a small Terraform resource and explain why you read `plan` before `apply`
5. Add a GitHub Actions job that only runs on `main`
6. Override Helm replicas and a resource limit with a values file

Stuck? Stay in Phase 01. Phase 02 assumes this is boringly solid.

---

## Resources

| Resource | What it's for |
|---|---|
| [Docker best practices](https://docs.docker.com/build/building/best-practices/) | Dockerfile habits that matter |
| [Ivan Velichko — containers](https://iximiuz.com/en/posts/container-learning-path/) | What a container really is |
| [Kubernetes basics tutorial](https://kubernetes.io/docs/tutorials/kubernetes-basics/) | Hands-on K8s intro |
| [kind](https://kind.sigs.k8s.io/) / [k3d](https://k3d.io/) | Local clusters |
| [Helm chart template guide](https://helm.sh/docs/chart_template_guide/) | Writing charts |
| [HashiCorp Terraform tutorials](https://developer.hashicorp.com/terraform/tutorials) | Official Terraform path |
| [GitHub Actions docs](https://docs.github.com/en/actions) | Workflows reference |
| [act](https://github.com/nektos/act) | Run Actions locally |
| Repo cheatsheets | Day-to-day command lookup |

---

## Track your progress

Open a GitHub issue:

```
[Phase 01] Starting — your-handle
[Phase 01] Done — your-handle
```

When you mark Done, link your capstone repo. Looking at someone else's finished pipeline is half the learning.

---

*← [Phase 00 — The Foundation](../Phase00_Foundation/README.md) | [Phase 02 — Cloud Native Operations →](../Phase02_Cloud_Native_Operations/README.md)*
