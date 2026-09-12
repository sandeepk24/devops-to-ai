#!/usr/bin/env bash
# Flip the kill switch at runtime — no restart, no lost episodes. An
# approval that was blocked while it was on can go through the moment
# it's off again, because nothing about the episode ever got wiped.
set -euo pipefail

AGENT="${AGENT_URL:-http://localhost:8200}"
MODE="${1:-}"

if [[ ! "$MODE" =~ ^(on|off)$ ]]; then
  echo "Usage: $0 on|off"
  exit 2
fi

VAL="false"
[ "$MODE" = "on" ] && VAL="true"

curl -sf -X POST "$AGENT/v1/admin/kill_switch" \
  -H "Content-Type: application/json" \
  -d "{\"enabled\": ${VAL}}"
echo
curl -sf "$AGENT/health" | tee /tmp/phase09-health.json
echo
