#!/usr/bin/env bash
# Path A smoke: suggest → auto heal → kill switch skip.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
CP="${CONTROL_PLANE_URL:-http://localhost:8090}"

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

# Short cooldown so smoke doesn't wait forever between steps
if grep -q '^COOLDOWN_SECONDS=' .env; then
  sed -i.bak 's/^COOLDOWN_SECONDS=.*/COOLDOWN_SECONDS=3/' .env
else
  echo 'COOLDOWN_SECONDS=3' >> .env
fi
rm -f .env.bak

echo "== compose up =="
docker compose up --build -d

echo "== wait for control plane =="
for _ in $(seq 1 40); do
  if curl -sf "$CP/health" >/dev/null; then
    break
  fi
  sleep 1
done
curl -sf "$CP/health" >/dev/null

echo "== reset world =="
curl -sf -X POST "$CP/v1/reset" >/dev/null

audit_has() {
  local needle="$1"
  curl -sf "$CP/v1/audit?limit=100" | grep -q "$needle"
}

wait_audit() {
  local needle="$1"
  local tries="${2:-20}"
  for _ in $(seq 1 "$tries"); do
    if audit_has "$needle"; then
      return 0
    fi
    sleep 1
  done
  echo "ERROR: audit missing '$needle'"
  curl -sf "$CP/v1/audit?limit=20" || true
  exit 1
}

echo "== SUGGEST mode =="
./scripts/set_mode.sh suggest
curl -sf -X POST "$CP/v1/reset" >/dev/null
./scripts/inject_alert.sh crashloop >/dev/null
wait_audit '"outcome": "suggest"'
# service should still be crashloop until someone acts
status=$(curl -sf "$CP/v1/services/flappy" | sed -n 's/.*"status": "\([^"]*\)".*/\1/p' | head -1)
if [ "$status" != "crashloop" ]; then
  echo "WARN: expected crashloop in suggest mode, got: $status (continuing if suggest audit present)"
fi
echo "suggest OK"

echo "== AUTO mode =="
./scripts/set_mode.sh auto
curl -sf -X POST "$CP/v1/reset" >/dev/null
./scripts/inject_alert.sh crashloop >/dev/null
wait_audit '"kind": "verify"'
status=$(curl -sf "$CP/v1/services/flappy" | sed -n 's/.*"status": "\([^"]*\)".*/\1/p' | head -1)
if [ "$status" != "healthy" ]; then
  echo "ERROR: expected healthy after auto restart, got: $status"
  exit 1
fi
echo "auto OK"

echo "== KILL SWITCH =="
./scripts/set_mode.sh auto kill
curl -sf -X POST "$CP/v1/reset" >/dev/null
./scripts/inject_alert.sh crashloop >/dev/null
wait_audit 'skipped_kill_switch'
status=$(curl -sf "$CP/v1/services/flappy" | sed -n 's/.*"status": "\([^"]*\)".*/\1/p' | head -1)
if [ "$status" = "healthy" ]; then
  echo "ERROR: kill switch should leave service unhealthy/crashloop"
  exit 1
fi
echo "kill switch OK"

echo "== high_latency stays non-acting =="
./scripts/set_mode.sh auto
curl -sf -X POST "$CP/v1/reset" >/dev/null
./scripts/inject_alert.sh high_latency >/dev/null
wait_audit 'suggest_only_no_safe_action'
echo "latency policy OK"

echo "SMOKE OK — Path A complete"
