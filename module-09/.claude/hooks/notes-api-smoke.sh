#!/usr/bin/env bash
# notes-api-smoke runner.
#
# Boots a single-file FastAPI app in an ephemeral dependency env and asserts
# its CRUD contract over HTTP. Prints PASS/FAIL per endpoint and exits
# non-zero on ANY failure, so it can gate a git pre-commit hook.
#
# Usage: notes-api-smoke.sh [MODULE_PATH] [PORT] [RESOURCE]
#   MODULE_PATH  path (repo-relative) to the .py file defining `app`  [module-09/notes_api.py]
#   PORT         localhost port to bind                               [8099]
#   RESOURCE     collection path under test                           [/notes]
set -uo pipefail

export PATH="$HOME/.local/bin:$PATH"

MODULE="${1:-module-09/notes_api.py}"
PORT="${2:-8099}"
RESOURCE="${3:-/notes}"

if ! command -v uv >/dev/null 2>&1; then
  echo "FAIL  tooling  (uv not found on PATH)" >&2
  exit 2
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
ABS_MODULE="$REPO_ROOT/$MODULE"
APP_DIR="$(cd "$(dirname "$ABS_MODULE")" && pwd)"
APP_MODULE="$(basename "$ABS_MODULE" .py)"
BASE="http://127.0.0.1:${PORT}"

WORK="$(mktemp -d)"
LOG="$WORK/server.log"

# Launch the server with its cwd in a throwaway dir so any local state
# (e.g. a SQLite file) lands there and is cleaned up.
( cd "$WORK" && exec uv run --with fastapi --with uvicorn \
    uvicorn "${APP_MODULE}:app" --app-dir "$APP_DIR" --port "$PORT" \
    >"$LOG" 2>&1 ) &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null; rm -rf "$WORK"' EXIT

# Readiness: independent of the routes under test (FastAPI always serves
# /openapi.json), so a broken endpoint shows up as a FAIL, not a timeout.
ready=""
for _ in $(seq 1 60); do
  code="$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/openapi.json")"
  [ "$code" != "000" ] && { ready=1; break; }
  sleep 0.5
done
if [ -z "$ready" ]; then
  echo "FAIL  startup  (server did not become ready)"
  cat "$LOG"
  exit 1
fi

fails=0
check() {  # label expected actual
  if [ "$2" = "$3" ]; then
    echo "PASS  $1  (HTTP $3)"
  else
    echo "FAIL  $1  (expected $2, got $3)"
    fails=$((fails + 1))
  fi
}
req() {  # METHOD PATH [JSON_BODY]
  if [ -n "${3:-}" ]; then
    curl -s -w '\n%{http_code}' -X "$1" "${BASE}${2}" \
      -H 'Content-Type: application/json' -d "$3"
  else
    curl -s -w '\n%{http_code}' -X "$1" "${BASE}${2}"
  fi
}
status_of() { printf '%s\n' "$1" | tail -n1; }
body_of()   { printf '%s\n' "$1" | sed '$d'; }

resp="$(req POST "$RESOURCE" '{"title":"smoke","body":"hello"}')"
check "POST   ${RESOURCE}" 201 "$(status_of "$resp")"
id="$(body_of "$resp" | grep -oE '"id"[: ]*[0-9]+' | grep -oE '[0-9]+' | head -1)"
id="${id:-1}"

check "GET    ${RESOURCE}" 200 "$(status_of "$(req GET "$RESOURCE")")"
check "GET    ${RESOURCE}/{id}" 200 "$(status_of "$(req GET "${RESOURCE}/${id}")")"
check "PATCH  ${RESOURCE}/{id}" 200 "$(status_of "$(req PATCH "${RESOURCE}/${id}" '{"title":"smoke-2"}')")"
check "DELETE ${RESOURCE}/{id}" 204 "$(status_of "$(req DELETE "${RESOURCE}/${id}")")"
check "GET    ${RESOURCE}/999" 404 "$(status_of "$(req GET "${RESOURCE}/999")")"

echo
if [ "$fails" -eq 0 ]; then
  echo "ALL PASS"
  exit 0
else
  echo "${fails} FAILED"
  exit 1
fi
