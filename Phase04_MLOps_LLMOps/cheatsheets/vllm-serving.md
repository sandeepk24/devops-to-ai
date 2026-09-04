# vLLM & model serving cheatsheet

**Use this when:** Path B — you have an NVIDIA GPU and want a real OpenAI-compatible server behind the Phase 04 gateway.  
**Rule of thumb:** finish the mock path first. If you're fighting drivers for a day, go back to mock and learn the gateway.

No GPU? Skip this file until you need it. The gateway speaks the same API either way.

---

## Run vLLM (Docker + GPU)

```bash
docker run --gpus all -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model mistralai/Mistral-7B-Instruct-v0.3 \
  --max-model-len 8192
```

Private models:

```bash
docker run --gpus all -p 8000:8000 \
  -e HUGGING_FACE_HUB_TOKEN=$HF_TOKEN \
  vllm/vllm-openai:latest \
  --model meta-llama/Meta-Llama-3.1-8B-Instruct
```

---

## Common server flags

| Flag | Why |
|---|---|
| `--model` | HF repo id or local path |
| `--max-model-len` | Cap context; saves KV VRAM |
| `--tensor-parallel-size N` | Shard across N GPUs |
| `--gpu-memory-utilization 0.90` | Leave headroom vs OOM |
| `--quantization awq` / `gptq` | Load quantised checkpoints |
| `--served-model-name NAME` | Stable API model id |

Check the current flag list in the [vLLM CLI docs](https://docs.vllm.ai/en/latest/) — names evolve.

---

## Health & models

```bash
curl -s localhost:8000/health
curl -s localhost:8000/v1/models | jq .
```

---

## Latency debugging

```
High TTFT, OK decode     → prefill heavy / long prompts / queueing
OK TTFT, slow tokens     → decode bound / low batch efficiency
Both bad                 → GPU saturation, thermal throttle, wrong GPU type
Sporadic 502s            → OOM kills, probe failures, network to GPU node
```

Collect: `nvidia-smi`, gateway histograms, upstream logs, queue depth.

---

## Kubernetes GPU snippet

```yaml
resources:
  limits:
    nvidia.com/gpu: "1"
nodeSelector:
  nvidia.com/gpu.present: "true"
```

Requires the NVIDIA device plugin on the cluster.

---

## Alternatives (when to consider)

| Engine | Fit |
|---|---|
| vLLM | High-throughput OpenAI-compatible serving |
| TGI | HF-centric production serving |
| TensorRT-LLM + Triton | Max performance, more ops complexity |
| Ollama / llama.cpp | Local/dev, not multi-tenant prod |

---

## Capacity sketch

```
needed_replicas ≈ ceil( concurrent_req × avg_out_tokens / tokens_per_sec_per_replica )
```

Add headroom for spikes. Measure tokens/sec yourself — blog numbers lie for your prompts.
