# LLMOps cheatsheet

Quick reference for running LLM workloads as infrastructure.

---

## Core vocabulary

| Term | Meaning |
|---|---|
| Prefill | Process the prompt; dominates TTFT |
| Decode | Generate tokens one-by-one after prefill |
| TTFT | Time to first token |
| TPS | Tokens per second (throughput) |
| KV cache | Cached attention keys/values — VRAM hungry |
| Continuous batching | Dynamically pack concurrent decode work |
| Quantisation | Lower precision weights (INT8/INT4) to save VRAM |
| RAG | Retrieve docs → stuff context → generate |
| Canary | Send a slice of traffic to a new model version |

---

## OpenAI-compatible chat call

```bash
curl http://GATEWAY/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "MODEL_ID",
    "messages": [
      {"role": "system", "content": "Be concise."},
      {"role": "user", "content": "Explain TTFT"}
    ],
    "max_tokens": 256
  }'
```

Canary override:

```bash
-H "X-Model-Version: canary"
```

---

## Metrics that matter

```
Requests/sec          traffic
Error rate            reliability
TTFT p50/p99          perceived latency
E2E latency p99       SLO
Tokens/sec            capacity + cost
GPU util / VRAM       saturation
Queue depth           backpressure
Rate-limit 429s       client abuse / undersized quotas
```

PromQL starters (gateway):

```promql
sum(rate(llm_gateway_requests_total[5m]))

sum(rate(llm_gateway_requests_total{status=~"5.."}[5m]))
  / clamp_min(sum(rate(llm_gateway_requests_total[5m])), 1e-9)

histogram_quantile(0.99, sum(rate(llm_gateway_request_duration_seconds_bucket[5m])) by (le))

sum(rate(llm_gateway_tokens_total[5m])) by (type)
```

---

## VRAM rule of thumb

```
FP16 weights ≈ 2 bytes × parameter count
7B  FP16  ≈ 14 GB (+ KV cache + activations)
7B  INT4  ≈ ~4–5 GB weights (quality tradeoff)
```

Always leave headroom for KV cache at your max context length.

---

## RAG checklist

1. Chunk with overlap (start ~300–800 chars; tune)
2. Embed once; store vectors + metadata
3. Retrieve top-k; filter by metadata when possible
4. Prompt: system rules + context + question
5. Cite sources; decline on empty retrieval
6. Re-ingest when docs change
7. Eval retrieval with a golden question set

---

## Rollout decision matrix

| Signal | Action |
|---|---|
| Canary 5xx ↑ | Roll back immediately |
| Canary p99 latency ↑ >20% | Pause promote; investigate |
| Eval score ↓ | Do not promote |
| Stable error budget healthy + eval OK | Promote; set canary % → 0 |

Rollback: `CANARY_PERCENT=0` or force `X-Model-Version: stable`.

---

## Safety red flags

- Logging raw prompts that contain secrets / PII without redaction
- Untrusted docs in the RAG index (prompt injection)
- Unlimited `max_tokens` / no per-tenant quotas
- Deploying `latest` model tags to production
- Auto-executing tool calls from model output without allowlists

---

## Useful links

- [vLLM docs](https://docs.vllm.ai/en/latest/)
- [Qdrant docs](https://qdrant.tech/documentation/)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [OTel GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
