#!/usr/bin/env bash
# Path A smoke: scaffold (if needed), compose up, curl /health, tear down optional.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${1:-demo-api}"
COMPOSE_FILE="$ROOT/services/$NAME/compose.yaml"
HOST_PORT="${HOST_PORT:-8080}"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker not found. Install Docker Desktop and retry."
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker daemon not running. Start Docker Desktop, then retry."
  exit 1
fi

if [ ! -d "$ROOT/services/$NAME" ]; then
  echo "== scaffolding ${NAME} =="
  "$ROOT/scripts/new_service.sh" "$NAME"
fi

echo "== compose up ${NAME} (host port ${HOST_PORT}) =="
HOST_PORT="$HOST_PORT" docker compose -f "$COMPOSE_FILE" up --build -d

echo "== waiting for /health =="
ok=0
for _ in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:${HOST_PORT}/health" >/tmp/phase06-health.json 2>/dev/null; then
    ok=1
    break
  fi
  sleep 2
done

if [ "$ok" -ne 1 ]; then
  echo "ERROR: /health did not become ready. Logs:"
  docker compose -f "$COMPOSE_FILE" logs --tail=80
  exit 1
fi

echo "health response:"
cat /tmp/phase06-health.json
echo
curl -sf "http://127.0.0.1:${HOST_PORT}/v1/info"
echo
echo "SMOKE OK — Path A works for ${NAME}"
echo "Leave it running, or: docker compose -f services/${NAME}/compose.yaml down"
