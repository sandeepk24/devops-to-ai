#!/usr/bin/env bash
# Submit an intent fixture and print the resulting episode.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGENT="${AGENT_URL:-http://localhost:8200}"
NAME="${1:-bad-deploy}"
FILE="$ROOT/fixtures/intents/${NAME}.json"

if [ ! -f "$FILE" ]; then
  echo "Usage: $0 <intent-fixture-name>"
  echo "Available: $(ls "$ROOT/fixtures/intents" | sed 's/\.json$//' | tr '\n' ' ')"
  exit 2
fi

curl -sf -X POST "$AGENT/v1/intents" \
  -H "Content-Type: application/json" \
  -d @"$FILE" | tee /tmp/phase09-episode.json
echo
