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

### 3. Model serving with vLLM

Serving is the heart of LLMOps. Users don't care about your weights — they care that `/v1/chat/completions` responds fast and correctly. **vLLM** is currently one of the best open-source inference engines for high-throughput LLM serving.

**Why vLLM specifically:**
- OpenAI-compatible HTTP API (drop-in for many clients)
- PagedAttention — efficient KV-cache memory management
- Continuous batching — packs concurrent requests for higher GPU utilisation
- Supports popular open models (Llama, Mistral, Qwen, etc.)

**How a typical request flows:**

```
Client
  → POST /v1/chat/completions
  → API gateway (auth, rate limit, routing)
  → vLLM engine (tokenize → prefill → decode loop → stream tokens)
  → streamed SSE or JSON response
```

**What to cover:**

- Prefill vs decode — why time-to-first-token (TTFT) and inter-token latency are different metrics
- Continuous batching vs static batching
- Context length limits and what happens when you exceed them
- Tensor parallelism — splitting a model across multiple GPUs
- Choosing a model size for your GPU VRAM (rule of thumb: ~2 bytes/param for FP16, less when quantised)
- Alternative engines you'll see in the wild: Hugging Face TGI, NVIDIA Triton + TensorRT-LLM, Ollama (local/dev), llama.cpp

**Example — run vLLM locally (GPU required):**

```bash
# Serve an OpenAI-compatible API on :8000
docker run --gpus all \
  -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model mistralai/Mistral-7B-Instruct-v0.3 \
  --max-model-len 8192
```

**Example — call it like OpenAI:**

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistralai/Mistral-7B-Instruct-v0.3",
    "messages": [{"role": "user", "content": "Explain continuous batching in one paragraph."}],
    "max_tokens": 200
  }'
```

**Recommended resources:**
- [vLLM documentation](https://docs.vllm.ai/en/latest/)
- [PagedAttention paper](https://arxiv.org/abs/2309.06180) — optional depth, useful interview signal
- [Hugging Face Text Generation Inference](https://huggingface.co/docs/text-generation-inference)

---

### 4. Vector databases and embeddings

LLMs don't know your private docs. **RAG (Retrieval-Augmented Generation)** fixes that by retrieving relevant chunks from a knowledge base and stuffing them into the prompt before generation.

**The RAG pipeline:**

```
Documents
  → chunk (size + overlap matter)
  → embed (embedding model → vectors)
  → store in vector DB
        ↓
User query
  → embed query
  → similarity search (top-k)
  → build prompt: system + retrieved context + question
  → LLM generates grounded answer
```

**What to cover:**

- Embeddings — dense vectors that capture semantic similarity
- Chunking strategies — fixed size, recursive, by heading; why bad chunking kills RAG quality
- Similarity metrics — cosine, dot product, L2
- Vector DB options: **Qdrant**, Weaviate, Chroma, pgvector, Pinecone
- Metadata filtering — "only search docs tagged `runbook` and `env=prod`"
- Hybrid search — sparse (BM25) + dense for better recall
- When *not* to use RAG — tiny knowledge bases that fit in the prompt, or tasks that need parametric knowledge updates (fine-tune instead)

**Anti-patterns:**
- Dumping entire PDFs as single chunks
- Re-embedding the corpus every request
- Ignoring citation / source attribution in answers
- Treating retrieval score as truth without evaluation

**Recommended resources:**
- [Qdrant documentation](https://qdrant.tech/documentation/)
- [LangChain RAG tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [pgvector](https://github.com/pgvector/pgvector) — if you already run Postgres

---

### 5. GPU provisioning and capacity planning

GPUs are expensive, scarce, and easy to waste. Platform engineers who can reason about utilisation save real money.

**What to cover:**

- GPU types you'll meet: consumer (RTX), datacenter (A10, L4, A100, H100), Apple Silicon for local-only
- VRAM as the binding constraint — model weights + KV cache + activations must fit
- Cloud options — AWS (g5/p4/p5), GCP (A100/H100), Azure NC-series, Lambda, RunPod, CoreWeave
- Kubernetes device plugins — scheduling pods onto GPU nodes (`nvidia.com/gpu`)
- Fractional GPUs / MIG (Multi-Instance GPU) — when one physical GPU serves multiple workloads
- Autoscaling inference — scale on queue depth or tokens/sec, not just CPU
- Spot / preemptible GPUs — cheaper, but you need checkpoint-friendly or restartable serving

**Capacity planning sketch:**

```
Concurrent users × avg tokens out / request
        ÷
Tokens/sec per GPU replica
        =
Replicas needed (plus headroom for spikes)
```

Always leave headroom. A GPU at 100% utilisation means queueing and exploding TTFT.

**Recommended resources:**
- [NVIDIA Kubernetes device plugin](https://github.com/NVIDIA/k8s-device-plugin)
- [Kubernetes GPU scheduling docs](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/)
- [vLLM performance tuning](https://docs.vllm.ai/en/latest/performance/)

---
