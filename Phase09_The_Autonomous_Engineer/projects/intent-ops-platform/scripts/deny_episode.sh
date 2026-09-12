#!/usr/bin/env bash
# Deny one episode's plan. Nothing executes.
set -euo pipefail

AGENT="${AGENT_URL:-http://localhost:8200}"
ID="${1:-}"

if [ -z "$ID" ]; then
  echo "Usage: $0 <episode_id>"
  exit 2
fi

curl -sf -X POST "$AGENT/v1/episodes/${ID}/deny" \
  -H "Content-Type: application/json" \
  -d '{"approver":"local-dev"}' | tee /tmp/phase09-deny.json
echo
