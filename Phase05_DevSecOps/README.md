# Phase 05 — DevSecOps & Supply Chain Security

> **"If you can deploy it, someone can exploit it — unless you build security into the path, not onto the end."**
>
> Phases 00–04 got you shipping and running systems (including LLM platforms). Phase 05 is where you stop treating security as a ticket that arrives after the outage. You bake checks into CI, images, clusters, and policy — so "secure enough to sleep" is a default, not a heroics weekend.

---

## Who this is for

| You are... | Do this |
|---|---|
| Finished Phase 02+ (CI + containers + basic K8s) | Work every topic; build the secure-pipeline lab |
| Junior DevOps — scans fail and you click "ignore" | Focus on *why* each gate exists, then automate one path |
| Already run Sigstore, OPA/Kyverno, and SCA in prod | Take the [self-check](#self-check--can-you-skip) |

**Time:** 4–6 weeks part-time  
**Goal:** A pipeline that builds, scans, signs, and only deploys what policy allows — plus a clear story for interviews about supply-chain risk.

**Prereqs:** Phase 01 (Docker/CI) strongly recommended; Phase 02 (K8s) for admission policy labs.

---

## Start here — four steps

```
1. Self-check     →  Already doing supply-chain security at work? Maybe skip
2. Learn          →  Shift-left → SCA/SAST → images → signing → policy → runtime
3. Practice       →  Add scanners to a Phase 01-style pipeline
4. Capstone       →  Secure delivery path with fail-the-build gates + admission policy
```

---

## Self-check — can you skip?

If you can do **all** of these without looking things up, skip to [Phase 06](../Phase06_Platform_Engineering/README.md):

- Explain SBOM, SCA, and SAST in one sentence each
- Add Trivy (or equivalent) to CI so HIGH vulns fail the job
- Sign a container image and verify the signature before deploy
- Write a Kyverno or OPA policy that blocks privileged pods
- Describe what "poisoned dependency" and "typosquat" mean
- Know what *not* to put in Git (and how secrets still leak via CI logs)

---

## Learning objectives

- [ ] Map the software supply chain from laptop → registry → cluster
- [ ] Run SCA + image scanning in CI with actionable fail criteria
- [ ] Generate and store an SBOM for a release artifact
- [ ] Sign images (Sigstore/Cosign) and verify on admission or deploy
- [ ] Enforce baseline policy (no `:latest`, no privileged, require labels)
- [ ] Threat-model a simple service (STRIDE-lite is enough)
- [ ] Explain secret management options (GitHub Actions OIDC, vault, sealed secrets)

---

## Topics

### 1. Mindset — security as a pipeline property

Security work that only happens in annual audits fails. Your job is to make the **happy path** the secure path: scanners in CI, defaults in charts, policy in the cluster.

```
Code → build → test → SCA/SAST → image scan → sign → push
                                              ↓
                                    policy checks on deploy
                                              ↓
                                         runtime signals
```

### 2. Dependencies & SBOMs

- SCA tools (e.g. Dependabot, Trivy fs, Grype, Snyk) — know what they catch
- Lockfiles matter; "works on my machine" floating versions are a risk
- SBOM (CycloneDX / SPDX) — inventory of what you shipped
- Typosquatting and malicious packages — verify names, prefer pinned digests

### 3. Static analysis & IaC security

- SAST for app code (language-dependent)
- Checkov / tfsec / Trivy config for Terraform and K8s YAML
- Same red flags as Phase 03 trust cheatsheet: `*`, `0.0.0.0/0`, missing limits

### 4. Container image hardening

- Minimal base images, non-root, read-only root FS where possible
- Multi-stage builds (you did this in Phase 01 — now scan the *final* image)
- Trivy/Grype in CI; severity thresholds that match your risk appetite
- Distroless / chainguard-style images — tradeoffs for debugging

### 5. Signing & provenance

- Why "tag mutable" is a lie — prefer digest pins
- Cosign / Sigstore keyless (OIDC) vs keyful
- SLSA provenance ideas — who built this, from which commit?
- Verify signature in CD or with admission controllers

### 6. Policy as code

- Kyverno or OPA Gatekeeper — validate/mutate/generate
- Start with a small policy pack: require `runAsNonRoot`, block `:latest`, require `app` label
- Break-glass procedures — policy without escape hatches strands on-call

### 7. Secrets & identity

- No long-lived cloud keys in GitHub secrets if OIDC works
- Short-lived credentials; least privilege IAM roles for CI
- Sealed Secrets / External Secrets / Vault — pick one story and go deep enough to demo
- Never log secrets (AI PR bots included — Phase 03 lesson still applies)

### 8. Runtime & response

- Basic runtime signals: Falco-style detection concepts (you don't need prod Falco on day one)
- Image drift — what's running vs what was signed
- Incident notes: how supply-chain compromise shows up (unexpected egress, new process, new package)

---

## Capstone (lab)

### Secure delivery path

Take your Phase 01 microservice (or a tiny API) and make delivery boringly safe.

**Build:**
1. CI job: lint → test → build image → **Trivy scan (fail on HIGH/CRITICAL)** → push by digest
2. Generate an SBOM artifact and upload it with the release
3. Sign the image with Cosign (keyless in GitHub Actions is ideal)
4. Cluster policy (kind/k3d is fine): block privileged pods + require non-root
5. Deploy only if signature verifies (script or policy)
6. Short `SECURITY.md` / runbook: how to rotate a leaked CI token

**Definition of done:**
- [ ] PR pipeline fails on a known-bad base image or planted CRITICAL CVE
- [ ] SBOM exists for a tagged release
- [ ] Image is signed; verify command documented
- [ ] Policy rejects a privileged Pod YAML you try on purpose
- [ ] README explains how a teammate reproduces the gates

**Stretch:** OIDC to cloud deploy role; Dependabot + auto-PR triage notes; Kyverno policy reports in CI.

> Starter code for this phase will land under `projects/secure-pipeline/` — until then, extend your Phase 01 repo.

---

## Ready for Phase 06?

You can explain your supply chain end-to-end, fail builds on real risk, and enforce at least one cluster policy without paging yourself. Platform engineering (Phase 06) assumes security defaults exist — golden paths without gates are just golden footguns.

---

## Resources

| Resource | Why |
|---|---|
| [OWASP Top 10 CI/CD](https://owasp.org/www-project-top-10-ci-cd-security-risks/) | Pipeline threat model |
| [Trivy](https://aquasecurity.github.io/trivy/) | Practical scanner |
| [Sigstore / Cosign](https://docs.sigstore.dev/) | Signing |
| [Kyverno docs](https://kyverno.io/docs/) | K8s policy |
| [SLSA](https://slsa.dev/) | Provenance model |
| [NIST SSDF](https://csrc.nist.gov/projects/ssdf) | Secure development framing |

---

## Track your progress

```
[Phase 05] Starting — your-handle
[Phase 05] Done — your-handle
```

---

*← [Phase 04 — MLOps & LLMOps](../Phase04_MLOps_LLMOps/README.md) | [Phase 06 — Platform Engineering →](../Phase06_Platform_Engineering/README.md)*
