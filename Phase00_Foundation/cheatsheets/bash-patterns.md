# Bash scripting patterns

Reusable patterns for writing reliable Bash scripts. Copy, adapt, use.

---

## The script header — always start with this

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# set -e  → exit immediately if any command fails
# set -u  → treat unset variables as errors
# set -o pipefail → if any command in a pipe fails, the pipe fails
# IFS     → safer word splitting (newlines and tabs only)
```

This one header prevents the majority of silent failures in Bash scripts.

---

## Variables

```bash
# Basic
NAME="devops-to-ai"
echo "$NAME"              # always quote variables
echo "${NAME}_suffix"     # use braces when concatenating

# Default values
DB_HOST="${DB_HOST:-localhost}"          # use localhost if DB_HOST not set
DB_PORT="${DB_PORT:-5432}"
LOG_LEVEL="${LOG_LEVEL:-info}"

# Required variables — fail fast if not set
: "${API_KEY:?API_KEY environment variable is required}"
: "${DB_PASSWORD:?DB_PASSWORD environment variable is required}"

# Command output into variable
CURRENT_DATE=$(date +%Y-%m-%d)
GIT_SHA=$(git rev-parse --short HEAD)
HOSTNAME=$(hostname -f)

# Arithmetic
COUNT=0
COUNT=$((COUNT + 1))
TOTAL=$((5 * 10))
```

---

## Conditionals

```bash
# File tests
if [[ -f "/etc/nginx/nginx.conf" ]]; then
  echo "nginx config exists"
fi

if [[ ! -d "/var/log/myapp" ]]; then
  mkdir -p /var/log/myapp
fi

# -f  file exists and is a regular file
# -d  directory exists
# -e  file or directory exists
# -r  readable
# -w  writable
# -x  executable
# -s  file exists and is not empty
# -z  string is empty
# -n  string is not empty

# String comparison
if [[ "$ENV" == "production" ]]; then
  echo "running in production"
elif [[ "$ENV" == "staging" ]]; then
  echo "running in staging"
else
  echo "unknown environment: $ENV"
fi

# Numeric comparison
if [[ $EXIT_CODE -ne 0 ]]; then
  echo "command failed with exit code $EXIT_CODE"
fi

# -eq  equal
# -ne  not equal
# -gt  greater than
# -lt  less than
# -ge  greater than or equal
# -le  less than or equal

# Multiple conditions
if [[ -f "$CONFIG" && -r "$CONFIG" ]]; then
  echo "config exists and is readable"
fi

if [[ "$ENV" == "production" || "$ENV" == "staging" ]]; then
  echo "running in a real environment"
fi

# One-liners (use sparingly — prefer explicit if blocks for clarity)
[[ -d "/tmp/work" ]] || mkdir -p /tmp/work
[[ -z "$NAME" ]] && echo "NAME is empty" && exit 1
```

---

## Loops

```bash
# Loop over a list
for server in web-01 web-02 web-03; do
  echo "checking $server"
  ssh "$server" "uptime"
done

