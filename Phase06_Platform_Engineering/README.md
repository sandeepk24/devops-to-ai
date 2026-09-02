# Phase 06 — Platform Engineering

> **"A platform isn't a pile of YAML. It's a product whose customers are other engineers."**
>
> After DevSecOps, you know how to ship safely. Phase 06 is about making the *right* way the *easy* way: golden paths, templates, self-service, and clear ownership — so every team doesn't reinvent CI, observability, and security from scratch.

---

## Who this is for

| You are... | Do this |
|---|---|
| Finished Phases 01–02 (and ideally 05) | Build a minimal internal platform sketch |
| Junior DevOps asked to "make an IDP" | Learn product thinking first; start tiny |
| Already run Backstage + Crossplane in prod | Take the [self-check](#self-check--can-you-skip) |

**Time:** 5–7 weeks part-time  
**Goal:** Design and demo a paved road: one golden path from repo template → CI → deploy → metrics/alerts defaults.

**Prereqs:** Phase 01–02. Phase 05 recommended so your golden path includes security gates.

---

## Start here — four steps

```
1. Self-check     →  Already owning an IDP? Maybe skip
2. Learn          →  Platform as product → golden paths → tenancy → APIs
3. Practice       →  Template a service; measure time-to-first-deploy
4. Capstone       →  Mini platform: template + pipeline + defaults + docs portal stub
```

---

## Self-check — can you skip?

- Define platform as product (users, roadmap, SLAs for the platform itself)
- List three golden-path capabilities every app team should get for free
- Explain multi-tenancy tradeoffs (namespaces vs clusters vs accounts)
- Sketch an IDP: portal → templates → pipelines → environments
- Measure platform success with something better than "number of tools installed"
- Explain when *not* to build a platform (team of 3, no repeated pain)

---

## Learning objectives

- [ ] Interview "app teams" (even fictional personas) for platform pain
- [ ] Publish a golden-path service template (Dockerfile, CI, Helm/Kustomize, dashboards)
- [ ] Reduce time-to-hello-prod with documentation a junior can follow
- [ ] Separate platform plane vs tenant plane responsibilities
- [ ] Offer at least one self-service action (e.g. spin namespace + repo from template)
- [ ] Set a platform SLO (e.g. CI start < 2m, template deploy success rate)
- [ ] Write an RFC for a platform capability and a "not doing" list

---

## Topics

### 1. Platform as a product

Your customers are developers. They don't want seventeen YAML files; they want "ship a service."

- Personas, jobs-to-be-done, support model
- Platform roadmap vs shadow IT
- Say no: every custom snowflake multiplies support cost

### 2. Golden paths (paved roads)

A golden path is an opinionated default that is secure, observable, and boring.

Minimum golden path for a web service:
- Repo template (app layout, lint/test, Dockerfile)
- CI that builds, tests, scans (Phase 05), pushes
- Deploy via GitOps (Phase 02)
- Metrics, logs, traces baselines + example alerts
- README: "day 1 / day 2" operations

Optional paths later: jobs/cron, data services, ML services (Phase 04).

### 3. Internal Developer Portal (IDP)

- Catalog of services, owners, docs, on-call
- Software templates (Backstage, Port, or even a well-made GitHub template org)
- Scorecards: does this service have on-call? dashboards? scans green?
- Start with a static portal or GitHub org README if Backstage is too heavy

### 4. Tenancy & isolation

- Namespaces + quotas + network policies
- Cluster-per-team vs namespace-per-team vs account-per-env
- Shared services (observability, secrets) vs per-tenant stacks
- Cost attribution (labels, projects, chargeback lite)

### 5. Platform APIs & automation

- Everything a human clicks should be an API/CRD/script eventually
- Crossplane / Terraform modules / Helm charts as the "platform SDK"
- GitOps as the control plane for desired state
- Asynchronous provisioning — don't block the portal UI on 15-minute applies

### 6. Measuring platform value

| Metric | Why it matters |
|---|---|
| Time to first deploy (new service) | Onboarding friction |
| % services on golden path | Adoption |
| Change fail rate / MTTR for platform | Trust |
| Support tickets per team per month | Hidden tax |
| Scan/policy pass rate | Security default working |

If nobody adopts your platform, you built a museum.

### 7. Enabling vs ticket-driven ops

- Self-service > "file a ticket for a namespace"
- Guardrails > unrestricted cluster-admin for everyone
- Documentation as a feature — versioned, searchable, with examples

---

## Capstone

### Mini internal platform

**Build a thin vertical slice:**

1. **Service template repo** — app + Dockerfile + CI + Helm chart + example Grafana dashboard JSON + SECURITY notes
2. **Golden path doc** — a junior follows it and deploys to kind/k3d in < 2 hours
3. **Provisioning script or Actions workflow** — creates repo from template *or* scaffolds a new service folder
4. **Catalog stub** — markdown or simple portal page listing services, owners, links to dashboards
5. **Platform RFC** — one page: problem, proposal, non-goals, success metrics

**Definition of done:**
- [ ] Second person (or rubber-duck checklist) can create a service from the template
- [ ] Default path includes test + image scan gate
- [ ] New service gets `/health`, metrics endpoint, and a starter alert rule
- [ ] You publish time-to-first-deploy before/after (even if rough)
- [ ] RFC lists at least three things you will *not* build yet

**Stretch:** Backstage template; Crossplane XRD for a database claim; scorecards in CI.

> Starter material will live under `projects/golden-path-platform/` as the phase matures.

---

## Ready for Phase 07?

You can describe your platform users, ship a golden path with security/observability defaults, and measure adoption. AIOps (Phase 07) automates *operations* — without a platform baseline, automation just scales chaos.

---

## Resources

| Resource | Why |
|---|---|
| [Team Topologies](https://teamtopologies.com/) | Platform team interaction modes |
| [CNCF Platforms whitepaper](https://tag-app-delivery.cncf.io/whitepapers/platforms/) | Shared language |
| [Backstage](https://backstage.io/) | IDP reference |
| [Crossplane](https://www.crossplane.io/) | Control-plane style provisioning |
| Humanitec / Port / Cortex docs | How vendors frame golden paths (learn concepts, not lock-in) |

---

## Track your progress

```
[Phase 06] Starting — your-handle
[Phase 06] Done — your-handle
```

---

*← [Phase 05 — DevSecOps](../Phase05_DevSecOps/README.md) | [Phase 07 — AIOps →](../Phase07_AIOps_Autonomous_Operations/README.md)*
