# Capstone: Secure pipeline lab

> **Phase 05 project** — finish this before [Phase 06](../../../Phase06_Platform_Engineering/README.md).  
> Phase guide: [Phase 05 README](../../README.md)

You're going to put seatbelts on a tiny API: scan dependencies and the image, emit an SBOM, refuse a privileged Kubernetes manifest, and leave a CI workflow that fails when HIGH/CRITICAL findings show up. That's DevSecOps you can demo — not a slide about "shift left."

---

## Paths

| Path | Needs | What you prove |
|---|---|---|
| **A — Laptop (start here)** | Docker | Local scan + SBOM + catch bad manifest |
| **B — Cluster** | kind/k3d, kubectl, Kyverno | Admission denies privileged Deployment |

**Do Path A completely.** Add Path B when Docker scans feel boring.

---

## What's in this folder

```
secure-pipeline-lab/
├── app/                         ← tiny FastAPI service
├── Dockerfile
├── requirements.txt
├── k8s/
│   ├── deployment-good.yaml     ← non-root, not privileged
│   └── deployment-bad-privileged.yaml
├── policy/
│   └── disallow-privileged.yaml ← Kyverno ClusterPolicy
├── scripts/
│   ├── scan_local.sh
│   ├── generate_sbom.sh
│   ├── check_manifests.sh
│   └── smoke_test.sh
└── docs/exceptions.md
```

CI lives at the **repo root**: [`.github/workflows/phase05-secure-ci.yml`](../../../../.github/workflows/phase05-secure-ci.yml) (GitHub only runs workflows from there).

---

## Path A — first win (~20 minutes)

```bash
cd Phase05_DevSecOps/projects/secure-pipeline-lab

# 1. Build the image
docker build -t secure-lab:local .

# 2. Run local security checks (Trivy via Docker — no local install needed)
./scripts/smoke_test.sh
```

What smoke does:

1. Filesystem + image scan (HIGH/CRITICAL)
2. SBOM written under `out/`
3. Manifest checker — **good** passes, **bad** fails

If Trivy finds something real in base packages, read the report, bump the base digest or document an exception in `docs/exceptions.md`. Don't delete the gate.

### Break the gate on purpose

```bash
# Should FAIL
./scripts/check_manifests.sh k8s/deployment-bad-privileged.yaml && echo "unexpected pass" || echo "caught privileged — good"

# Should PASS
./scripts/check_manifests.sh k8s/deployment-good.yaml
```

Optional: temporarily pin an ancient package in `requirements.txt`, re-run `./scripts/scan_local.sh`, watch SCA complain, then upgrade again.

---

## What already works (Path A)

- [x] Small API + multi-stage non-root Dockerfile
- [x] Trivy FS + image scripts (Docker wrapper)
- [x] SBOM generation (SPDX JSON → `out/`)
- [x] Local privileged-manifest detector
- [x] Good vs bad Deployment examples
- [x] GitHub Actions workflow at repo root (`.github/workflows/phase05-secure-ci.yml`)

---

## Your tasks (level up)

### Understand & operate
- [ ] Read `scripts/scan_local.sh` — know why `--exit-code 1` matters
- [ ] Open a Trivy report and explain one finding in plain language
- [ ] Run `./scripts/generate_sbom.sh` and skim `out/sbom.spdx.json` for package names
- [ ] Explain why `deployment-bad-privileged.yaml` is dangerous

### CI
- [ ] Push a fork / branch and confirm Actions runs `secure-ci.yml` (or run `act` locally if you use it)
- [ ] Note in your fork README how you'd waive a CVE temporarily (`docs/exceptions.md`)

### Stretch
- [ ] Path B: kind cluster + Kyverno + apply policy + prove bad Deployment is denied
- [ ] Cosign sign/verify the local image ([supply-chain cheatsheet](../../cheatsheets/supply-chain.md))
- [ ] Add `pip-audit` step beside Trivy in CI

---

## Path B — Kyverno on kind (optional)

```bash
kind create cluster --name phase05
kubectl apply -f https://github.com/kyverno/kyverno/releases/download/v1.13.0/install.yaml
# wait until kyverno pods are ready
kubectl apply -f policy/disallow-privileged.yaml

kubectl apply -f k8s/deployment-good.yaml          # should work
kubectl apply -f k8s/deployment-bad-privileged.yaml # should DENY
```

If deny doesn't happen: Kyverno not ready, wrong namespace, or policy still in Audit mode — check `kubectl get clusterpolicy`.

---

## Definition of done

- [ ] `docker build -t secure-lab:local .` succeeds
- [ ] `./scripts/smoke_test.sh` passes (or exceptions documented with owner + expiry)
- [ ] Bad privileged manifest fails `check_manifests.sh`
- [ ] You can explain SCA vs image scan vs SBOM in one minute
- [ ] CI workflow exists and you know which step fails the job
- [ ] Notes say whether you completed Path B

---

## Sharing

Open `[Phase 05] Done` on [devops-to-ai](https://github.com/sandeepk24/devops-to-ai) with a scan log snippet and (optional) Kyverno deny message.

→ [Phase 06 — Platform Engineering](../../../Phase06_Platform_Engineering/README.md)
