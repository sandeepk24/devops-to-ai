# devops-to-ai

> A project-driven roadmap from Linux basics to AI-native infrastructure — with capstone projects you can demo in interviews, not just talk about.

Most learning paths are tool lists. This one is a **career arc**: **ten phases (00–09)** that build on each other, each ending in something real you ship.

**Available now (full guides + projects):** Phases 00–05  
**Coming soon (brief teasers):** Phases 06–09

```
Phase 00  Linux, Bash, Python, Git          →  server health reporter
Phase 01  Docker, K8s, Terraform, CI        →  microservice pipeline
Phase 02  Observability, GitOps, SRE        →  metrics + logs + traces
Phase 03  AI in daily DevOps work           →  incident response bot
Phase 04  Run LLMs as infrastructure        →  inference platform + RAG
Phase 05  DevSecOps & supply chain          →  secure pipelines + policy
Phase 06  Platform engineering              →  golden paths / IDP sketch
Phase 07  AIOps & self-healing              →  detect → act with guardrails
Phase 08  Agentic infrastructure            →  tool-using ops agents
Phase 09  The Autonomous Engineer           →  intent-driven AI ops platform
```

**Time:** ~12–18 months part-time if you go linear  
**Format:** Read the phase guide → use cheatsheets → build the capstone → open a progress issue

---

## Start here

| You are... | Start at |
|---|---|
| New to Linux / servers | [Phase 00 — The Foundation](./Phase00_Foundation/README.md) |
| Know Linux, learning cloud & containers | [Phase 01 — Core DevOps](./Phase01_Core_DevOps/README.md) |
| Working DevOps, want observability & GitOps | [Phase 02 — Cloud Native Operations](./Phase02_Cloud_Native_Operations/README.md) |
| Comfortable in prod, adding AI to your workflow | [Phase 03 — AI-Augmented DevOps](./Phase03_AI_Augmented_DevOps/README.md) |
| Ready to **run** LLM workloads (not just call APIs) | [Phase 04 — MLOps & LLMOps](./Phase04_MLOps_LLMOps/README.md) |
| Shipping to prod, need security & supply-chain depth | [Phase 05 — DevSecOps](./Phase05_DevSecOps/README.md) |
| Building internal platforms / golden paths | [Phase 06 — Platform Engineering](./Phase06_Platform_Engineering/README.md) |
| Want infrastructure that remediates itself | [Phase 07 — AIOps](./Phase07_AIOps_Autonomous_Operations/README.md) |
| Building tool-using agents for ops | [Phase 08 — Agentic Infrastructure](./Phase08_Agentic_Infrastructure/README.md) |
| Designing intent-driven AI ops platforms | [Phase 09 — Autonomous Engineer](./Phase09_The_Autonomous_Engineer/README.md) |

Each phase has a **self-check**. If you pass it, skip ahead.

---

## Phases at a glance

