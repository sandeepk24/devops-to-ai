# Continuous batching

Continuous batching is an inference-server technique that keeps the GPU busy by inserting new requests into the decode batch as soon as other requests finish, instead of waiting for an entire static batch to complete.

## Why it matters

- Improves tokens/sec under concurrent load
- Reduces average queue wait compared with static batching
- Pairs with paged KV-cache management (e.g. PagedAttention in vLLM)

## Operator notes

Watch queue depth and time-to-first-token together. A saturated GPU can still accept HTTP connections while TTFT explodes — that is a capacity problem, not an application bug.
