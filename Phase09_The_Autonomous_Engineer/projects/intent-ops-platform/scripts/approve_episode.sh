#!/usr/bin/env bash
# Approve one episode's plan. This is the only door to mutating the world.
set -euo pipefail

AGENT="${AGENT_URL:-http://localhost:8200}"
ID="${1:-}"

if [ -z "$ID" ]; then
  echo "Usage: $0 <episode_id>"
  exit 2
fi

curl -sf -X POST "$AGENT/v1/episodes/${ID}/approve" \
  -H "Content-Type: application/json" \
  -d '{"approver":"local-dev"}' | tee /tmp/phase09-approve.json
echo
