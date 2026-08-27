# Project: LLM inference platform with RAG

> Phase 04 capstone — build this before moving to Phase 05.

An OpenAI-compatible inference gateway in front of a model server, plus a RAG service backed by Qdrant, with Prometheus metrics you can actually operate on. Works with real **vLLM** on a GPU, or with the included **mock inference** backend on a laptop.

---

## What's in this project

```
llm-inference-platform/
├── docker-compose.yml
├── .env.example
├── prompts/
│   ├── rag_system_v1.txt
│   └── gateway_system_v1.txt
├── services/
│   ├── inference-gateway/     ← auth, rate limits, routing, metrics
│   ├── rag-service/           ← chunk → embed → retrieve → generate
│   └── mock-inference/        ← CPU-friendly OpenAI-compatible stub
├── config/
│   ├── prometheus/prometheus.yml
│   └── grafana/               ← datasource + dashboard provisioning
├── k8s/                       ← optional GPU Deployment sketches
├── scripts/
│   ├── smoke_test.sh
│   ├── eval_rag.py
│   └── generate_load.sh
├── data/
│   ├── corpus/                ← sample ops docs for RAG ingest
│   └── eval/golden_set.jsonl  ← retrieval eval cases
```

---

## Quick start (CPU / mock)

```bash
# 1. Copy environment
cp .env.example .env

# 2. Start the stack
docker compose up --build

# 3. Chat completion via the gateway
curl -s http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mock-model",
    "messages": [{"role": "user", "content": "What is continuous batching?"}],
    "max_tokens": 128
  }' | jq .

# 4. RAG query (after corpus ingest — see rag-service README tasks)
curl -s http://localhost:8081/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do we roll back a bad model canary?"}' | jq .
```

Prometheus: http://localhost:9090  
Grafana: http://localhost:3000 (admin / admin)  
Qdrant UI: http://localhost:6333/dashboard  

---

## GPU path (vLLM)

If you have an NVIDIA GPU and the NVIDIA Container Toolkit installed:

1. Set `INFERENCE_URL=http://vllm:8000` in `.env`
2. Uncomment the `vllm` service in `docker-compose.yml`
3. Stop or leave `mock-inference` unused
4. Pull a model that fits your VRAM (start with a 7B instruct model)

Record TTFT and tokens/sec for three prompts in your project notes — interview gold.

---

## Your tasks

Complete the `TODO` sections marked in the service code:

### Gateway
- [ ] API key authentication
- [ ] Per-key rate limiting (429 when exceeded)
- [ ] Proxy to upstream `/v1/chat/completions`
- [ ] Canary routing via `X-Model-Version: canary`
- [ ] Prometheus metrics (`/metrics`)
- [ ] `/health` and `/ready` (ready fails if upstream is down)

### RAG service
- [ ] Corpus ingest into Qdrant
- [ ] Embedding + top-k retrieval
- [ ] Grounded generation through the gateway
- [ ] Return `answer` + `sources[]`
- [ ] Empty-retrieval fallback message

### Ops
- [ ] Confirm Grafana dashboard shows live RPS / latency / errors
- [ ] Run `scripts/smoke_test.sh` green
- [ ] Run a tiny eval with `scripts/eval_rag.py`
- [ ] Document rollback steps for canary → stable

---

## Definition of done

- [ ] Gateway returns completions through the configured upstream
- [ ] RAG answers cite at least one source from `data/corpus/`
- [ ] Excess traffic gets HTTP 429
- [ ] Upstream down → gateway returns 502/503, process stays up
- [ ] Metrics visible in Prometheus/Grafana
- [ ] Prompts versioned under `prompts/`
- [ ] README notes whether you used mock or vLLM

---

## Sharing your work

Open a `[Phase 04] Done` issue on the devops-to-ai repo. Include:
- Dashboard screenshot
- One RAG answer with citations
- Mock vs vLLM note
