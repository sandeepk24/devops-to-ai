#!/usr/bin/env bash
# Inject a fixture alert into the mock control plane.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${1:-crashloop}"
CP="${CONTROL_PLANE_URL:-http://localhost:8090}"
FILE="$ROOT/fixtures/alerts/${NAME}.json"

if [ ! -f "$FILE" ]; then
  echo "Usage: $0 <crashloop|high_latency>"
  echo "Unknown fixture: $NAME"
  exit 2
fi

echo "Injecting $FILE → $CP/v1/alerts"
curl -sf -X POST "$CP/v1/alerts" \
  -H "Content-Type: application/json" \
  -d @"$FILE" | tee /tmp/phase07-alert.json
echo
