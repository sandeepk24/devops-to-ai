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

If you can say yes to all seven, you're ready for Phase 05 (DevSecOps) — and the rest of the autonomy arc.

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

### 6. Model monitoring and LLM observability

Prometheus golden signals still apply — but LLMs need extra dimensions. A 200 OK that returns nonsense is still a failure from the user's perspective.

**Metrics you must track:**

| Metric | Why it matters |
|---|---|
| Request rate | Traffic / capacity planning |
| Error rate (4xx/5xx + model errors) | Reliability |
| Time to first token (TTFT) | Perceived latency |
| Tokens/sec (throughput) | Cost and capacity |
| End-to-end latency | SLO compliance |
| GPU utilisation / VRAM | Waste and saturation |
| Queue depth | Backpressure early warning |
| Cost per 1k tokens (est.) | Budget control |

**Quality signals (harder, still required):**
- Retrieval hit-rate / relevance scores for RAG
- Refusal rate and safety filter triggers
- User feedback (👍/👎) as a weak label
- Offline eval suites run on every model/prompt change

**What to cover:**

- Exporting metrics from vLLM / gateway (Prometheus `/metrics`)
- Tracing a request across gateway → retriever → LLM with OpenTelemetry
- Logging prompts and completions safely — PII redaction, retention limits, access control
- Alerting on TTFT and queue depth, not just HTTP errors
- Distinguishing infrastructure failure from model quality regression

**Dashboard layout that actually helps:**

```
┌──────────────────────┬──────────────────────┐
│  Requests / sec      │  Error rate          │
├──────────────────────┼──────────────────────┤
│  TTFT p50 / p99      │  Tokens / sec        │
├──────────────────────┼──────────────────────┤
│  GPU util + VRAM     │  Queue depth         │
└──────────────────────┴──────────────────────┘
```

