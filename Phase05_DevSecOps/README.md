# Phase 05 — DevSecOps & Supply Chain Security

> **"A green deploy that ships a known critical CVE is still a failed deploy — you just haven't been paged yet."**
>
> Phases 00–04 taught you to build, observe, and run services (including LLM ones). Phase 05 is about making the *happy path* the *safe path*: scan early, prove what you shipped, and stop bad pods at the gate.

---

## Who this is for

| You are... | Do this |
|---|---|
| Finished Phase 01 (Docker + CI) and ideally Phase 04 | Work the topics, then the secure-pipeline lab |
| Junior DevOps — heard of Trivy/SBOMs, never gated a merge | Start **Path A (laptop scans)**; cluster policy is Path B |
| Already run SCA + image signing + admission policy in prod | Take the [self-check](#self-check--can-you-skip) — skip to Phase 06 if you pass |

**Time:** 4–6 weeks part-time  
**Goal:** A pipeline that fails on serious vulns, produces an SBOM, signs (or documents signing), and a policy that blocks privileged pods.

---

## Start here — four steps

```
1. Self-check     →  Already gating supply chain in prod? Maybe skip to Phase 06
2. Learn          →  Shift-left → scan → SBOM/sign → policy → secrets hygiene
3. Practice       →  scripts/scan_local.sh on the lab app (Docker only)
4. Capstone       →  Secure CI + good/bad manifests + policy notes
```

**You do not need a cluster on day one.** Path A uses Docker + Trivy-in-a-container. Path B adds kind/k3d + Kyverno when you're ready.

**Cheatsheets:**

| Topic | Cheatsheet |
|---|---|
| Scanning (SCA / image / FS) | [cheatsheets/scanning.md](./cheatsheets/scanning.md) |
| SBOM, signing, provenance | [cheatsheets/supply-chain.md](./cheatsheets/supply-chain.md) |
| Policy-as-code (Kyverno basics) | [cheatsheets/policy-as-code.md](./cheatsheets/policy-as-code.md) |

**What you need:**

| Thing | Why | Notes |
|---|---|---|
| Docker (running) | Build images + run Trivy without a local install | `docker info` must work |
| GitHub account (optional) | See Actions gates on a PR | Workflow: `.github/workflows/phase05-secure-ci.yml` |
| kind/k3d + kubectl (optional) | Path B admission policy | After Path A is solid |
| Phase 01 comfort | Dockerfile + CI basics | Soft gate, not a quiz |

---

## Self-check — can you skip?

If you can do **all** of these without looking things up, skip to [Phase 06](../Phase06_Platform_Engineering/README.md):

- Explain SCA vs SAST vs container image scanning in one sentence each
- Fail a CI job on HIGH/CRITICAL CVEs with a tool you've actually configured
- Say what an SBOM is and why auditors ask for it
- Sketch image signing (Cosign/Sigstore) and where verification happens
- Write or apply a policy that blocks `privileged: true` pods
- Name two pipeline secret anti-patterns (and what to use instead)

Otherwise stay here. Phase 06 assumes paved roads that are *already* somewhat safe.

---

## Learning objectives

By the end of Phase 05, answer **yes** to all of these:

- [ ] Put dependency and image scans in CI and know what "fail the build" means in practice
- [ ] Generate an SBOM for an image or filesystem and point to it in a PR
- [ ] Explain signing vs scanning (different jobs — both matter)
- [ ] Apply (or dry-run) a policy that blocks privileged containers
- [ ] Keep secrets out of git and prefer OIDC/short-lived creds where you can
- [ ] Document an exception process (temporary ignore ≠ forever ignore)

---

## Topics

Work in order. Don't jump to Cosign before you can read a Trivy report.

### 1. Shift-left — security as part of shipping

Security that only happens in a quarterly audit arrives too late. Shift-left means: catch the cheap mistakes in the PR, not in production.

```
Commit → lint/test → SCA (deps) → build image → image scan → SBOM
                                              → sign (stretch)
                                              → deploy only if gates pass
Cluster admission policy = last seatbelt
```

You're not becoming a full-time AppSec engineer. You're making *default* DevOps work hard to do unsafely.

### 2. Dependency & image scanning

- **SCA** — "are my libraries known-bad?" (`pip-audit`, npm audit, Trivy fs)
- **Image scan** — OS packages + app deps in the final image (Trivy, Grype)
- **SAST** — static code smells / sinks (nice-to-have here; don't boil the ocean)

Severity gates matter: failing on every LOW will train people to skip the job. Start with **HIGH/CRITICAL**, tune from there.

→ [scanning cheatsheet](./cheatsheets/scanning.md)

### 3. SBOMs and signing (supply chain)

An **SBOM** is an ingredients list. Signing says "this artifact came from us / this pipeline." Neither replaces scanning — they answer different questions when something blows up six months later.

→ [supply-chain cheatsheet](./cheatsheets/supply-chain.md)

### 4. Policy-as-code at the cluster

CI can be skipped. Admission policy is harder to skip. Start with one rule juniors actually hit: **no privileged pods**. Kyverno policies read like Kubernetes YAML — friendlier first step than full Rego for many teams.

→ [policy-as-code cheatsheet](./cheatsheets/policy-as-code.md)

### 5. Secrets & pipeline identity

Long-lived cloud keys in GitHub secrets are common and fragile. Prefer OIDC to cloud roles where your org supports it. Never commit `.env` with real tokens. Rotate when leaked — don't just "delete the file from main" and hope history is fine.

### 6. Exceptions without lying to yourself

Sometimes you must ship with a known CVE (no fix yet, compensating control). Track it: ticket, expiry, owner. Infinite `.trivyignore` with no owner is how breaches stay quiet.

---

## Capstone project

### Secure pipeline lab

**Starter:** [projects/secure-pipeline-lab/](./projects/secure-pipeline-lab/)

| Path | Needs | Outcome |
|---|---|---|
| **A — Laptop (start here)** | Docker | Scan app + image, SBOM, catch bad manifest locally |
| **B — Cluster** | kind/k3d + Kyverno | Policy blocks privileged Deployment on apply |

**Already wired for Path A:** small API + Dockerfile, Trivy/SBOM scripts, good vs privileged manifests, local policy checker, and repo-root Actions workflow (`phase05-secure-ci`).

**Your job:** run the scans, break a gate on purpose (privileged manifest or the vuln demo fixture), put it back, and know *why* the privileged YAML is rejected. Cluster + Cosign are stretch — finish the laptop path first.

Full walkthrough → [projects/secure-pipeline-lab/README.md](./projects/secure-pipeline-lab/README.md)

---

## Ready for Phase 06?

Don't move on until you can do these **without googling**:

1. SCA vs image scan vs SBOM vs signature — four different jobs  
2. Show a CI config that fails on HIGH/CRITICAL  
3. Explain where admission policy sits vs CI  
4. Name a safe way to handle a temporary CVE exception  
5. Spot a privileged pod manifest in under a minute  

Phase 06 (platform engineering) assumes golden paths that already include some of these gates.

---

## Resources

| Resource | What it's for |
|---|---|
| [Trivy docs](https://aquasecurity.github.io/trivy/) | FS + image scanning |
| [Sigstore / Cosign](https://docs.sigstore.dev/) | Signing & verify |
| [Kyverno docs](https://kyverno.io/docs/) | Policy-as-code |
| [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/) | Extra SCA context |
| [SLSA](https://slsa.dev/) | Supply-chain levels (interview signal) |
| Repo cheatsheets | Day-to-day lookup |

---

## Track your progress

```
[Phase 05] Starting — your-handle
[Phase 05] Done — your-handle
```

When Done, share: a failing scan screenshot (or log), a passing run after the fix, and whether you did Path B.

---

*← [Phase 04 — MLOps & LLMOps](../Phase04_MLOps_LLMOps/README.md) | [Phase 06 — Platform Engineering →](../Phase06_Platform_Engineering/README.md)*
