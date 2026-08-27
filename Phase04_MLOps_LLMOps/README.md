# Phase 04 — MLOps & LLMOps

> **"Using AI in your workflow is Phase 03. Running AI as infrastructure is Phase 04."**
>
> Up to now you've treated models as APIs you call. Here you become the person who runs those APIs — GPUs, model serving, vector stores, latency SLOs, and the operational patterns that keep LLM systems healthy in production. This is where DevOps meets machine learning operations.

---

## What this phase is

MLOps is the discipline of taking machine learning models from notebooks into reliable production systems. LLMOps is the same idea applied to large language models — with harder constraints: GPU scarcity, token-level latency, prompt versioning, retrieval quality, and cost that scales with every request.

By the end of this phase you will have built a working LLM inference platform: model serving with an OpenAI-compatible API, a RAG pipeline backed by a vector database, and monitoring that tells you when quality or performance is degrading — the kind of stack AI platform teams run every day.

**Estimated time:** 6–8 weeks  
**Target audience:** Anyone who completed Phase 03 or has built production LLM integrations and wants to run the models themselves  
**Skippable if:** You've deployed vLLM (or equivalent) in production, operated a vector database for RAG, provisioned GPUs on a cloud/k8s cluster, and monitored model latency, throughput, and drift professionally

---

## Learning objectives

When you finish this phase, you should be able to answer yes to all of these:

- [ ] Can you explain the difference between training, fine-tuning, and inference — and which one DevOps/platform teams usually own?
- [ ] Can you serve an open-weights LLM with vLLM (or similar) behind an OpenAI-compatible API?
- [ ] Can you explain what a vector database does and when RAG is the right pattern vs fine-tuning?
- [ ] Can you provision GPU capacity (cloud or Kubernetes) and reason about utilisation, batching, and cost?
- [ ] Can you monitor an LLM service for latency, tokens/sec, error rate, and GPU saturation?
- [ ] Can you design a model deployment pattern (blue/green, canary, or shadow) for a generative API?
- [ ] Can you explain prompt/model versioning and why "just change the prompt in prod" is an incident waiting to happen?

If you can say yes to all seven, you're ready for Phase 05.

---

## Topics

### 1. MLOps vs LLMOps — the mental model

Before touching GPUs, get the vocabulary right. Classic MLOps grew around tabular/vision models with clear labels and offline evaluation. LLMOps inherits that foundation but adds generative-specific concerns: prompts as code, retrieval quality, token economics, and evaluation that is often subjective.

```
Classic MLOps                         LLMOps additions
─────────────                         ────────────────
Train → validate → deploy             Prompt versioning
Feature store                         RAG / context assembly
Model registry                        Embedding pipelines
Batch + online inference              Streaming token generation
Accuracy / F1 / AUC                   Latency to first token, tokens/sec
Drift on features & labels            Drift on embeddings, retrieval hit-rate, jailbreaks
```

**What platform/DevOps engineers usually own:**
- Model serving (inference servers, autoscaling, GPUs)
- Networking, auth, rate limits, and API gateways in front of models
- Observability for latency, throughput, errors, and cost
- CI/CD for model artifacts, prompts, and retrieval configs
- Secrets, isolation, and safe rollout patterns

**What data scientists / ML engineers usually own:**
- Training and fine-tuning
- Evaluation datasets and quality rubrics
- Choosing base models and prompting strategies

Your job in this phase is the left column plus the operational half of the right. You don't need to train Llama from scratch — you need to run it reliably.

**The three layers of an LLM platform:**

```
┌─────────────────────────────────────────────────────────┐
│  Application layer     Chat UIs, agents, internal tools │
├─────────────────────────────────────────────────────────┤
│  Platform layer        Gateway, RAG, auth, rate limits  │
├─────────────────────────────────────────────────────────┤
│  Inference layer       vLLM / TGI / Triton + GPUs       │
└─────────────────────────────────────────────────────────┘
```

Phase 04 lives primarily in the bottom two layers.

---

### 2. Model packaging and the model registry

Models are artifacts. Treat them like container images: versioned, immutable, and promoted through environments.

**What to cover:**

- Model formats you'll actually serve: Hugging Face weights, GGUF (llama.cpp), SafeTensors, ONNX
- Quantisation tradeoffs — FP16 vs INT8 vs INT4 (AWQ/GPTQ): memory vs quality vs latency
- Model registry concepts — MLflow Model Registry, Hugging Face Hub, cloud registries (SageMaker, Vertex, Azure ML)
- Artifact promotion: `staging` → `canary` → `production` with immutable version IDs
- Checksums and supply-chain hygiene — never `latest` for production model tags

**Mental model:**

```
Training job / download
        ↓
Model artifact (weights + config + tokenizer)
        ↓
Registry entry: name, version, stage, metadata
        ↓
Serving job pulls a specific version (not "latest")
```

**Recommended resources:**
- [Hugging Face Hub docs](https://huggingface.co/docs/hub/index)
- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)
- [SafeTensors](https://huggingface.co/docs/safetensors/index) — why it exists (safer than pickle)

---
