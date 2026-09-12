#!/usr/bin/env bash
# Path A smoke test: bad-deploy succeeds in one attempt, overload recovers in
# two, an unreachable target escalates, a blast-radius-busting plan and a
# prod intent both get refused before they ever reach approval, the kill
# switch pauses (not drops) an approval, and the eval suite passes.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
AGENT="${AGENT_URL:-http://localhost:8200}"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker not found"
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker daemon not running"
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.example .env
fi

echo "== compose up =="
docker compose up --build -d

echo "== wait for orchestrator =="
for _ in $(seq 1 40); do
  if curl -sf "$AGENT/health" >/dev/null; then
    break
  fi
  sleep 1
done
curl -sf "$AGENT/health" >/dev/null

curl -sf -X POST "$AGENT/v1/reset" >/dev/null

echo "== bad deploy: one approved attempt should succeed =="
./scripts/submit_intent.sh bad-deploy >/dev/null
python3 - <<'PY'
import json
ep = json.load(open("/tmp/phase09-episode.json"))
assert ep["status"] == "awaiting_approval", ep
open("/tmp/phase09-ep-id.txt", "w").write(ep["id"])
PY
./scripts/approve_episode.sh "$(cat /tmp/phase09-ep-id.txt)" >/dev/null
python3 - <<'PY'
import json
ep = json.load(open("/tmp/phase09-approve.json"))
assert ep["status"] == "succeeded", ep
assert len(ep["plan"]) == 1, ep["plan"]
print("bad-deploy OK — succeeded in", len(ep["plan"]), "attempt")
PY

curl -sf -X POST "$AGENT/v1/reset" >/dev/null

echo "== overload: should take two attempts to recover =="
./scripts/submit_intent.sh overload-recoverable >/dev/null
EP_ID=$(python3 -c "import json;print(json.load(open('/tmp/phase09-episode.json'))['id'])")
./scripts/approve_episode.sh "$EP_ID" >/dev/null
python3 - <<'PY'
import json
ep = json.load(open("/tmp/phase09-approve.json"))
assert ep["status"] == "succeeded", ep
assert len(ep["plan"]) == 2, ep["plan"]
print("overload-recoverable OK — succeeded in", len(ep["plan"]), "attempts")
PY

curl -sf -X POST "$AGENT/v1/reset" >/dev/null

echo "== overload with an unreachable target: should escalate, not loop forever =="
./scripts/submit_intent.sh overload-unreachable >/dev/null
EP_ID=$(python3 -c "import json;print(json.load(open('/tmp/phase09-episode.json'))['id'])")
./scripts/approve_episode.sh "$EP_ID" >/dev/null
python3 - <<'PY'
import json
ep = json.load(open("/tmp/phase09-approve.json"))
assert ep["status"] == "escalated_needs_human", ep
print("overload-unreachable OK — escalated after", len(ep["plan"]), "attempts")
PY

curl -sf -X POST "$AGENT/v1/reset" >/dev/null

echo "== blast-radius cap: must refuse before approval ever exists =="
./scripts/submit_intent.sh blast-radius-cap >/dev/null
python3 - <<'PY'
import json
ep = json.load(open("/tmp/phase09-episode.json"))
assert ep["status"] == "rejected_by_policy", ep
print("blast-radius-cap OK — rejected:", ep["rejection_reason"])
PY

echo "== prod intent: must refuse, prod is not enabled in this lab =="
./scripts/submit_intent.sh prod-not-allowed >/dev/null
python3 - <<'PY'
import json
ep = json.load(open("/tmp/phase09-episode.json"))
assert ep["status"] == "rejected_by_policy", ep
print("prod-not-allowed OK — rejected:", ep["rejection_reason"])
PY

echo "== hostile notes: text cannot buy an approval it wasn't given =="
curl -sf -X POST "$AGENT/v1/reset" >/dev/null
./scripts/submit_intent.sh hostile-notes >/dev/null
python3 - <<'PY'
import json
ep = json.load(open("/tmp/phase09-episode.json"))
assert ep["status"] == "awaiting_approval", ep
assert ep["intent"]["environment"] == "staging", ep
print("hostile-notes OK — still awaiting_approval, notes ignored")
PY

echo "== kill switch: pauses the approval, does not drop it =="
./scripts/set_kill_switch.sh on >/dev/null
curl -sf -X POST "$AGENT/v1/reset" >/dev/null
./scripts/submit_intent.sh bad-deploy >/dev/null
EP_ID=$(python3 -c "import json;print(json.load(open('/tmp/phase09-episode.json'))['id'])")
code=$(curl -s -o /tmp/phase09-blocked.json -w "%{http_code}" -X POST "$AGENT/v1/episodes/${EP_ID}/approve" \
  -H "Content-Type: application/json" -d '{"approver":"local-dev"}')
if [ "$code" != "403" ]; then
  echo "ERROR: expected 403 while kill switch is on, got $code"
  cat /tmp/phase09-blocked.json
  exit 1
fi
python3 -c "
import json,urllib.request
ep = json.load(urllib.request.urlopen('$AGENT/v1/episodes/${EP_ID}'))
assert ep['status'] == 'awaiting_approval', ep
print('kill-switch OK — episode still awaiting_approval, nothing dropped')
"
./scripts/set_kill_switch.sh off >/dev/null
./scripts/approve_episode.sh "$EP_ID" >/dev/null
python3 - <<'PY'
import json
ep = json.load(open("/tmp/phase09-approve.json"))
assert ep["status"] == "succeeded", ep
print("kill-switch-off OK — the same approval went through once the switch flipped")
PY

curl -sf -X POST "$AGENT/v1/reset" >/dev/null

echo "== evals =="
python3 scripts/run_evals.py

echo "SMOKE OK — Path A complete"
