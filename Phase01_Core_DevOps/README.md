# Phase 01 — Core DevOps

> **"A pipeline that works once is a script. A pipeline that works every time is engineering."**
>
> This is where you stop being someone who uses a computer and start being someone who builds infrastructure. By the end of this phase you'll have a real CI/CD pipeline, real containerised workloads, and real infrastructure-as-code running in the cloud. Not tutorials. Not sandboxes. Yours.

---

## What this phase is

Phase 01 is the core toolkit of every working DevOps engineer. These are the tools you'll use every single day regardless of which company you work at, which cloud you're on, or which team you join. Docker, Kubernetes, Terraform, and CI/CD pipelines are not trends — they are the current standard. Learn them properly here and every phase after this accelerates.

**Estimated time:** 6–8 weeks  
**Target audience:** Anyone who has completed Phase 00 or already has solid Linux, Python, and Git skills  
**Skippable if:** You've written multi-stage Docker builds, deployed to Kubernetes from a CI pipeline, and written Terraform modules professionally

---

## Learning objectives

When you finish this phase, you should be able to answer yes to all of these:

- [ ] Can you write a multi-stage Dockerfile that produces a minimal production image?
- [ ] Can you explain what a Kubernetes pod, deployment, service, and ingress actually are — without reading a definition?
- [ ] Can you write a GitHub Actions pipeline that lints, tests, builds, and deploys an application?
- [ ] Can you write Terraform that provisions real cloud infrastructure and manages its state correctly?
- [ ] Can you debug a failing container without a GUI — using only `docker logs`, `docker exec`, and `kubectl`?
- [ ] Can you explain what happens when a Kubernetes node goes down and how the scheduler responds?
- [ ] Can you write a Helm chart from scratch for a simple application?

If you can say yes to all seven, you're ready for Phase 02.

---

## Topics

### 1. Docker — containers from the inside out

Most engineers learn Docker by copying `docker run` commands. That's not learning Docker, that's using Docker. You need to understand what a container actually is — a process with an isolated filesystem, network namespace, and cgroup limits — so that when something breaks you know where to look.

**What to cover:**

- What a container is — namespaces, cgroups, and how they differ from VMs
- The Docker image layer model — how layers stack, what gets cached, why order matters
- Writing efficient Dockerfiles — layer caching strategy, minimising image size
- Multi-stage builds — separating build-time and runtime dependencies
- Base image selection — `alpine` vs `debian-slim` vs `distroless` and the tradeoffs
- Docker networking — bridge, host, overlay — how containers talk to each other
- Docker volumes vs bind mounts — when to use each
- `.dockerignore` — what it does and why it matters for build context size
- Container security basics — running as non-root, read-only filesystems, `USER` instruction
- `docker inspect`, `docker stats`, `docker logs` — the diagnostic toolkit
- Image registries — pushing to Docker Hub and GitHub Container Registry (GHCR)

**The mental model that matters:** A Docker image is an immutable snapshot. A container is a running instance of that snapshot with a writable layer on top. Everything that happens inside a container's writable layer disappears when the container stops. Once that clicks, everything else makes sense.

