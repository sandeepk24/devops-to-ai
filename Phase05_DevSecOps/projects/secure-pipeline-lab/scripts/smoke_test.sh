#!/usr/bin/env bash
# End-to-end Path A smoke: build (if needed), scan, SBOM, manifest checks.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=./_common.sh
source "$ROOT/scripts/_common.sh"
cd "$ROOT"

require_docker

IMAGE="${IMAGE:-secure-lab:local}"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "== building ${IMAGE} =="
  docker build -t "$IMAGE" .
fi

./scripts/scan_local.sh
./scripts/generate_sbom.sh

echo "== expect GOOD manifest to pass =="
./scripts/check_manifests.sh k8s/deployment-good.yaml

echo "== expect BAD manifest to fail =="
if ./scripts/check_manifests.sh k8s/deployment-bad-privileged.yaml; then
  echo "ERROR: bad privileged manifest was not rejected"
  exit 1
fi
echo "bad manifest correctly rejected"

echo "SMOKE OK — Path A complete. Read the project README for CI + Path B next."
