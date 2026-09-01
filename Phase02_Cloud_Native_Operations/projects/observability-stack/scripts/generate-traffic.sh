#!/usr/bin/env bash
# Generate checkout traffic for Phase 02 observability demos.
set -euo pipefail

BASE="${BASE_URL:-http://localhost:8000}"
REQUESTS="${REQUESTS:-40}"

echo "Sending $REQUESTS checkout requests to $BASE ..."

for i in $(seq 1 "$REQUESTS"); do
  user="user-$(( (i % 10) + 1 ))"
  amount=$(awk -v n="$i" 'BEGIN { printf "%.2f", 10 + (n % 50) }')
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    "${BASE}/checkout?user_id=${user}&amount=${amount}")
  printf "."
  if [ "$(( i % 20 ))" -eq 0 ]; then echo " ($i, last=$code)"; fi
  sleep 0.15
done

echo
echo "Done. Check Grafana / Prometheus / Tempo."
echo "Tip: mix in bad-user requests to force 404s:"
echo "  curl -X POST '${BASE}/checkout?user_id=bad-user&amount=1'"
