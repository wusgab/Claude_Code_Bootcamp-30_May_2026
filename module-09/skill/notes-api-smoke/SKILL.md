---
name: notes-api-smoke
description: Boot a single-file FastAPI app and smoke-test its 5 CRUD endpoints plus a 404 case, printing PASS/FAIL per check.
---

## Purpose

Boot a single-file FastAPI application in an ephemeral dependency
environment and assert that its five CRUD endpoints return the expected
status codes, plus one negative case. The skill exercises the *running*
app over HTTP — not its source — so it catches wiring, routing, and
startup failures that unit tests can miss.

## When to use it

- After generating or refactoring a small REST API, to confirm every
  route still boots and answers over HTTP before you trust unit tests.
- In a pull-request or pre-merge check where you want a fast, dependency
  -light contract test without a full test harness.
- When a single-file FastAPI service exposes the standard create / list
  / read / update / delete surface and you need a one-shot "is it
  alive and correct?" probe.
- When you suspect an endpoint returns the wrong status code (e.g. a
  delete that answers `200` instead of `204`, or a missing-resource
  lookup that answers `500` instead of `404`).

## Prompt body

```text
You are running a smoke test against a single-file FastAPI application.

Inputs:
- MODULE_PATH: filesystem path to the .py file that defines `app` (a
  FastAPI instance). Example: ./api/main.py
- PORT: the localhost port to bind. Example: 8011
- RESOURCE: the collection path the API exposes. Default: /notes

The application is assumed to expose this CRUD surface and contract:
  POST   {RESOURCE}            -> 201   (create one resource)
  GET    {RESOURCE}            -> 200   (list resources)
  GET    {RESOURCE}/{id}       -> 200   (read the created resource)
  PATCH  {RESOURCE}/{id}       -> 200   (partial update)
  DELETE {RESOURCE}/{id}       -> 204   (delete the resource)
  GET    {RESOURCE}/999        -> 404   (unknown id -> not found)

Do the following:

1. Derive the import target from MODULE_PATH: app module = the file's
   basename without ".py"; app dir = the file's directory. The ASGI
   target is "<module>:app".

2. Boot the app in the background with an ephemeral, isolated
   dependency environment so nothing needs to be pre-installed:
     uv run --with fastapi --with uvicorn \
       uvicorn "<module>:app" --app-dir "<dir>" --port "$PORT"
   Capture its PID and arrange to kill it on exit (trap).

3. Poll http://127.0.0.1:$PORT{RESOURCE} until it answers or a ~20s
   timeout elapses. If it never answers, print "FAIL  startup" and the
   captured server log, then exit non-zero.

4. Send exactly one HTTP request per check below, capturing both the
   response body and the HTTP status code in a single call. Print one
   line per check in the form:
     PASS  <METHOD PATH>  (HTTP <code>)
     FAIL  <METHOD PATH>  (expected <X>, got <Y>)

   Checks, in order:
     a. POST   {RESOURCE}        with a minimal valid JSON body -> 201.
        Parse the created id from the JSON response.
     b. GET    {RESOURCE}                                        -> 200.
     c. GET    {RESOURCE}/{id}    using the id from (a)          -> 200.
     d. PATCH  {RESOURCE}/{id}    with a minimal valid patch     -> 200.
     e. DELETE {RESOURCE}/{id}                                   -> 204.
     f. GET    {RESOURCE}/999     (an id that should not exist)  -> 404.

5. Tear down the server and exit 0 only if every check passed; exit
   non-zero (and print a one-line summary of how many failed) otherwise.

Do not reference any project-specific paths, file names, or schema
beyond MODULE_PATH, PORT, and RESOURCE. Keep the test self-contained:
plain bash + curl, no extra dependencies installed into the project.
```

## Expected inputs

- **`MODULE_PATH`** — path to the single `.py` file that defines a
  FastAPI `app` object (e.g. `./api/main.py`).
- **`PORT`** — a free localhost port to bind during the test (e.g.
  `8011`).
