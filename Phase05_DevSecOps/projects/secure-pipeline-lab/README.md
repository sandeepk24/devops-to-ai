# Capstone: Secure pipeline lab

> **Phase 05 project** — finish this before [Phase 06](../../../Phase06_Platform_Engineering/README.md).  
> Phase guide: [Phase 05 README](../../README.md)

You're putting seatbelts on a tiny API: scan deps and the image, emit an SBOM, refuse a privileged Kubernetes manifest, and leave a CI job that fails on HIGH/CRITICAL findings. That's DevSecOps you can demo — not a slide deck about "shift left."

---

## Paths

| Path | Needs | What you prove |
|---|---|---|
| **A — Laptop (start here)** | Docker Desktop (or Engine) running | Local scan + SBOM + catch bad manifest |
| **B — Cluster** | kind/k3d, kubectl, Kyverno | Admission denies privileged Deployment |

**Do Path A completely.** Add Path B when the laptop path feels boring.

---

## What's in this folder

```
secure-pipeline-lab/
├── app/                         ← tiny FastAPI service
├── Dockerfile
├── requirements.txt             ← keep this clean for green scans
├── fixtures/
│   └── requirements-vuln-demo.txt  ← optional: prove SCA can fail
├── k8s/
│   ├── deployment-good.yaml
│   └── deployment-bad-privileged.yaml
├── policy/
│   └── disallow-privileged.yaml
├── scripts/
│   ├── scan_local.sh
│   ├── generate_sbom.sh
│   ├── check_manifests.sh
│   ├── wait_kyverno.sh          ← Path B helper
│   └── smoke_test.sh
├── .trivyignore.example
└── docs/exceptions.md
```

CI lives at the **repo root**: [`.github/workflows/phase05-secure-ci.yml`](../../../../.github/workflows/phase05-secure-ci.yml)  
(GitHub only runs workflows from `.github/workflows/` at the repo root — not inside this folder.)

---

## Path A — first win (~20 minutes)

```bash
# From the devops-to-ai repo root:
cd Phase05_DevSecOps/projects/secure-pipeline-lab

# Docker must actually be running (whale icon / `docker info` works)
docker build -t secure-lab:local .

./scripts/smoke_test.sh
```

What smoke does:

1. Filesystem + image scan (HIGH/CRITICAL) via Trivy-in-Docker  
2. SBOM written under `out/`  
3. Manifest checker — **good** passes, **bad** fails  

First Trivy run can take a few minutes while it pulls the scanner image and vuln DB. Later runs are faster.

If Trivy finds something real in base packages: bump the base image, or document a temporary waiver in `docs/exceptions.md` (and mirror IDs in a `.trivyignore` only while that row is active). **Don't delete the gate.**

### Break the gate on purpose

```bash
# Should FAIL
./scripts/check_manifests.sh k8s/deployment-bad-privileged.yaml && echo "unexpected pass" || echo "caught privileged — good"

# Should PASS
./scripts/check_manifests.sh k8s/deployment-good.yaml
```

Optional SCA demo (don't leave this as your main requirements):

```bash
# See pip-audit complain, then go back to the clean file
python -m pip install pip-audit
pip-audit -r fixtures/requirements-vuln-demo.txt || echo "gate failed — that's the lesson"
```

---

## Stuck? Quick fixes

| Symptom | Likely cause | What to try |
|---|---|---|
| `docker: command not found` | Docker not on PATH | Install Docker Desktop; open a new terminal |
| `Cannot connect to the Docker daemon` | Docker app not running | Start Docker Desktop; wait until it's idle |
| `Image secure-lab:local not found` | Forgot to build | `docker build -t secure-lab:local .` |
| Trivy hangs a long time | First DB/image pull | Wait; check network; re-run once |
| Scan fails on base OS CVE | Real finding in `python:*-slim` | Upgrade base tag/digest or use `docs/exceptions.md` |
| Actions never run | Wrong file name / path filter | Workflow is `phase05-secure-ci.yml`; change files under this lab or use **workflow_dispatch** |

---

## What already works (Path A)

- [x] Small API + multi-stage non-root Dockerfile  
- [x] Trivy FS + image scripts (Docker wrapper — no local Trivy install)  
- [x] SBOM generation (SPDX JSON → `out/`)  
- [x] Local privileged-manifest detector  
- [x] Good vs bad Deployment examples  
- [x] GitHub Actions: `phase05-secure-ci.yml` at repo root  

---

## Your tasks (level up)

### Understand & operate
- [ ] Read `scripts/scan_local.sh` — know why `--exit-code 1` matters  
- [ ] Open a Trivy report and explain one finding in plain language  
- [ ] Run `./scripts/generate_sbom.sh` and skim `out/sbom.spdx.json` for package names  
- [ ] Explain why `deployment-bad-privileged.yaml` is dangerous  

### CI
- [ ] Confirm Actions run for `phase05-secure-ci` (push a lab change, or **Actions → Run workflow**)  
- [ ] Skim which step would fail the job on a HIGH CVE  
- [ ] Fill one example row in `docs/exceptions.md` as if you needed a temporary waiver  

### Stretch
- [ ] Path B: kind + Kyverno + prove bad Deployment is denied  
- [ ] Cosign sign/verify locally ([supply-chain cheatsheet](../../cheatsheets/supply-chain.md))  
- [ ] Add a note in your fork about OIDC vs long-lived cloud keys in CI  

---

## Path B — Kyverno on kind (optional)

```bash
kind create cluster --name phase05

kubectl apply -f https://github.com/kyverno/kyverno/releases/download/v1.13.0/install.yaml
./scripts/wait_kyverno.sh

kubectl apply -f policy/disallow-privileged.yaml

kubectl apply -f k8s/deployment-good.yaml          # should work
kubectl apply -f k8s/deployment-bad-privileged.yaml # should DENY
```

If deny doesn't happen: Kyverno still starting, wrong context (`kubectl config current-context`), or policy not applied — run `kubectl get clusterpolicy` and `kubectl -n kyverno get pods`.

---

## Definition of done

- [ ] `docker build -t secure-lab:local .` succeeds  
- [ ] `./scripts/smoke_test.sh` passes (or exceptions documented with owner + expiry)  
- [ ] Bad privileged manifest fails `check_manifests.sh`  
- [ ] You can explain SCA vs image scan vs SBOM in one minute  
- [ ] You know `phase05-secure-ci` is the workflow that fails the job  
- [ ] Notes say whether you completed Path B  

---

## Sharing

Open `[Phase 05] Done` on [devops-to-ai](https://github.com/sandeepk24/devops-to-ai) with a scan log snippet and (optional) Kyverno deny message.

→ [Phase 06 — Platform Engineering](../../../Phase06_Platform_Engineering/README.md)
