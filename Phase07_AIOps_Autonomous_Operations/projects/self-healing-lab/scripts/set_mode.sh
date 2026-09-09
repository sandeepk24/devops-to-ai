#!/usr/bin/env bash
# Flip healer mode by rewriting .env and recreating the healer container.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODE="${1:-}"
FLAG="${2:-}"

if [ -z "$MODE" ] || [[ ! "$MODE" =~ ^(suggest|auto)$ ]]; then
  echo "Usage: $0 suggest|auto [kill]"
  echo "  kill  → also set KILL_SWITCH=true"
  exit 2
fi

if [ ! -f .env ]; then
  cp .env.example .env
fi

# Portable-ish in-place env updates
set_kv() {
  local key="$1" val="$2"
  if grep -q "^${key}=" .env; then
    sed -i.bak "s|^${key}=.*|${key}=${val}|" .env
  else
    echo "${key}=${val}" >> .env
  fi
}

set_kv HEALER_MODE "$MODE"
if [ "$FLAG" = "kill" ]; then
  set_kv KILL_SWITCH true
else
  set_kv KILL_SWITCH false
fi
rm -f .env.bak

echo "HEALER_MODE=$MODE KILL_SWITCH=$(grep '^KILL_SWITCH=' .env | cut -d= -f2)"
docker compose up -d --force-recreate healer
# give poll loop a moment
sleep 2
curl -sf http://localhost:8091/v1/config | tee /tmp/phase07-healer-config.json
echo
