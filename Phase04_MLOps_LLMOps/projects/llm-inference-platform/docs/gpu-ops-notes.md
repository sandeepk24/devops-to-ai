# GPU utilisation notes — Phase 04

Operators often discover too late that "GPU util 100%" is not the same as
"serving is healthy."

## What to watch on the node

```bash
nvidia-smi
nvidia-smi --query-gpu=utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu --format=csv -l 5
```

| Signal | Healthy pattern | Trouble |
|---|---|---|
| GPU util | High under load, drops when idle | 100% with rising TTFT → overload |
| Memory used | Stable near model+KV footprint | Climbing until OOM / pod restart |
| Temperature | Within vendor range | Thermal throttle → token/sec cliff |
| ECC / Xid errors | None | Hardware or driver faults |

## Application-side companions

Correlate `nvidia-smi` with:

- Gateway p99 latency + TTFT
- Queue depth / waiting requests (engine metrics)
- Tokens/sec
- Autoscale events (HPA / custom)

## Fractional GPUs

MIG / time-slicing can improve packing but complicates performance isolation.
Document which workloads share a GPU before you debug "mystery" latency.

## Stretch task

Export DCGM or `nvidia-smi` metrics into Prometheus and add a Grafana row
for GPU util + VRAM next to the gateway panels.
