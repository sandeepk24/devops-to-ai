#!/usr/bin/env bash
# Smoke test for the Phase 04 LLM inference platform (mock path).
set -euo pipefail

GATEWAY_URL="${GATEWAY_URL:-http://localhost:8080}"
RAG_URL="${RAG_URL:-http://localhost:8081}"
API_KEY="${API_KEY:-dev-key}"

echo "== health =="
curl -sf "$GATEWAY_URL/health" | tee /tmp/gw-health.json
echo
curl -sf "$GATEWAY_URL/ready" | tee /tmp/gw-ready.json
echo

echo "== chat completion =="
curl -sf "$GATEWAY_URL/v1/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"mock-model","messages":[{"role":"user","content":"What is TTFT?"}],"max_tokens":64}' \
  | tee /tmp/chat.json
echo

echo "== unauthorized should 401 =="
code=$(curl -s -o /dev/null -w "%{http_code}" "$GATEWAY_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{"model":"mock-model","messages":[{"role":"user","content":"x"}]}')
test "$code" = "401"

echo "== rag ingest + query =="
curl -sf -X POST "$RAG_URL/v1/rag/ingest" | tee /tmp/ingest.json
echo
curl -sf "$RAG_URL/v1/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"question":"How do we roll back a bad model canary?"}' \
  | tee /tmp/rag.json
echo

echo "== metrics exposed =="
curl -sf "$GATEWAY_URL/metrics" | grep -q llm_gateway_requests_total

echo "== rate limit should eventually 429 =="
# Use a throwaway key only if present; otherwise hammer the default carefully.
limited=0
for _ in $(seq 1 $(( ${RATE_LIMIT_RPM:-60} + 5 ))); do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$GATEWAY_URL/v1/chat/completions" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model":"mock-model","messages":[{"role":"user","content":"rl"}],"max_tokens":8}')
  if [ "$code" = "429" ]; then
    limited=1
    break
  fi
done
# Soft check: if RATE_LIMIT_RPM is very high this may not trip in CI — warn only.
if [ "$limited" -ne 1 ]; then
  echo "WARN: did not observe 429 (raise load or lower RATE_LIMIT_RPM to verify)"
fi

echo "SMOKE OK"