**Recommended resources:**
- [Docker official docs — Dockerfile best practices](https://docs.docker.com/build/building/best-practices/) — the canonical reference
- [Ivan Velichko's container learning path](https://iximiuz.com/en/posts/container-learning-path/) — the best deep-dive on what containers actually are under the hood
- [dive](https://github.com/wagoodman/dive) — tool to inspect image layers and find bloat

---

### 2. Docker Compose — local environments that mirror production

Before you deploy to Kubernetes, you need to be able to run a multi-service application locally. Docker Compose is how you do that. It's also how most teams run integration tests in CI.

**What to cover:**

- `docker-compose.yml` structure — services, networks, volumes
- Environment variables and `.env` files in Compose
- Health checks and `depends_on` with condition
- Named volumes and how data persists between `docker compose down` and `up`
- Overriding with `docker-compose.override.yml` for local dev vs CI
- Running one-off commands with `docker compose run`
- Networking between services — how service names resolve as DNS

**Recommended resource:**
- [Compose file reference](https://docs.docker.com/compose/compose-file/) — bookmark this, you'll use it constantly

---

### 3. Kubernetes — the operating system for your infrastructure

Kubernetes is not easy. It has a steep learning curve and a lot of moving parts. The goal of this section is not to make you a Kubernetes expert — it's to make you operationally competent. You should be able to deploy an application, debug it when it breaks, and understand what the cluster is doing.

**What to cover:**

**Core concepts:**
- The control plane — API server, etcd, scheduler, controller manager — what each does
- Worker nodes — kubelet, kube-proxy, container runtime
- Pods — the atomic unit, why they're not containers
- Deployments — desired state, reconciliation loop, rolling updates, rollbacks
- ReplicaSets — what they are and why you almost never create them directly
- Services — ClusterIP, NodePort, LoadBalancer — when to use each
- Ingress — how external traffic reaches your application
- ConfigMaps and Secrets — externalising configuration
- Namespaces — logical isolation, resource quotas
- RBAC — roles, role bindings, service accounts — the basics of least privilege

**Operations:**
- `kubectl get`, `describe`, `logs`, `exec`, `port-forward` — daily driver commands
- Reading pod events — the first place to look when something breaks
- `kubectl rollout` — checking status, rolling back deployments
- Resource requests and limits — why they matter, what happens when you get them wrong
- Liveness and readiness probes — what they are, how to configure them, what happens when they fail
- `kubectl apply` vs `kubectl create` — declarative vs imperative

**What to skip for now:** Kubernetes networking internals (CNI plugins, eBPF), custom operators, cluster administration. That comes in later phases.

**Recommended resources:**
- [Kubernetes official interactive tutorial](https://kubernetes.io/docs/tutorials/kubernetes-basics/) — start here for the basics
- [The Kubernetes Book](https://www.nigelpoulton.com/books/) by Nigel Poulton — the most approachable book on Kubernetes
- [killer.sh](https://killer.sh/) — exam simulator, excellent for practice even if you're not taking the CKA
- [k3d](https://k3d.io/) or [kind](https://kind.sigs.k8s.io/) — run a local Kubernetes cluster in Docker, essential for practice

---

### 4. Helm — packaging Kubernetes applications

Raw Kubernetes YAML gets repetitive fast. Helm is how the industry packages and deploys applications to Kubernetes. You need to understand it from both the user side (installing charts) and the author side (writing charts).

**What to cover:**

- What Helm is — the package manager for Kubernetes
- Charts, releases, and repositories
- `helm install`, `helm upgrade`, `helm rollback`, `helm uninstall`
- Writing your own chart from scratch — `Chart.yaml`, `templates/`, `values.yaml`
- Helm template syntax — `{{ .Values.x }}`, conditionals, loops, named templates
- Overriding values — `--set` vs `-f values.yaml`
- Helm hooks — pre-install, post-upgrade jobs
- `helm lint` and `helm template` for local testing

**Recommended resource:**
- [Helm docs — chart template guide](https://helm.sh/docs/chart_template_guide/) — the official guide is genuinely good

---

### 5. Terraform — infrastructure as code

Terraform is how you stop clicking in the cloud console and start describing infrastructure as code. It's the most widely used IaC tool in the industry. Learn it until writing a module feels natural.

**What to cover:**

- HCL syntax — resources, data sources, variables, outputs, locals
- Providers — what they are, how to configure them (AWS or GCP)
- State — what it is, why it matters, what happens when it gets out of sync
- Remote state backends — S3 + DynamoDB locking (AWS) or GCS (GCP)
- `terraform init`, `plan`, `apply`, `destroy` — the workflow
- Modules — writing reusable modules, module sources, version pinning
- `terraform.tfvars` and variable files — managing configuration per environment
- `data` sources — reading existing infrastructure into Terraform
- `depends_on` and implicit vs explicit dependencies
- `terraform import` — bringing existing resources under Terraform management
- Workspaces — managing multiple environments (use with caution)
- `terraform fmt`, `terraform validate`, `tflint` — keeping your code clean

**The rule you must internalise:** Never modify infrastructure that Terraform manages by clicking in the console. Drift is the enemy. Everything goes through code.

**Recommended resources:**
- [HashiCorp Learn — Terraform tutorials](https://developer.hashicorp.com/terraform/tutorials) — structured, hands-on, free
- [tflint](https://github.com/terraform-linters/tflint) — linter for Terraform, run it in CI
- [Infracost](https://www.infracost.io/) — adds cost estimates to `terraform plan`, excellent habit to build early

---

### 6. CI/CD pipelines — GitHub Actions

A CI/CD pipeline is the automation layer that connects your code to your running infrastructure. You write code, push it, and the pipeline takes it from there — testing, building, and deploying without you touching anything manually. This is the discipline that separates professional engineering from hobby projects.

**What to cover:**

- GitHub Actions core concepts — workflows, jobs, steps, runners, events
- Triggers — `push`, `pull_request`, `workflow_dispatch`, `schedule`
- Writing multi-job pipelines with job dependencies (`needs`)
- Environment variables and GitHub secrets — never hardcode credentials
- Reusable workflows and composite actions — DRY principles in pipelines
- Docker build and push in CI — using GHCR or Docker Hub
- Deploying to Kubernetes from CI — `kubectl` in a pipeline, kubeconfig as a secret
- Caching dependencies — `actions/cache` for faster builds
- Matrix builds — testing across multiple versions in parallel
- Branch protection rules — requiring CI to pass before merge
- Pipeline security — `GITHUB_TOKEN` permissions, `pull_request_target` risks

**The pipeline discipline:** Every repository should have CI from day one, not "when it's ready." A pipeline with just a linter and a build check is better than no pipeline.

**Recommended resources:**
- [GitHub Actions documentation](https://docs.github.com/en/actions) — comprehensive and well-maintained
- [act](https://github.com/nektos/act) — run GitHub Actions locally for faster iteration

---

## Capstone project

### Full CI/CD pipeline for a microservice

This project ties everything in Phase 01 together into one deployable system. It's your first real portfolio piece.

**What you're building:**

A simple REST API (Python FastAPI or Go — your choice) with a complete automated delivery pipeline from code commit to running Kubernetes deployment.

**Requirements:**

1. **The application**
   - A REST API with at least 3 endpoints
   - Unit tests with at least 70% coverage
   - A `Dockerfile` using a multi-stage build — final image must be under 100MB
   - A `docker-compose.yml` for local development with the app + a database

2. **The infrastructure (Terraform)**
   - A cloud Kubernetes cluster — GKE Autopilot (GCP free tier) or EKS (AWS)
   - A container registry (GHCR or ECR)
   - Remote state stored in a cloud bucket with locking enabled
   - Everything in a reusable Terraform module

3. **The Kubernetes manifests**
   - A Helm chart for the application with configurable replicas, resource limits, and environment variables
   - Liveness and readiness probes configured
   - A `values-dev.yaml` and `values-prod.yaml` showing environment differentiation

4. **The pipeline (GitHub Actions)**
   - `lint` job — runs on every push to every branch
   - `test` job — runs unit tests, fails the pipeline if coverage drops below 70%
   - `build` job — builds the Docker image, pushes to registry, tags with git SHA
   - `deploy` job — deploys to Kubernetes using Helm, runs only on merge to `main`
   - Each job depends on the previous one succeeding

**Constraints — the constraints are the point:**
- The pipeline must complete in under 5 minutes
- The Docker image must run as a non-root user
- No credentials may appear anywhere in the repository — all secrets go through GitHub Secrets
- The Terraform state must never be stored locally

**Stretch goals:**
- Add a `security-scan` job using Trivy to scan the Docker image for vulnerabilities
- Add Infracost to the pipeline to show cost estimates on PRs
- Add a staging environment that deploys automatically and a production environment that requires manual approval

**What this proves on a CV:**
- You can containerise and deploy a real application end-to-end
- You understand CI/CD as a discipline, not just a tool
- You write infrastructure as code from day one
- You understand security basics (non-root containers, secrets management)

---

## How to know you're ready for Phase 02

Do not move on until you can do all of the following without googling:

- Write a multi-stage Dockerfile for a Python or Go application from memory
- Explain what happens step-by-step when you run `kubectl apply -f deployment.yaml`
- Debug a `CrashLoopBackOff` pod — find the cause and fix it
- Write a Terraform resource for a cloud storage bucket with versioning enabled
- Explain what `terraform plan` does and why you should always read it before `apply`
- Add a new job to a GitHub Actions pipeline that only runs on pushes to `main`
- Write a Helm values file that overrides the default replica count and sets a resource limit

If any of those trips you up, spend more time on it. Phase 02 builds directly on these skills and assumes they are solid.

---

## Resources summary

| Resource | Type | Cost | Link |
|---|---|---|---|
| Docker best practices | Docs | Free | [docs.docker.com](https://docs.docker.com/build/building/best-practices/) |
| Ivan Velichko — containers | Blog | Free | [iximiuz.com](https://iximiuz.com/en/posts/container-learning-path/) |
| dive (image inspector) | Tool | Free | [github.com/wagoodman/dive](https://github.com/wagoodman/dive) |
| The Kubernetes Book | Book | Paid | [nigelpoulton.com](https://www.nigelpoulton.com/books/) |
| Kubernetes interactive tutorial | Tutorial | Free | [kubernetes.io](https://kubernetes.io/docs/tutorials/kubernetes-basics/) |
| kind (local k8s) | Tool | Free | [kind.sigs.k8s.io](https://kind.sigs.k8s.io/) |
| Helm chart template guide | Docs | Free | [helm.sh](https://helm.sh/docs/chart_template_guide/) |
| HashiCorp Terraform tutorials | Tutorial | Free | [developer.hashicorp.com](https://developer.hashicorp.com/terraform/tutorials) |
| tflint | Tool | Free | [github.com/terraform-linters/tflint](https://github.com/terraform-linters/tflint) |
| GitHub Actions docs | Docs | Free | [docs.github.com](https://docs.github.com/en/actions) |
| act (local Actions runner) | Tool | Free | [github.com/nektos/act](https://github.com/nektos/act) |
| Infracost | Tool | Free | [infracost.io](https://www.infracost.io/) |

---

## Community & tracking

Open an issue with the title `[Phase 01] Starting` when you begin and `[Phase 01] Done` when you complete the capstone. Link your GitHub repo for the capstone project in the Done issue — it helps others see what a finished project looks like and gives you accountability.

---

*← [Phase 00 — The Foundation](../Phase00_Foundation/README.md) | [Phase 02 — Cloud Native Operations →](../Phase02_Cloud_Native_Operations/README.md)*
