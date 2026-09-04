#!/usr/bin/env bash
# Path A teaching brake: fail if a manifest enables privileged containers.
# Not a replacement for Kyverno admission — see Path B in the project README.
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <manifest.yaml> [more.yaml...]"
  exit 2
fi

fail=0
for f in "$@"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: missing file $f"
    fail=1
    continue
  fi
  # Match privileged: true (common YAML forms). Ignore comments.
  if grep -E '^[[:space:]]*privileged:[[:space:]]*true[[:space:]]*(#.*)?$' "$f" >/dev/null; then
    echo "FAIL: $f sets privileged: true"
    fail=1
  else
    echo "OK: $f (no privileged: true)"
  fi
done

if [ "$fail" -ne 0 ]; then
  exit 1
fi
echo "MANIFEST CHECK OK"
