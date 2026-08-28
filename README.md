# devops-to-ai

> A project-driven roadmap from Linux basics to AI-native infrastructure — with capstone projects you can demo in interviews, not just talk about.

Most learning paths are tool lists. This one is a **career arc**: seven phases that build on each other, each ending in something real you ship.

```
Phase 00  Linux, Bash, Python, Git     →  server health reporter
Phase 01  Docker, K8s, Terraform, CI   →  full deployment pipeline
Phase 02  Observability, GitOps, SRE   →  metrics + logs + traces stack
Phase 03  AI in daily DevOps work      →  incident response bot
Phase 04  Run LLMs as infrastructure   →  inference platform + RAG
Phase 05  Self-healing ops             →  (coming soon)
Phase 06  Autonomous engineer          →  (coming soon)
```

**Time:** ~9–14 months part-time, linear path  
**Format:** Read the phase guide → use cheatsheets → build the capstone → open a progress issue

---

## Start here

| You are... | Start at |
|---|---|
| New to Linux / servers | [Phase 00 — The Foundation](./Phase00_Foundation/README.md) |
| Know Linux, learning cloud & containers | [Phase 01 — Core DevOps](./Phase01_Core_DevOps/README.md) |
| Working DevOps engineer, want observability & GitOps | [Phase 02 — Cloud Native Operations](./Phase02_Cloud_Native_Operations/README.md) |
| Comfortable in prod, adding AI to your workflow | [Phase 03 — AI-Augmented DevOps](./Phase03_AI_Augmented_DevOps/README.md) |
| Ready to **run** LLM workloads (not just call APIs) | [Phase 04 — MLOps & LLMOps](./Phase04_MLOps_LLMOps/README.md) |

Each phase has a **self-check** at the top. If you pass it, skip ahead.

---

## Phases at a glance

| Phase | Focus | Capstone project | Status |
|---|---|---|---|
| [00 — Foundation](./Phase00_Foundation/README.md) | Linux, Bash, Python, Git, networking, SSH | [Server health reporter](./Phase00_Foundation/projects/server-health-reporter/) | ✅ Available |
| [01 — Core DevOps](./Phase01_Core_DevOps/README.md) | Docker, Kubernetes, Terraform, CI/CD | Full CI/CD pipeline for a microservice | ✅ Available |
| [02 — Cloud Native Ops](./Phase02_Cloud_Native_Operations/README.md) | Prometheus, Grafana, OTel, ArgoCD, SLOs | [Observability stack](./Phase02_Cloud_Native_Operations/projects/observability-stack/) | ✅ Available |
| [03 — AI-Augmented DevOps](./Phase03_AI_Augmented_DevOps/README.md) | Prompt engineering, AI in CI, ChatOps | [Incident response bot](./Phase03_AI_Augmented_DevOps/projects/incident-response-bot/) | ✅ Available |
| [04 — MLOps & LLMOps](./Phase04_MLOps_LLMOps/README.md) | vLLM, RAG, GPUs, model monitoring | [LLM inference platform](./Phase04_MLOps_LLMOps/projects/llm-inference-platform/) | ✅ Available |
| 05 — AIOps & Autonomous Ops | Self-healing, anomaly detection, predictive scale | TBD | 🔜 Coming soon |
| 06 — The Autonomous Engineer | AI agents as operators, intent-driven infra | TBD | 🔜 Coming soon |

---

## What's in each phase

Every available phase follows the same shape:

```
PhaseXX/
├── README.md           ← learning guide + objectives + capstone spec
├── cheatsheets/        ← quick references (where applicable)
└── projects/           ← starter code for the capstone (where applicable)
```

**You get:**
- Clear learning objectives and a "ready for next phase" checklist
- Curated resources (books, docs, tools)
- Capstone projects with starter code, TODOs, and a definition of done

**You build:**
- Portfolio pieces — bots, pipelines, observability stacks, LLM platforms
- Muscle memory for the terminal, Git, and automation

---

## How to use this repo

**Linear (recommended for beginners)**  
Start at Phase 00. Finish the capstone. Open a `[Phase 00] Done` issue. Move to Phase 01. Repeat.

**Jump in at your level**  
Use the table above. Each phase README starts with a self-check — pass it, skip the phase.

**Reference mode**  
Star the repo. Come back to a specific phase or cheatsheet when you need structure for a new topic.

---

## Track your progress

Open a GitHub issue when you start and finish a phase:

```
[Phase 00] Starting — your-handle
[Phase 00] Done — your-handle
```

Use the [progress issue template](./.github/ISSUE_TEMPLATE/progress.md). When you mark Done, link your capstone repo or a screenshot — it helps others at the same stage find you.

---

## Repo map

```
devops-to-ai/
├── Phase00_Foundation/          Linux, Bash, Git + server health reporter
├── Phase01_Core_DevOps/         Docker, K8s, Terraform, CI/CD
├── Phase02_Cloud_Native_Operations/   Observability + GitOps stack project
├── Phase03_AI_Augmented_DevOps/       AI incident bot + prompt cheatsheets
├── Phase04_MLOps_LLMOps/              LLM gateway, RAG, Grafana dashboards
├── .github/ISSUE_TEMPLATE/      Progress tracking template
└── LICENSE                      MIT
```

---

## Contributing

Issues and PRs welcome — especially capstone improvements, new cheatsheets, and corrections.

This roadmap is opinionated by design. Open an issue before large structural changes.

---

## License

[MIT](./LICENSE)

---

<p align="center">
  <a href="./Phase00_Foundation/README.md"><strong>Start Phase 00 →</strong></a>
  &nbsp;·&nbsp;
  <a href="./Phase04_MLOps_LLMOps/README.md">Jump to Phase 04 →</a>
</p>
