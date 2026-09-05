#!/usr/bin/env bash
# Generate an SPDX SBOM for the lab image into ./out
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=./_common.sh
source "$ROOT/scripts/_common.sh"
cd "$ROOT"

require_docker

IMAGE="${IMAGE:-secure-lab:local}"
TRIVY_IMAGE="${TRIVY_IMAGE:-aquasec/trivy:0.58.1}"
mkdir -p out

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "ERROR: image ${IMAGE} not found."
  echo "Build first: docker build -t ${IMAGE} ."
  exit 1
fi

echo "== SBOM for ${IMAGE} → out/sbom.spdx.json =="
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$ROOT/out:/out" \
  "$TRIVY_IMAGE" image \
  --format spdx-json \
  --output /out/sbom.spdx.json \
  "$IMAGE"

echo "SBOM OK ($(wc -c < out/sbom.spdx.json | tr -d ' ') bytes)"
echo "Tip: search that file for a package name when the next big CVE drops."
