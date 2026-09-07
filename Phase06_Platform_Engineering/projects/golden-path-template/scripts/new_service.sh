#!/usr/bin/env bash
# Scaffold a new service from the golden-path skeleton.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${1:-}"

if [ -z "$NAME" ]; then
  echo "Usage: $0 <service-name>"
  echo "Example: $0 demo-api"
  echo "Name rules: lowercase letters, numbers, hyphens (Kubernetes-friendly)."
  exit 2
fi

if ! [[ "$NAME" =~ ^[a-z0-9]([a-z0-9-]*[a-z0-9])?$ ]]; then
  echo "ERROR: '$NAME' is not a safe service name."
  echo "Use lowercase DNS-ish labels: demo-api, payments-bff, checkout2"
  exit 2
fi

DEST="$ROOT/services/$NAME"
if [ -e "$DEST" ]; then
  echo "ERROR: $DEST already exists. Pick a new name or remove it."
  exit 1
fi

mkdir -p "$ROOT/services"
cp -R "$ROOT/skeleton" "$DEST"

# Replace placeholder in text files (skip nothing critical — skeleton is small).
# macOS/BSD sed needs backup suffix; use a portable approach.
while IFS= read -r -d '' file; do
  if grep -q "__SERVICE_NAME__" "$file" 2>/dev/null; then
    tmp="${file}.tmp"
    sed "s/__SERVICE_NAME__/${NAME}/g" "$file" > "$tmp"
    mv "$tmp" "$file"
  fi
done < <(find "$DEST" -type f -print0)

# Hide the example workflow name confusion: keep .example suffix.
# (Already named ci.yml.example in skeleton.)

cat <<EOF
OK — scaffolded services/${NAME}

Next (Path A):
  cd services/${NAME}
  docker compose up --build -d
  curl -s http://localhost:8080/health

Or from template root:
  ./scripts/smoke_test.sh ${NAME}

Edit ownership in:
  services/${NAME}/catalog-info.yaml
  services/${NAME}/docs/runbook.md
EOF