| Phase | Focus | Capstone | Status |
|---|---|---|---|
| [00 — Foundation](./Phase00_Foundation/README.md) | Linux, Bash, Python, Git, networking, SSH | [Server health reporter](./Phase00_Foundation/projects/server-health-reporter/) | ✅ Available |
| [01 — Core DevOps](./Phase01_Core_DevOps/README.md) | Docker, Kubernetes, Terraform, CI/CD | [Microservice pipeline](./Phase01_Core_DevOps/projects/microservice-pipeline/) | ✅ Available |
| [02 — Cloud Native Ops](./Phase02_Cloud_Native_Operations/README.md) | Prometheus, Grafana, OTel, ArgoCD, SLOs | [Observability stack](./Phase02_Cloud_Native_Operations/projects/observability-stack/) | ✅ Available |
| [03 — AI-Augmented DevOps](./Phase03_AI_Augmented_DevOps/README.md) | Prompts, AI in CI, ChatOps | [Incident response bot](./Phase03_AI_Augmented_DevOps/projects/incident-response-bot/) | ✅ Available |
| [04 — MLOps & LLMOps](./Phase04_MLOps_LLMOps/README.md) | vLLM, RAG, GPUs, model monitoring | [LLM inference platform](./Phase04_MLOps_LLMOps/projects/llm-inference-platform/) | ✅ Available |
| [05 — DevSecOps](./Phase05_DevSecOps/README.md) | SCA, image scan, SBOM, signing, policy-as-code | [Secure pipeline lab](./Phase05_DevSecOps/projects/secure-pipeline-lab/) | ✅ Available |
| [06 — Platform Engineering](./Phase06_Platform_Engineering/README.md) | Golden paths, IDPs, paved roads, multi-tenancy | Golden-path template (planned) | 🔜 Teaser |
| [07 — AIOps](./Phase07_AIOps_Autonomous_Operations/README.md) | Anomaly detection, self-healing, predictive scale | Self-healing demo (planned) | 🔜 Teaser |
| [08 — Agentic Infrastructure](./Phase08_Agentic_Infrastructure/README.md) | Tool-using agents, approvals, evals | Gated ops agent (planned) | 🔜 Teaser |
| [09 — Autonomous Engineer](./Phase09_The_Autonomous_Engineer/README.md) | Intent → infra, feedback loops | Intent ops platform (planned) | 🔜 Teaser |

---

## The arc (why ten phases)

```
00–01   Build & ship          foundations + daily toolkit
02      Operate               see and measure production
03–04   Add AI                use AI, then run AI workloads
05–06   Harden & productize   security + platform as a product
07–09   Autonomy              self-heal → agents → intent-driven systems
```

Phases 05–06 sit **after** you can ship and observe, and **before** you hand more authority to automation. Security and platform thinking are what keep autonomous systems from becoming expensive chaos.

---

## What's in each phase

```
PhaseXX/
├── README.md           ← learning guide + objectives + capstone spec
├── cheatsheets/        ← quick references (where applicable)
└── projects/           ← starter code for the capstone (where applicable)
```

**You get:** learning objectives, resources, a capstone with a definition of done.  
**You build:** portfolio pieces — pipelines, bots, observability stacks, LLM platforms, agents.

---

## How to use this repo

**Linear (recommended for beginners)** — Phase 00 → … → Phase 09. Open `[Phase XX] Done` when each capstone works.

**Jump in at your level** — use the table above. Self-checks at the top of each phase README.

**Reference mode** — star the repo; come back when you need a structured path for a new topic.

---

## Track your progress

```
[Phase 00] Starting — your-handle
[Phase 00] Done — your-handle
```

Use the [progress issue template](./.github/ISSUE_TEMPLATE/progress.md).

---

## Repo map

```
devops-to-ai/
├── Phase00_Foundation/
├── Phase01_Core_DevOps/
├── Phase02_Cloud_Native_Operations/
├── Phase03_AI_Augmented_DevOps/
├── Phase04_MLOps_LLMOps/
├── Phase05_DevSecOps/
├── Phase06_Platform_Engineering/
├── Phase07_AIOps_Autonomous_Operations/
├── Phase08_Agentic_Infrastructure/
├── Phase09_The_Autonomous_Engineer/
├── .github/ISSUE_TEMPLATE/
└── LICENSE
```

---

## Contributing

Issues and PRs welcome — especially capstone starters for Phases 06–09, cheatsheets, and corrections. This roadmap is opinionated; open an issue before large structural changes.

---

## License

[MIT](./LICENSE)

---

<p align="center">
  <a href="./Phase00_Foundation/README.md"><strong>Start Phase 00 →</strong></a>
  &nbsp;·&nbsp;
  <a href="./Phase05_DevSecOps/README.md">Explore Phase 05 →</a>
  &nbsp;·&nbsp;
  <a href="./Phase09_The_Autonomous_Engineer/README.md">See the destination →</a>
</p>
