#!/usr/bin/env bash
# Path A — filesystem + image scan with Trivy (no local Trivy install).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=./_common.sh
source "$ROOT/scripts/_common.sh"
cd "$ROOT"

require_docker

IMAGE="${IMAGE:-secure-lab:local}"
TRIVY_IMAGE="${TRIVY_IMAGE:-aquasec/trivy:0.58.1}"
SEVERITY="${SEVERITY:-HIGH,CRITICAL}"

echo "== Trivy FS (repo) severity=${SEVERITY} =="
echo "(first run may download the Trivy image + vuln DB — give it a few minutes)"
docker run --rm \
  -v "$ROOT:/src" \
  "$TRIVY_IMAGE" fs \
  --severity "$SEVERITY" \
  --exit-code 1 \
  /src

echo "== Trivy image ${IMAGE} =="
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "ERROR: image ${IMAGE} not found."
  echo "Build it first from this folder:"
  echo "  docker build -t ${IMAGE} ."
  exit 1
fi

docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  "$TRIVY_IMAGE" image \
  --severity "$SEVERITY" \
  --exit-code 1 \
  "$IMAGE"

echo "SCAN OK"
