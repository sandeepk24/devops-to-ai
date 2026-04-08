#!/usr/bin/env bash
set -euo pipefail

# Server health reporter — cron wrapper
# Designed to be called by cron every 6 hours:
# 0 */6 * * * /full/path/to/server-health-reporter/run.sh

# ── config ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/config.yaml"
LOG_FILE="${SCRIPT_DIR}/logs/run.log"
PYTHON_BIN="${PYTHON_BIN:-python3}"

# ── setup ──────────────────────────────────────────────────────────────────────
mkdir -p "${SCRIPT_DIR}/logs"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# ── checks ─────────────────────────────────────────────────────────────────────
if [[ ! -f "$CONFIG_FILE" ]]; then
  log "ERROR: config file not found at $CONFIG_FILE"
  log "Copy config.example.yaml to config.yaml and edit it"
  exit 1
fi

if ! command -v "$PYTHON_BIN" &>/dev/null; then
  log "ERROR: python3 not found"
  exit 1
fi

# ── run ────────────────────────────────────────────────────────────────────────
log "starting health reporter"

cd "$SCRIPT_DIR"

# TODO: activate a virtualenv here if you're using one
# source .venv/bin/activate

if "$PYTHON_BIN" reporter.py --config "$CONFIG_FILE"; then
  log "reporter completed successfully"
else
  log "ERROR: reporter exited with error code $?"
  exit 1
fi
