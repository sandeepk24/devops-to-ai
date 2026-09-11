#!/usr/bin/env bash
set -euo pipefail
AGENT="${AGENT_URL:-http://localhost:8100}"
ID="${1:-}"
if [ -z "$ID" ]; then
  echo "Usage: $0 <approval_id>"
  exit 2
fi
curl -sf -X POST "$AGENT/v1/approvals/${ID}/approve" \
  -H "Content-Type: application/json" \
  -d '{"approver":"local-dev"}' | tee /tmp/phase08-approve.json
echo