**Recommended resources:**
- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [vLLM metrics](https://docs.vllm.ai/en/latest/serving/metrics.html)
- [LangSmith](https://docs.smith.langchain.com/) / [Phoenix (Arize)](https://docs.arize.com/phoenix) — LLM tracing & eval UIs

---

### 7. LLM deployment patterns

Shipping a new model version is not the same as shipping a new container image. Behaviour can change subtly even when the API shape stays identical.

**Patterns to know:**

```
Blue / green     Two full stacks; flip traffic at the gateway
Canary           Send 5–10% of traffic to the new model; compare quality + latency
Shadow           New model sees live traffic but responses are discarded (compare offline)
A/B              Explicit experiment with user assignment and metrics
```

**What to cover:**

- Gateway-level routing by `model` name or header (`X-Model-Version`)
- Keeping prompt templates versioned alongside model versions
- Rollback criteria — not just error rate: TTFT regression, elevated refusals, eval score drop
- Multi-model serving — one gateway, many backends (cheap model for classification, large model for reasoning)
- Feature flags for prompts — change behaviour without redeploying the inference pod

**Rule of thumb:** Never swap production model weights without a canary or shadow period. "It looked fine on three test prompts" is not an evaluation strategy.

---

### 8. Evaluation, prompts as code, and safety

If you can't measure quality, you can't safely change anything.

**What to cover:**

- Offline evaluation sets — golden questions with expected behaviours
- LLM-as-judge — useful but biased; always sample-check with humans
- Prompt versioning — store prompts in Git, not Slack; tag releases
- Guardrails — input/output filters, PII scrubbing, tool-use allowlists
- Prompt injection & data exfiltration — especially when RAG indexes untrusted docs
- Cost controls — max tokens, per-tenant quotas, cheaper model fallbacks

**Prompts are code:**

```
prompts/
  system/v3_ops_assistant.txt
  rag/v2_grounded_answer.txt
  eval/golden_set.jsonl
```

Review them in PRs. Diff them. Roll them back like application config.

**Recommended resources:**
- [HELM (Stanford)](https://crfm.stanford.edu/helm/) — holistic evaluation of language models
- [OpenAI evals](https://github.com/openai/evals)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

---

## Capstone project

### LLM inference platform with RAG

Build a production-shaped LLM platform you can demo: an OpenAI-compatible gateway in front of a model server, a RAG service backed by a vector database, and monitoring for the signals that matter. Interviewers care about this project because it proves you can *operate* AI infrastructure — not just call ChatGPT.

---

**Architecture:**

```
Client / curl / app
        ↓
  Inference Gateway (auth, rate limit, routing, metrics)
        ↓                    ↓
   vLLM (or mock)      RAG Service → Qdrant (vectors)
        ↓                    ↓
   completions          grounded answers + citations
        ↓
  Prometheus + Grafana dashboards
```

Starter code lives in `projects/llm-inference-platform/`. Use a real GPU + vLLM when you have one; otherwise run the included **mock inference backend** so you can complete every other part of the project on a laptop.

---

**Part 1 — Inference gateway**

Build (or complete) the FastAPI gateway in `services/inference-gateway/`:

- [ ] Expose `POST /v1/chat/completions` (OpenAI-compatible request/response shape)
- [ ] Proxy to an upstream inference URL (`INFERENCE_URL`)
- [ ] Add a simple API key check (`Authorization: Bearer ...`)
- [ ] Enforce a per-key rate limit (requests / minute)
- [ ] Emit Prometheus metrics: request count, latency histogram, token counts (if present), errors
- [ ] Support a `X-Model-Version` header for canary routing to a secondary upstream

---

**Part 2 — Model serving**

- [ ] Document how to run vLLM with a small instruct model (or the mock server for CPU-only)
- [ ] Verify `curl` against the gateway returns a completion
- [ ] Record baseline TTFT and tokens/sec for three representative prompts
- [ ] Add a `/health` and `/ready` endpoint on the gateway that fails when upstream is down

---

**Part 3 — RAG service**

Build the RAG service in `services/rag-service/`:

- [ ] Ingest a small corpus of ops docs (runbooks / README snippets) into Qdrant
- [ ] Chunk + embed documents (sentence-transformers or an embedding API)
- [ ] `POST /v1/rag/query` — retrieve top-k chunks, call the gateway, return answer + sources
- [ ] Version the RAG system prompt under `prompts/`
- [ ] Handle empty retrieval gracefully ("I don't have enough context…")

---

**Part 4 — Observability**

- [ ] Docker Compose (or k8s) wiring for Prometheus + Grafana
- [ ] Dashboard panels for: RPS, error rate, latency p99, (optional) GPU util
- [ ] Alert rule stubs: high error rate, high p99 latency, upstream unhealthy
- [ ] Structured JSON logs for every gateway request (redact auth headers)

---

**Part 5 — Rollout practice**

- [ ] Run two upstreams (`stable` + `canary`) behind the gateway
- [ ] Send ~10% of traffic to canary via header or percentage split
- [ ] Compare latency and a tiny offline eval set before promoting canary
- [ ] Document the rollback steps in the project README

---

**Definition of done:**

- [ ] `curl` to the gateway returns a chat completion through the configured upstream
- [ ] RAG query returns an answer that cites at least one retrieved source
- [ ] Grafana (or Prometheus UI) shows live request metrics from the gateway
- [ ] Rate limiting rejects excess requests with HTTP 429
- [ ] Upstream failure surfaces as gateway 502/503 without crashing the process
- [ ] Prompts live in `prompts/` as version-controlled text files
- [ ] Project `README.md` explains CPU-only (mock) and GPU (vLLM) paths

**Stretch goals:**
- Add OpenTelemetry traces spanning gateway → RAG → inference
- Shadow traffic to canary and log output diffs without serving them
- Per-tenant quotas and a simple cost estimator (tokens × price)
- Kubernetes manifests with a GPU node selector for the vLLM Deployment

---

## How to know you're ready for Phase 05

Do not move on until you can do all of the following:

- Explain prefill vs decode and why TTFT and tokens/sec are both required metrics
- Serve (or mock-serve) an OpenAI-compatible chat API and put a gateway in front of it
- Describe when to use RAG vs fine-tuning in plain language
- Sketch how you would canary a new model version and what would make you roll back
- Name at least five metrics you would put on an LLM platform dashboard
- Explain why prompts and model artifacts must be versioned like application code
- Reason about GPU VRAM as a capacity constraint (even if you only used the mock backend)

Phase 05 (DevSecOps) assumes you can run services — including AI workloads — as real deployable systems. If the gateway/RAG stack still feels magical, stay here longer.

---

## Resources summary

| Resource | Type | Cost | Link |
|---|---|---|---|
| vLLM docs | Docs | Free | [docs.vllm.ai](https://docs.vllm.ai/en/latest/) |
| Hugging Face Hub | Docs | Free | [huggingface.co/docs/hub](https://huggingface.co/docs/hub/index) |
| MLflow Model Registry | Docs | Free | [mlflow.org](https://mlflow.org/docs/latest/model-registry.html) |
| Qdrant docs | Docs | Free | [qdrant.tech/documentation](https://qdrant.tech/documentation/) |
| LangChain RAG tutorial | Tutorial | Free | [python.langchain.com](https://python.langchain.com/docs/tutorials/rag/) |
| NVIDIA k8s device plugin | Docs | Free | [github.com/NVIDIA/k8s-device-plugin](https://github.com/NVIDIA/k8s-device-plugin) |
| OTel GenAI conventions | Spec | Free | [opentelemetry.io](https://opentelemetry.io/docs/specs/semconv/gen-ai/) |
| OWASP LLM Top 10 | Guide | Free | [owasp.org](https://owasp.org/www-project-top-10-for-large-language-model-applications/) |
| HELM evaluation | Research | Free | [crfm.stanford.edu/helm](https://crfm.stanford.edu/helm/) |
| PagedAttention paper | Paper | Free | [arxiv.org/abs/2309.06180](https://arxiv.org/abs/2309.06180) |

---

## Community & tracking

Open an issue with `[Phase 04] Starting` when you begin and `[Phase 04] Done` when you complete the capstone. When you post Done, share:
- A screenshot of your Grafana (or Prometheus) LLM dashboard
- A sample RAG answer with citations
- Whether you ran real vLLM or the mock backend
- One capacity or cost lesson that surprised you

---

*← [Phase 03 — AI-Augmented DevOps](../Phase03_AI_Augmented_DevOps/README.md) | [Phase 05 — DevSecOps →](../Phase05_DevSecOps/README.md)*
