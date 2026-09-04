# Capstone: LLM inference platform with RAG

> **Phase 04 project** — finish this before [Phase 05](../../../Phase05_DevSecOps/README.md).  
> Phase guide: [Phase 04 README](../../README.md)

You're going to run an OpenAI-compatible API *you* control: gateway in front, model (or mock) behind, optional RAG over ops docs, and Grafana so you can see load. That's the LLMOps loop — not fine-tuning Llama from scratch.

---

## Paths

| Path | Needs | What you prove |
|---|---|---|
| **A — Mock (start here)** | Docker Compose | Full platform shape on a laptop |
| **B — vLLM** | NVIDIA GPU + Container Toolkit | Same gateway/RAG against a real engine |

**Do Path A completely.** Add Path B if you have hardware and time.

---

## What's in this folder

```
llm-inference-platform/
├── docker-compose.yml
├── .env.example
├── services/
│   ├── mock-inference/      ← CPU stub (OpenAI-compatible)
│   ├── inference-gateway/   ← auth, rate limits, canary, metrics
│   └── rag-service/         ← ingest → retrieve → generate
├── config/                  ← Prometheus + Grafana
├── prompts/                 ← versioned system prompts
├── data/corpus/             ← sample ops docs
├── data/eval/               ← golden retrieval questions
├── scripts/                 ← smoke_test, eval_rag, generate_load
├── k8s/                     ← optional GPU sketches
└── docs/gpu-ops-notes.md
```

---

## Path A — first win (~15 minutes)

```bash
cd Phase04_MLOps_LLMOps/projects/llm-inference-platform

cp .env.example .env
docker compose up --build -d

# Wait until healthy, then:
./scripts/smoke_test.sh
```

Manual checks:

```bash
# Chat via gateway
curl -s http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer dev-key" \
  -H "Content-Type: application/json" \
  -d '{"model":"mock-model","messages":[{"role":"user","content":"What is TTFT?"}],"max_tokens":64}' | jq .

# Ingest corpus then ask RAG
curl -s -X POST http://localhost:8081/v1/rag/ingest | jq .
curl -s http://localhost:8081/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question":"How do we roll back a bad model canary?"}' | jq .
```

**UIs:** Grafana http://localhost:3000 (admin/admin) · Prometheus http://localhost:9090 · Qdrant http://localhost:6333/dashboard

Populate panels: `./scripts/generate_load.sh`

---

## What already works (Path A)

You should **not** rewrite these from scratch on day one — run them, read them, then harden:

- [x] Mock OpenAI-compatible inference
- [x] Gateway: Bearer auth, RPM limits → 429, proxy, canary header/`CANARY_PERCENT`, `/metrics`, `/ready`
- [x] RAG: ingest markdown corpus, retrieve, call gateway, return `answer` + `sources`
- [x] Prometheus scrape + Grafana dashboard JSON
- [x] `smoke_test.sh` and `eval_rag.py`

---

## Your tasks (level up)

### Understand & operate
- [ ] Read `services/inference-gateway/main.py` — know how 401/429/502 happen
- [ ] Read `services/rag-service/main.py` — know chunk → embed → search → generate
- [ ] Break upstream (`docker compose stop mock-inference`) and confirm gateway stays up with 502/503
- [ ] Lower `RATE_LIMIT_RPM` in `.env` and prove 429s
- [ ] Run `python scripts/eval_rag.py` and note pass/fail

### Document rollouts
- [ ] Send a request with `X-Model-Version: canary` and explain what the gateway does
- [ ] Write 5–10 lines in your fork README: when you'd roll back a canary (latency, errors, eval drop)
- [ ] Note whether you used **mock** or **vLLM**

### Stretch
- [ ] Path B: uncomment `vllm` in Compose, point `INFERENCE_URL` at it, record TTFT for 3 prompts
- [ ] Swap hash embeddings for `sentence-transformers` (see TODO in rag-service)
- [ ] Add OTel traces gateway → RAG → inference
- [ ] Apply/adapt `k8s/inference.yaml` on a GPU node

---

## Path B — GPU / vLLM (optional)

1. NVIDIA driver + [Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
2. Set in `.env`: `INFERENCE_URL=http://vllm:8000` (and matching canary URL if used)
3. Uncomment the `vllm` service in `docker-compose.yml`
4. Pick a model that fits VRAM (start small, e.g. 7B instruct)
5. Re-run smoke tests; keep notes on latency vs mock

If the GPU path fights you for a day, **stop and finish Path A well**. Interviewers care that you understand the gateway and RAG loop.

---

## Definition of done

- [ ] `docker compose up` healthy; `./scripts/smoke_test.sh` passes (or you documented one soft WARN)
- [ ] Chat completion through the gateway works
- [ ] RAG answer cites at least one `data/corpus/` source
- [ ] Grafana (or Prometheus) shows gateway request metrics after load
- [ ] You can explain 401 / 429 / 502 behaviour without guessing
- [ ] Prompts remain under `prompts/` in Git
- [ ] Your notes say mock vs vLLM

---

## Sharing

Open `[Phase 04] Done` on [devops-to-ai](https://github.com/sandeepk24/devops-to-ai) with a dashboard screenshot and one cited RAG answer.

→ [Phase 05 — DevSecOps](../../../Phase05_DevSecOps/README.md)
