#!/usr/bin/env bash
# Path B — build image, load into kind, apply k8s manifests for a scaffolded service.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${1:-}"
CLUSTER="${KIND_CLUSTER:-phase06}"

if [ -z "$NAME" ]; then
  echo "Usage: $0 <service-name>"
  echo "Example: KIND_CLUSTER=phase06 $0 demo-api"
  exit 2
fi

DIR="$ROOT/services/$NAME"
if [ ! -d "$DIR" ]; then
  echo "ERROR: services/${NAME} missing. Run: ./scripts/new_service.sh ${NAME}"
  exit 1
fi

for cmd in docker kubectl kind; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR: ${cmd} not found. Path B needs docker, kubectl, and kind."
    exit 1
  fi
done

if ! kind get clusters 2>/dev/null | grep -qx "$CLUSTER"; then
  echo "ERROR: kind cluster '${CLUSTER}' not found."
  echo "Create it: kind create cluster --name ${CLUSTER}"
  exit 1
fi

echo "== building ${NAME}:local =="
docker build -t "${NAME}:local" "$DIR"

echo "== loading image into kind (${CLUSTER}) =="
kind load docker-image "${NAME}:local" --name "$CLUSTER"

echo "== applying manifests =="
kubectl apply -f "$DIR/k8s/app.yaml"

echo "== waiting for rollout =="
kubectl -n "$NAME" rollout status deployment/"$NAME" --timeout=120s

echo "OK — deployed ${NAME} to namespace ${NAME}"
echo "Try: kubectl -n ${NAME} port-forward svc/${NAME} 8080:8080"
