# Phase 04 — MLOps & LLMOps

> **"Using AI in your workflow is Phase 03. Running AI as infrastructure is Phase 04."**
>
> Up to now you've *called* models. Here you *run* them — gateways, RAG, metrics, rollouts. You don't need a GPU on day one. The capstone has a mock backend so you can learn the platform shape on a laptop.

---

## Who this is for

| You are... | Do this |
|---|---|
| Finished Phase 03 (or comfortable calling LLM APIs from Python) | Work the topics, then the capstone |
| Junior DevOps — curious about "how ChatGPT-like APIs are hosted" | Start **Path A (mock)**; ignore GPUs until it clicks |
| Already run vLLM + RAG in production | Take the [self-check](#self-check--can-you-skip) — skip to Phase 05 if you pass |

**Time:** 6–8 weeks part-time  
**Goal:** Operate an OpenAI-compatible inference path with a gateway, optional RAG, and dashboards you trust.

---

## Start here — four steps

```
1. Self-check     →  Already running LLM platforms? Maybe skip to Phase 05
2. Learn          →  Mental model → serving → RAG → metrics → rollouts
3. Practice       →  docker compose up (mock) → smoke test → Grafana
4. Capstone       →  Gateway + RAG + canary notes (GPU/vLLM is stretch)
```

**You do not need a GPU to finish Phase 04.** Path A uses `mock-inference`. Path B swaps in vLLM when you have hardware.

**Cheatsheets:**

| Topic | Cheatsheet |
|---|---|
| LLMOps vocabulary & metrics | [cheatsheets/llmops.md](./cheatsheets/llmops.md) |
| vLLM / serving knobs | [cheatsheets/vllm-serving.md](./cheatsheets/vllm-serving.md) |
| RAG & vector DBs | [cheatsheets/rag-vector-db.md](./cheatsheets/rag-vector-db.md) |

**What you need:**

| Thing | Why | Notes |
|---|---|---|
| Docker Compose | Run the whole stack | Same as Phase 02 |
| ~4–8 GB free RAM | Qdrant + services | Fine on most laptops |
| GPU + NVIDIA toolkit (optional) | Real vLLM | Path B only |
| Phase 03 comfort | APIs, prompts as code | Helps, not a hard gate |

---

## Self-check — can you skip?

If you can do **all** of these without looking things up, skip to [Phase 05](../Phase05_DevSecOps/README.md):

- Explain training vs fine-tuning vs inference — and what platform teams usually own
- Put an OpenAI-compatible API behind auth + rate limits
- Explain RAG vs fine-tuning in plain language
- Name five metrics for an LLM gateway dashboard (including TTFT or tokens/sec)
- Sketch canary vs rollback for a new model version
- Say why prompts and model tags must be versioned (no `latest` in prod)

Otherwise stay here. Phase 05 assumes you can treat AI workloads like any other service.

---

## Learning objectives

By the end of Phase 04, answer **yes** to all of these:

- [ ] Explain training / fine-tuning / inference and the platform ownership line
- [ ] Serve (or mock-serve) chat completions behind a gateway
- [ ] Explain what a vector DB does and when RAG is the right tool
- [ ] Reason about GPU/VRAM or honestly use the mock path and still talk capacity
- [ ] Monitor latency, errors, tokens (or stand-ins), and gateway health
- [ ] Describe blue/green, canary, or shadow for a generative API
- [ ] Version prompts + model IDs like application config

---

## Topics

Work in order. Don't jump to vLLM before the gateway mental model is solid.

### 1. Mental model — MLOps vs LLMOps

Classic MLOps: train → validate → deploy a model that outputs scores.  
LLMOps adds: prompts as code, retrieval, streaming tokens, and cost that grows with every request.

```
App / bot
   → Gateway (auth, limits, routing, metrics)
   → Inference (vLLM or mock)
   → (optional) RAG: embed → search → stuff context → generate
```

**You usually own:** serving, gateways, GPUs/capacity, observability, rollouts, secrets.  
**You usually don't own (yet):** training from scratch, research eval rubrics.

Interview line: "I don't need to train Llama — I need to run it reliably."

### 2. Models are artifacts

Treat weights like container images: versioned, immutable, promoted (`staging` → `canary` → `prod`). Never deploy `latest` to production. Quantisation (FP16 / INT8 / INT4) trades VRAM and quality — know the tradeoff exists even if you stay on mock.

### 3. Serving — OpenAI-compatible APIs

Users care about `POST /v1/chat/completions`, not your Docker tag.

- **Prefill** = process the prompt (drives time-to-first-token)  
- **Decode** = emit tokens (drives tokens/sec)  
- **vLLM** = popular high-throughput engine (GPU). **Mock** = enough to learn the platform on CPU.

Gateway sits in front: API keys, rate limits, canary header, Prometheus metrics, honest `/ready`.

→ [vLLM cheatsheet](./cheatsheets/vllm-serving.md)

### 4. RAG — when the model shouldn't "just know"

Private runbooks don't live in base model weights. RAG: chunk docs → embed → store in Qdrant → retrieve top-k → generate with citations.

Bad chunking = bad answers. Empty retrieval should say "I don't know," not invent a kubectl command.

→ [RAG cheatsheet](./cheatsheets/rag-vector-db.md)

### 5. Capacity (even without a GPU)

VRAM is the binding constraint when you go real. Rule of thumb: leave headroom — 100% GPU util often means exploding TTFT. On Path A, still practice the *questions*: concurrency, tokens out, replicas, cost.

→ [gpu-ops-notes](./projects/llm-inference-platform/docs/gpu-ops-notes.md)

### 6. Monitoring LLM services

HTTP 200 that returns nonsense is still a failure. Track at least: RPS, errors, latency/TTFT, tokens/sec (or mock usage), queue/upstream health. Alert on user pain, not only process up.

→ [LLMOps cheatsheet](./cheatsheets/llmops.md)

### 7. Rollouts

New model ≠ new container tag with identical behaviour. Prefer canary or shadow; roll back on latency, errors, *or* eval score drop — not vibes from three test prompts.

### 8. Prompts as code + safety

Prompts live in Git. Golden eval sets catch silent quality regressions. Watch prompt injection via retrieved docs (Phase 03 lesson still applies).

---

## Capstone project

### LLM inference platform with RAG

**Starter:** [projects/llm-inference-platform/](./projects/llm-inference-platform/)

| Path | Needs | Outcome |
|---|---|---|
| **A — Mock (start here)** | Docker only | Gateway + RAG + Grafana on a laptop |
| **B — GPU / vLLM** | NVIDIA GPU + toolkit | Same stack, real model server |

**Already wired for Path A:** mock inference, gateway (auth, RPM limits, canary routing, metrics), RAG + Qdrant, Prometheus/Grafana, smoke + eval scripts.

**Your job:** run it, break it on purpose, prove the done checklist, document mock vs vLLM, practice canary/rollback notes. Stretch: real embeddings, OTel, k8s GPU manifests.

Full walkthrough → [projects/llm-inference-platform/README.md](./projects/llm-inference-platform/README.md)

---

## Ready for Phase 05?

Don't move on until you can do these **without googling**:

1. Prefill vs decode; why TTFT and tokens/sec both matter  
2. Curl a completion through a gateway you understand  
3. RAG vs fine-tuning in one plain paragraph  
4. Canary + rollback criteria for a model change  
5. Five dashboard metrics for an LLM API  
6. Why prompt/model versions belong in Git  

Phase 05 (DevSecOps) assumes AI workloads are just services you can secure and ship.

---

## Resources

| Resource | What it's for |
|---|---|
| [vLLM docs](https://docs.vllm.ai/en/latest/) | Real serving |
| [Qdrant docs](https://qdrant.tech/documentation/) | Vectors |
| [OTel GenAI conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) | Tracing shape |
| [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) | Safety |
| Repo cheatsheets | Day-to-day lookup |

---

## Track your progress

```
[Phase 04] Starting — your-handle
[Phase 04] Done — your-handle
```

When Done, share: Grafana screenshot, one RAG answer with citations, mock vs vLLM note.

---

*← [Phase 03 — AI-Augmented DevOps](../Phase03_AI_Augmented_DevOps/README.md) | [Phase 05 — DevSecOps →](../Phase05_DevSecOps/README.md)*