- **`RESOURCE`** *(optional)* — the collection path under test;
  defaults to `/notes`.
- A working `uv` installation and `curl` on `PATH`. No other
  dependencies need to be pre-installed — `uv run --with …` provisions
  FastAPI and uvicorn in an ephemeral environment.

## Expected outputs

- One `PASS` / `FAIL` line per endpoint check (6 lines), each naming
  the method, path, and observed HTTP status code.
- A final summary line (`ALL PASS`, or `<n> FAILED`).
- Process exit code `0` when all six checks pass, non-zero otherwise —
  suitable for use as a CI gate.
- The launched server is always torn down on exit (success, failure,
  or interrupt).

## Worked example

**Scenario.** A single-file FastAPI notes service lives at
`module-09/notes_api.py`. It defines `app`, persists to a local SQLite
file, and exposes the standard `/notes` CRUD surface. We want to
confirm all five endpoints answer with the right status codes — and
that an unknown id yields `404` — without installing anything into the
project.

**Invocation.** Run this from the repository root (it targets the real
file and binds port `8011`):

```bash
#!/usr/bin/env bash
set -uo pipefail

MODULE="${1:-module-09/notes_api.py}"   # path to the single-file FastAPI app
PORT="${2:-8011}"                   # localhost port to bind
RESOURCE="/notes"

APP_DIR="$(dirname "$MODULE")"
APP_MODULE="$(basename "$MODULE" .py)"
BASE="http://127.0.0.1:${PORT}"
LOG="$(mktemp)"

# 1. Boot the app in an ephemeral dependency env (nothing pre-installed).
uv run --with fastapi --with uvicorn \
  uvicorn "${APP_MODULE}:app" --app-dir "$APP_DIR" --port "$PORT" \
  >"$LOG" 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null' EXIT

# 2. Wait for readiness (~20s max).
for _ in $(seq 1 40); do
  curl -sf "${BASE}${RESOURCE}" >/dev/null 2>&1 && break
  sleep 0.5
done
if ! curl -sf "${BASE}${RESOURCE}" >/dev/null 2>&1; then
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

# One request per check: capture body + trailing status line together.
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

# a. POST /notes -> 201
resp="$(req POST "$RESOURCE" '{"title":"smoke","body":"hello"}')"
check "POST   ${RESOURCE}" 201 "$(status_of "$resp")"
id="$(body_of "$resp" | grep -oE '"id"[: ]*[0-9]+' | grep -oE '[0-9]+' | head -1)"
id="${id:-1}"

# b. GET /notes -> 200
check "GET    ${RESOURCE}" 200 "$(status_of "$(req GET "$RESOURCE")")"

# c. GET /notes/{id} -> 200
check "GET    ${RESOURCE}/{id}" 200 "$(status_of "$(req GET "${RESOURCE}/${id}")")"

# d. PATCH /notes/{id} -> 200
check "PATCH  ${RESOURCE}/{id}" 200 \
  "$(status_of "$(req PATCH "${RESOURCE}/${id}" '{"title":"smoke-2"}')")"

# e. DELETE /notes/{id} -> 204
check "DELETE ${RESOURCE}/{id}" 204 "$(status_of "$(req DELETE "${RESOURCE}/${id}")")"

# f. GET /notes/999 -> 404
check "GET    ${RESOURCE}/999" 404 "$(status_of "$(req GET "${RESOURCE}/999")")"

echo
if [ "$fails" -eq 0 ]; then
  echo "ALL PASS"
else
  echo "${fails} FAILED"
  exit 1
fi
```

**Expected output (excerpt).**

```text
PASS  POST   /notes  (HTTP 201)
PASS  GET    /notes  (HTTP 200)
PASS  GET    /notes/{id}  (HTTP 200)
PASS  PATCH  /notes/{id}  (HTTP 200)
PASS  DELETE /notes/{id}  (HTTP 204)
PASS  GET    /notes/999  (HTTP 404)

ALL PASS
```
