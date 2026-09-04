#!/usr/bin/env bash
# Path A — filesystem + image scan with Trivy (no local Trivy install).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

IMAGE="${IMAGE:-secure-lab:local}"
TRIVY_IMAGE="${TRIVY_IMAGE:-aquasec/trivy:0.58.1}"
SEVERITY="${SEVERITY:-HIGH,CRITICAL}"

echo "== Trivy FS (repo) severity=${SEVERITY} =="
docker run --rm \
  -v "$ROOT:/src" \
  "$TRIVY_IMAGE" fs \
  --severity "$SEVERITY" \
  --exit-code 1 \
  /src

echo "== Trivy image ${IMAGE} =="
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "Image ${IMAGE} not found. Build first: docker build -t ${IMAGE} ."
  exit 1
fi

docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  "$TRIVY_IMAGE" image \
  --severity "$SEVERITY" \
  --exit-code 1 \
  "$IMAGE"

echo "SCAN OK"