# Loop over files
for file in /var/log/*.log; do
  echo "processing $file"
  gzip "$file"
done

# Loop over lines in a file
while IFS= read -r line; do
  echo "processing: $line"
done < servers.txt

# Loop over command output
while IFS= read -r container; do
  docker restart "$container"
done < <(docker ps -q)

# C-style loop
for ((i=1; i<=10; i++)); do
  echo "iteration $i"
done

# While loop with condition
RETRIES=0
MAX_RETRIES=5
while [[ $RETRIES -lt $MAX_RETRIES ]]; do
  if curl -sf http://localhost:8080/health; then
    echo "service is healthy"
    break
  fi
  RETRIES=$((RETRIES + 1))
  echo "attempt $RETRIES/$MAX_RETRIES failed, retrying in 5s..."
  sleep 5
done

if [[ $RETRIES -eq $MAX_RETRIES ]]; then
  echo "service failed to become healthy after $MAX_RETRIES attempts"
  exit 1
fi
```

---

## Functions

```bash
# Basic function
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

log "deployment started"

# Function with return value (via stdout)
get_container_id() {
  local service_name="$1"
  docker ps --filter "name=${service_name}" --format "{{.ID}}" | head -1
}

CONTAINER_ID=$(get_container_id "nginx")

# Function with exit code as return
is_service_running() {
  local service="$1"
  systemctl is-active --quiet "$service"
}

if is_service_running "nginx"; then
  log "nginx is running"
else
  log "nginx is not running"
fi

# Function with local variables (always use local inside functions)
deploy() {
  local image="$1"
  local tag="$2"
  local namespace="${3:-default}"

  log "deploying $image:$tag to namespace $namespace"
  kubectl set image deployment/app "app=${image}:${tag}" -n "$namespace"
}

deploy "myapp" "v1.2.3" "production"
```

---

## Error handling

```bash
# Trap errors — runs cleanup even if script fails
cleanup() {
  local exit_code=$?
  log "script exiting with code $exit_code"
  # cleanup temp files, release locks, etc.
  rm -f /tmp/deploy.lock
}
trap cleanup EXIT

# Trap specific signals
trap 'log "interrupted"; exit 130' INT TERM

# Run a command and handle failure explicitly
if ! docker pull "$IMAGE"; then
  log "ERROR: failed to pull image $IMAGE"
  exit 1
fi

# Run command, capture output and exit code
OUTPUT=$(some-command 2>&1) || {
  log "ERROR: some-command failed: $OUTPUT"
  exit 1
}

# Retry pattern
retry() {
  local max_attempts="$1"
  local delay="$2"
  shift 2
  local cmd=("$@")

  local attempt=1
  while [[ $attempt -le $max_attempts ]]; do
    if "${cmd[@]}"; then
      return 0
    fi
    log "attempt $attempt/$max_attempts failed, retrying in ${delay}s..."
    sleep "$delay"
    attempt=$((attempt + 1))
  done

  log "ERROR: command failed after $max_attempts attempts: ${cmd[*]}"
  return 1
}

retry 3 5 curl -sf http://localhost:8080/health
```

---

## Arguments & input

```bash
# Positional arguments
SCRIPT_NAME="$0"
FIRST_ARG="$1"
SECOND_ARG="$2"
ALL_ARGS="$@"
ARG_COUNT="$#"

# Argument validation
if [[ $# -lt 2 ]]; then
  echo "usage: $0 <environment> <version>"
  echo "  environment: staging|production"
  echo "  version:     e.g. v1.2.3"
  exit 1
fi

ENV="$1"
VERSION="$2"

# getopts — for flag-style arguments
usage() {
  echo "usage: $0 [-e environment] [-v version] [-d] [-h]"
  echo "  -e  environment (staging|production)"
  echo "  -v  version to deploy (e.g. v1.2.3)"
  echo "  -d  dry run — show what would happen without doing it"
  echo "  -h  show this help"
}

DRY_RUN=false
while getopts "e:v:dh" opt; do
  case $opt in
    e) ENV="$OPTARG" ;;
    v) VERSION="$OPTARG" ;;
    d) DRY_RUN=true ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

if [[ "$DRY_RUN" == "true" ]]; then
  log "DRY RUN: would deploy $VERSION to $ENV"
else
  log "deploying $VERSION to $ENV"
fi
```

---

## String operations

```bash
NAME="devops-to-ai-v1.2.3"

# Length
echo "${#NAME}"              # 18

# Substring
echo "${NAME:0:6}"           # devops
echo "${NAME:7}"             # to-ai-v1.2.3

# Remove prefix
echo "${NAME#devops-}"       # to-ai-v1.2.3
echo "${NAME##*-}"           # v1.2.3   (greedy — removes everything up to last -)

# Remove suffix
echo "${NAME%-*}"            # devops-to-ai  (removes last -... to end)
echo "${NAME%.*}"            # devops-to-ai-v1  (removes last .*)

# Replace
echo "${NAME/ai/AI}"         # devops-to-AI-v1.2.3  (first occurrence)
echo "${NAME//./\_}"         # devops-to-ai-v1_2_3  (all occurrences)

# Uppercase / lowercase
echo "${NAME^^}"             # DEVOPS-TO-AI-V1.2.3
echo "${NAME,,}"             # devops-to-ai-v1.2.3

# Check if string contains substring
if [[ "$NAME" == *"v1"* ]]; then
  echo "version 1.x"
fi

# Split string into array
IFS='-' read -ra PARTS <<< "$NAME"
echo "${PARTS[0]}"           # devops
echo "${PARTS[@]}"           # all parts
```

---

## Working with files

```bash
# Read file into variable
CONFIG=$(cat config.yaml)

# Read file line by line
while IFS= read -r line; do
  echo "$line"
done < input.txt

# Write to file
echo "hello" > file.txt         # overwrite
echo "hello" >> file.txt        # append

cat > file.txt << 'EOF'
line one
line two
line three
EOF

# Temp files — always use mktemp
TEMP_FILE=$(mktemp)
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_FILE $TEMP_DIR" EXIT

# Check file is not empty
if [[ ! -s "$LOG_FILE" ]]; then
  echo "log file is empty"
fi

# Lock file pattern — prevent concurrent runs
LOCK_FILE="/tmp/myscript.lock"
if [[ -f "$LOCK_FILE" ]]; then
  echo "script is already running (lock file: $LOCK_FILE)"
  exit 1
fi
touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT
```

---

## Logging pattern

```bash
# Colour-coded logging (the pattern used in most real scripts)
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'   # no colour

log::info()    { echo -e "${BLUE}[INFO]${NC}  $(date '+%H:%M:%S') $*"; }
log::success() { echo -e "${GREEN}[OK]${NC}    $(date '+%H:%M:%S') $*"; }
log::warn()    { echo -e "${YELLOW}[WARN]${NC}  $(date '+%H:%M:%S') $*" >&2; }
log::error()   { echo -e "${RED}[ERROR]${NC} $(date '+%H:%M:%S') $*" >&2; }

log::info "starting deployment"
log::warn "staging environment — proceeding with caution"
log::error "failed to connect to database"
log::success "deployment complete"
```

---

## Complete script template

```bash
#!/usr/bin/env bash
set -euo pipefail

# ── constants ─────────────────────────────────────────────────────────────────
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"
readonly LOG_FILE="/var/log/${SCRIPT_NAME%.sh}.log"

# ── colours ───────────────────────────────────────────────────────────────────
readonly RED='\033[0;31m'; readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'; readonly NC='\033[0m'

# ── logging ───────────────────────────────────────────────────────────────────
log()   { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
info()  { echo -e "${GREEN}[INFO]${NC}  $*" | tee -a "$LOG_FILE"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*" | tee -a "$LOG_FILE" >&2; }
error() { echo -e "${RED}[ERROR]${NC} $*" | tee -a "$LOG_FILE" >&2; }

# ── usage ─────────────────────────────────────────────────────────────────────
usage() {
  cat << EOF
usage: $SCRIPT_NAME [options]

options:
  -e <env>    target environment (staging|production)
  -v <ver>    version to deploy (e.g. v1.2.3)
  -d          dry run
  -h          show this help
EOF
}

# ── cleanup ───────────────────────────────────────────────────────────────────
cleanup() {
  local exit_code=$?
  [[ $exit_code -ne 0 ]] && error "script failed with exit code $exit_code"
  rm -f /tmp/deploy.lock
}
trap cleanup EXIT
trap 'error "interrupted"; exit 130' INT TERM

# ── argument parsing ──────────────────────────────────────────────────────────
ENV=""
VERSION=""
DRY_RUN=false

while getopts "e:v:dh" opt; do
  case $opt in
    e) ENV="$OPTARG" ;;
    v) VERSION="$OPTARG" ;;
    d) DRY_RUN=true ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

# ── validation ────────────────────────────────────────────────────────────────
[[ -z "$ENV" ]]     && error "-e <env> is required"     && usage && exit 1
[[ -z "$VERSION" ]] && error "-v <ver> is required"     && usage && exit 1
[[ "$ENV" != "staging" && "$ENV" != "production" ]] \
  && error "env must be staging or production" && exit 1

# ── main ──────────────────────────────────────────────────────────────────────
main() {
  info "deploying $VERSION to $ENV"

  if [[ "$DRY_RUN" == "true" ]]; then
    warn "dry run — no changes will be made"
    return 0
  fi

  # your logic here
  info "deployment complete"
}

main "$@"
```

---

*Part of [devops-to-ai](../../README.md) — Phase 00: The Foundation*
