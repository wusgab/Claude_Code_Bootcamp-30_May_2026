# Bug-fix notes — Notes API (module-04/winner)

Findings from review, ranked by practical severity. Each item has the smallest
fix. Status: none applied yet unless marked **[done]**.

## App bugs (notes.py)

### 1. Unescaped LIKE metacharacters in search — `notes.py:119`
**Not** a SQL injection (the query is parameterized; no SQL can be injected).
It is a search-correctness bug: user input flows into a `LIKE` pattern without
escaping `%` and `_`, so those are treated as wildcards.

Demonstrated behavior:
- `q=%`      → returns **every** note instead of notes containing a percent sign.
- `q=100%`   → cannot filter for the literal `%`.
- `q=created_at` → also matches `createdXat`, `created9at`, … (false positives).

Impact: correctness defect; mild perf nuisance (forces table scan). No auth
impact here — the app has no per-user scoping, so `%` reveals nothing the caller
couldn't already get from `GET /notes`.

Smallest fix: escape `\ % _` in `q` and add `ESCAPE '\'` to both LIKE clauses.

```python
esc = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
like = f"%{esc}%"
# WHERE title LIKE ? ESCAPE '\' OR body LIKE ? ESCAPE '\'
```

### 2. `PATCH {}` is an accepted no-op that still bumps `updated_at`
An empty patch body returns 200 and rewrites the row (touching `updated_at`)
without changing any field. Arguably should be a no-op or a 422.
Smallest fix: if `patch.title is None and patch.body is None`, return the row
unchanged without an UPDATE (or reject with 422). Behavior decision — left open.

### 3. SQLite write contention under the threadpool (low)
Sync `def` handlers run in Starlette's threadpool; concurrent writes via separate
connections can hit `database is locked` (waits up to the 5s default, then errors).
Fine at exercise scale.
Smallest fix: pass `sqlite3.connect(DB_PATH, timeout=…)` and/or serialize writes;
only if it's ever load-tested.

## Test/config debt (my own diff)

### M1. Test deps undeclared — suite unrunnable from a clean install
`test_notes.py` needs `pytest` + `httpx`, neither in `requirements.txt`.
Smallest fix: add `requirements-dev.txt` (pytest, httpx) + a README line.

### M2. Fixture mutates global `notes.DB_PATH` without restoring it
`client` fixture sets `notes.DB_PATH` and never restores it; leaky global state
that could pollute future non-fixture tests.
Smallest fix: save/restore the original (or use monkeypatch).

### L. Minor
- `test_patch_empty_body_is_accepted` pins the questionable item #2 behavior —
  rename/comment so a future change reads as intentional, not a regression.
- `.gitignore` is currently inert (this is not a git repo yet).
- `scoring.md` hard-codes "13 cases" — drop the number to avoid doc staleness.
- Suite would fail under `filterwarnings = error` (httpx StarletteDeprecationWarning).

## Priority
1. **#1** search escaping (correctness, user-visible)
2. **M1** test deps (reproducibility)
3. **M2** fixture global restore
4. Everything else: opportunistic.
