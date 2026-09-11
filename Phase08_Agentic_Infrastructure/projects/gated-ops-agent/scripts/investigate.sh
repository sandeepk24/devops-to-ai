#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${1:-high-error-rate}"
AGENT="${AGENT_URL:-http://localhost:8100}"
FILE="$ROOT/fixtures/incidents/${NAME}.json"
if [ ! -f "$FILE" ]; then
  echo "Usage: $0 <high-error-rate|hostile-injection>"
  exit 2
fi
curl -sf -X POST "$AGENT/v1/investigate" \
  -H "Content-Type: application/json" \
  -d @"$FILE" | tee /tmp/phase08-investigate.json
echo
