#!/usr/bin/env bash
# Path B — wait until Kyverno pods are Ready before applying policies.
set -euo pipefail

NAMESPACE="${KYVERNO_NAMESPACE:-kyverno}"
TIMEOUT_SECS="${TIMEOUT_SECS:-180}"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "ERROR: kubectl not found. Install kubectl, then retry."
  exit 1
fi

echo "Waiting up to ${TIMEOUT_SECS}s for Kyverno in namespace ${NAMESPACE}..."
echo "Context: $(kubectl config current-context 2>/dev/null || echo '(none)')"

if ! kubectl get ns "$NAMESPACE" >/dev/null 2>&1; then
  echo "ERROR: namespace ${NAMESPACE} not found."
  echo "Did you apply the Kyverno install YAML first? See Path B in the project README."
  exit 1
fi

kubectl wait --namespace "$NAMESPACE" \
  --for=condition=Ready pod \
  --selector=app.kubernetes.io/part-of=kyverno \
  --timeout="${TIMEOUT_SECS}s" 2>/dev/null \
  || kubectl wait --namespace "$NAMESPACE" \
    --for=condition=Ready pod \
    --all \
    --timeout="${TIMEOUT_SECS}s"

echo "Kyverno looks ready. Next: kubectl apply -f policy/disallow-privileged.yaml"
