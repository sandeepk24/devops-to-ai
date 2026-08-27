#!/usr/bin/env bash
# Generate light load against the gateway so Grafana panels are non-empty.
set -euo pipefail

GATEWAY_URL="${GATEWAY_URL:-http://localhost:8080}"
API_KEY="${API_KEY:-dev-key}"
REQUESTS="${REQUESTS:-30}"

echo "Sending $REQUESTS chat completions to $GATEWAY_URL ..."
for i in $(seq 1 "$REQUESTS"); do
  curl -sf "$GATEWAY_URL/v1/chat/completions" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"mock-model\",\"messages\":[{\"role\":\"user\",\"content\":\"Load ping $i — what is queue depth?\"}],\"max_tokens\":32}" \
    >/dev/null
  printf "."
done
echo
echo "Done. Refresh Grafana: LLM Inference Gateway dashboard."
