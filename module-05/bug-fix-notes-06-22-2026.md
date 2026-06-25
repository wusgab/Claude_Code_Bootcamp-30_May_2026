# Bug-Fix Notes — Notes API Test Suite

Self-review of the test PR (`conftest.py`, `test_notes_api.py`, `requirements-test.txt`).
The suite is green, so there are no test-breaking defects — but green test code can
still give false confidence, be flaky under change, or miss the cases where the *app*
most plausibly hides bugs. Items are ranked by severity, each with the smallest fix.

---

## HIGH

### H1 — Production startup path (`lifespan` → `init_db`) is never exercised
httpx's `ASGITransport` does not run ASGI lifespan events, and the fixtures call
`notes.init_db()` by hand. If someone removes `lifespan=lifespan` from the
`FastAPI(...)` constructor or breaks the wiring, **every test still passes** while
the real server 500s on first request (no `notes` table). Highest false-green risk.
- **Fix:** add one test driving the app through `fastapi.testclient.TestClient` as a
  context manager (it runs lifespan, uses httpx underneath) against a monkeypatched
  temp `DB_PATH`, asserting `GET /notes` → 200.

---

## MEDIUM

### M1 — `updated_at` is never asserted to change on update
The only timestamp check is `created_at == updated_at` at create; the update test
only asserts `created_at` is *preserved*. An app bug that fails to bump `updated_at`
(or copies `created_at`) passes the suite. (Avoided `!=` because `now_iso()` is
seconds-resolution and would be flaky — correct instinct, but left the field untested.)
- **Fix:** assert `updated["updated_at"] >= created["updated_at"]` (ISO-8601 strings
  sort lexicographically) — monotonic, non-flaky, catches a copied/static value.

### M2 — Search edge cases most likely to hide app bugs are untested
`q` is interpolated into `LIKE '%...%'`, so `q="%"` / `q="_"` are live wildcard
injections, and `if q:` makes `q=""` falsy → returns *all* notes, not none.
None covered, and these are exactly where a stranger's API tends to be wrong.
- **Fix:** assert `q=""` returns all notes; add a case locking the `q="%"` wildcard
  behavior so a future escaping fix is a deliberate, visible change.

### M3 — Test deps installed into the app-under-test's venv
`pytest`/`httpx` were `pip install`ed into `module-04/winner/.venv`, and
`requirements-test.txt` lists only test deps with no link to the app's runtime deps.
So (a) the production venv now carries test-only packages, and (b) a fresh checkout
installing only `requirements-test.txt` can't import `notes` — the suite isn't
reproducible from its own manifest.
- **Fix:** add `-r ../module-04/winner/requirements.txt` to the top of
  `requirements-test.txt` (or document the dependency + use a module-05-local venv).

---

## LOW

### L1 — `9999` magic id and `+1` autoincrement assumptions are brittle
`test_missing_note_returns_404` hard-codes `9999` (safe only on a fresh DB);
`test_create_autoincrements_ids` asserts strictly `second == first + 1`
(assumes start-at-1, no reuse). Couples tests to incidental DB behavior.
- **Fix:** derive the missing id from a created note (`created["id"] + 1`) and
  assert `second["id"] > first["id"]` instead of exact `+1`.

### L2 — `sys.path.insert(0, ...)` + importing generic top-level `notes`
Inserting the winner dir at the front of `sys.path` and importing the unqualified
name `notes` risks collision with any other `notes` module and pulls from a dir that
also holds `notes.db`/`__pycache__`. Works now; fragile as the test tree grows.
- **Fix:** `append` rather than `insert(0)` so local modules win — or load via
  `importlib` from the explicit file path; keep the one-line intent comment.

### L3 — No coverage of negative/zero ids or wrong HTTP methods
`/notes/-1`, `/notes/0`, `POST /notes/{id}` are untested; int coercion accepts
negatives and they currently 404, but it's unasserted.
- **Fix:** one parametrized assertion that `/notes/0` and `/notes/-1` return 404.

---

## Suggested order
1. **H1** — fix before merge (false-green risk).
2. **M1, M2** — close the gaps where the app most plausibly hides bugs.
3. **M3** — reproducibility hygiene, cheap now.
4. **L1–L3** — opportunistic, low effort.
