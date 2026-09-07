# Phase 06 — Platform Engineering

> **"If every team reinvents CI, deploy, and dashboards, you don't have a platform — you have a wiki of snowflakes."**
>
> Phases 00–05 taught you to ship, observe, and secure services. Phase 06 flips the lens: you're not only running *your* app — you're building the **paved road** other engineers walk on. Golden paths, templates, light self-service. Treat the platform like a product.

---

## Who this is for

| You are... | Do this |
|---|---|
| Finished Phase 01 (and ideally 05) | Work the topics, then the golden-path template |
| Junior DevOps — tired of copy-paste Deployments | Start **Path A (scaffold on a laptop)**; kind is Path B |
| Already own an IDP / golden paths in prod | Take the [self-check](#self-check--can-you-skip) — skip to Phase 07 if you pass |

**Time:** 4–6 weeks part-time  
**Goal:** A service template a teammate can clone/scaffold, run locally, and (optionally) deploy to kind — plus docs that measure whether people actually use it.

---

## Start here — four steps

```
1. Self-check     →  Already shipping paved roads at work? Maybe skip to Phase 07
2. Learn          →  Platform-as-product → golden paths → templates → tenancy → metrics
3. Practice       →  scripts/new_service.sh → compose up → curl
4. Capstone       →  Golden-path template + "how to use this" docs (+ kind stretch)
```

**You do not need Backstage on day one.** Path A is a scaffold script + Compose. Path B is kind/k3d. A real IDP UI is stretch — the *ideas* matter more than the logo.

**Cheatsheets:**

| Topic | Cheatsheet |
|---|---|
| Golden paths & paved roads | [cheatsheets/golden-paths.md](./cheatsheets/golden-paths.md) |
| IDP basics (without boiling the ocean) | [cheatsheets/idp-basics.md](./cheatsheets/idp-basics.md) |
| Tenancy & self-service guardrails | [cheatsheets/tenancy-self-service.md](./cheatsheets/tenancy-self-service.md) |

**What you need:**

| Thing | Why | Notes |
|---|---|---|
| Docker (running) | Local Compose path | `docker info` must work |
| bash + sed | Scaffold script | macOS/Linux fine |
| kind/k3d + kubectl (optional) | Path B deploy | After Path A feels natural |
| Phase 01 comfort | Dockerfile, K8s basics | Soft gate |

---

## Self-check — can you skip?

If you can do **all** of these without looking things up, skip to [Phase 07](../Phase07_AIOps_Autonomous_Operations/README.md):

- Explain golden path vs "you can do anything" in one plain paragraph
- Name three things a good service template should include by default
- Sketch what an Internal Developer Platform (IDP) is — and what it is *not*
- List two platform success metrics that aren't "number of clusters"
- Describe a safe self-service boundary (what users can create vs what needs approval)
- Say why thinnest viable platform beats a giant portal nobody opens

Otherwise stay here. Phase 07 assumes some paved roads exist before you automate remediation.

---

## Learning objectives

By the end of Phase 06, answer **yes** to all of these:

- [ ] Explain platform-as-product (users = other engineers; roadmap = their pain)
- [ ] Ship a golden-path template that includes app + container + health + basic CI shape
- [ ] Document "day 1" for a new service so a junior can follow it without Slack archaeology
- [ ] Reason about namespaces / tenancy / quotas at a basic level
- [ ] Pick 2–3 platform metrics and know how you'd measure them
- [ ] Resist boiling the ocean (Backstage later; template that works today)

---

## Topics

Work in order. Don't install Backstage before you have one template people actually use.

### 1. Platform as a product

Your customers are application teams. Your competitors are: copy-paste from that one repo that works, asking you on Slack, or doing something unsafe because it's faster.

```
Bad platform                 Good-enough platform
─────────────                ────────────────────
"Here's 40 wiki pages"       "Run this script, get a running service"
Ticket for every namespace    Self-service within guardrails
Optional security            Secure defaults on the paved road
No idea who uses what        Adoption + time-to-first-deploy measured
```

Interview line: "I reduce cognitive load for other engineers — that's the product."

### 2. Golden paths (paved roads)

A **golden path** is the blessed way to do the common thing: new HTTP service, new worker, new cron. Opinionated. Boring on purpose. Escape hatches exist, but the default should be what you'd want in an incident at 2am.

Include by default: health endpoints, non-root image, resource requests, logs/metrics hooks (even if stubs), CI shape, a short runbook.

→ [golden-paths cheatsheet](./cheatsheets/golden-paths.md)

### 3. Templates beat tickets

The fastest platform feature is often: `./scripts/new_service.sh payments-api` → folder ready → `docker compose up` → green health check.

Cookiecutter, copier, or a humble bash scaffold all count. Fancy generators without a maintained skeleton become abandonware.

### 4. IDP — portal optional, interface required

An **Internal Developer Platform** is the product surface: "create service," "get logs," "request env." Tools like Backstage are one UI. YAML + scripts + docs can be an IDP v0.

Don't confuse "we installed Backstage" with "we have a platform." Empty catalog = empty product.

→ [IDP cheatsheet](./cheatsheets/idp-basics.md)

### 5. Tenancy & self-service

Self-service without guardrails is chaos. Guardrails without self-service is a ticket queue.

Start simple: one namespace per team/service, ResourceQuotas, NetworkPolicies later, who can `kubectl apply` what. Phase 05's admission policies belong on the paved road.

→ [tenancy cheatsheet](./cheatsheets/tenancy-self-service.md)

### 6. Metrics that prove the platform works

Vanity: "we have 12 tools."  
Useful: time-to-first-deploy for a new hire, % of services on the golden path, ticket volume for "please create a pipeline," paved-road version freshness.

If nobody uses the template, the template failed — not the users.

---

## Capstone project

### Golden-path service template

**Starter:** [projects/golden-path-template/](./projects/golden-path-template/)

| Path | Needs | Outcome |
|---|---|---|
| **A — Laptop (start here)** | Docker | Scaffold a service, Compose up, hit `/health` |
| **B — Cluster** | kind/k3d | Deploy the scaffolded service with the included manifests |

**Already wired for Path A:** skeleton service, `new_service.sh`, Compose, health check, CI stub, catalog stub, platform metrics worksheet.

**Your job:** scaffold at least one service, run it, write "day 1" notes a teammate could follow, and (stretch) deploy to kind.

Full walkthrough → [projects/golden-path-template/README.md](./projects/golden-path-template/README.md)

---

## Ready for Phase 07?

Don't move on until you can do these **without googling**:

1. Golden path vs snowflake — and why defaults should be secure  
2. Show a template (or scaffold output) another junior could use  
3. Name two platform metrics you'd put on a slide for leadership  
4. Explain IDP v0 without requiring Backstage  
5. Sketch one self-service action + one guardrail that must stay  

Phase 07 (AIOps) assumes paved roads exist — you don't want self-healing that reinvents CI for every team.

---

## Resources

| Resource | What it's for |
|---|---|
| [Team Topologies](https://teamtopologies.com/) (book) | Platform vs stream-aligned teams |
| [CNCF Platforms whitepaper](https://tag-app-delivery.cncf.io/whitepapers/platforms/) | Shared vocabulary |
| [Backstage](https://backstage.io/) | IDP UI (stretch) |
| [Humanitec / score / CNOE](https://cnoe.io/) | Platform tooling landscape (skim) |
| Repo cheatsheets | Day-to-day lookup |

---

## Track your progress

```
[Phase 06] Starting — your-handle
[Phase 06] Done — your-handle
```

When Done, share: screenshot of `/health` from a scaffolded service, and one sentence on who the "customer" of your platform is.

---

*← [Phase 05 — DevSecOps](../Phase05_DevSecOps/README.md) | [Phase 07 — AIOps →](../Phase07_AIOps_Autonomous_Operations/README.md)*
