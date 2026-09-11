#!/usr/bin/env bash
# Path A smoke: investigate → ungated refuse → approve → world updated → evals
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
AGENT="${AGENT_URL:-http://localhost:8100}"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker not found"
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker daemon not running"
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.example .env
fi

echo "== compose up =="
docker compose up --build -d

echo "== wait for agent =="
for _ in $(seq 1 40); do
  if curl -sf "$AGENT/health" >/dev/null; then
    break
  fi
  sleep 1
done
curl -sf "$AGENT/health" >/dev/null

curl -sf -X POST "$AGENT/v1/reset" >/dev/null

echo "== investigate =="
./scripts/investigate.sh high-error-rate >/dev/null
python3 - <<'PY'
import json
data=json.load(open("/tmp/phase08-investigate.json"))
assert data.get("mutation_executed") is False
assert data.get("approval_id"), "expected approval_id"
tools=[t["tool"] for t in data.get("tool_results",[]) if t.get("ok")]
assert "get_service_metrics" in tools or "get_recent_logs" in tools
open("/tmp/phase08-approval-id.txt","w").write(data["approval_id"])
print("investigate OK", data["approval_id"])
PY

echo "== ungated execute must fail =="
code=$(curl -s -o /tmp/phase08-ungated.json -w "%{http_code}" -X POST "$AGENT/v1/actions/execute_rollback" \
  -H "Content-Type: application/json" \
  -d '{"service":"payments-api"}')
if [ "$code" != "403" ] && [ "$code" != "400" ]; then
  echo "ERROR: expected 403/400 for ungated rollback, got $code"
  cat /tmp/phase08-ungated.json
  exit 1
fi
echo "ungated refuse OK ($code)"

echo "== approve =="
APR=$(cat /tmp/phase08-approval-id.txt)
./scripts/approve.sh "$APR" >/dev/null
python3 - <<'PY'
import json,urllib.request
world=json.load(urllib.request.urlopen("http://localhost:8100/v1/world"))
svc=world.get("services",{}).get("payments-api")
assert svc and svc.get("last_action")=="rollback", world
print("approve+execute OK")
PY

echo "== evals =="
python3 scripts/run_evals.py

echo "SMOKE OK — Path A complete"
