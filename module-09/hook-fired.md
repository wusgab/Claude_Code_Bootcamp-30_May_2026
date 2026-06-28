# Pre-commit hook fired — commit blocked

The `notes-api-smoke` pre-commit hook (declared in
`module-09/.claude/hooks.json`, installed to `.git/hooks/pre-commit`,
runner `module-09/.claude/hooks/notes-api-smoke.sh`) gates any commit
that stages `module-09/notes_api.py`.

## How it was proven

A one-line bug was injected into `notes_api.py` so `GET /notes` returns
`500` instead of `200`:

```python
def list_notes(q: str | None = None) -> list[NoteOut]:
    return JSONResponse(status_code=500, content={"error": "boom"})  # BUG: injected for hook demo
    with closing(get_db()) as conn:
```

Then the buggy file was staged and a commit attempted.

## Actual terminal output (verbatim)

```text
$ git add module-09/notes_api.py
$ git commit -m "feat: tweak notes list endpoint"
pre-commit: notes-api-smoke -> booting module-09/notes_api.py on :8099
PASS  POST   /notes  (HTTP 201)
FAIL  GET    /notes  (expected 200, got 500)
PASS  GET    /notes/{id}  (HTTP 200)
PASS  PATCH  /notes/{id}  (HTTP 200)
PASS  DELETE /notes/{id}  (HTTP 204)
PASS  GET    /notes/999  (HTTP 404)

1 FAILED
pre-commit: notes-api-smoke FAILED — commit blocked.

$ echo $?
1
```

## Confirmation the commit did NOT land

```text
$ git log --oneline -1
2c12077 feat: add module-08 constrained-refactor exercise   # unchanged HEAD
```

`git commit` exited `1`, HEAD did not advance, and the change remained
staged but uncommitted. The bug was reverted afterward, restoring
`GET /notes -> 200` (re-running the runner then yields `ALL PASS`).
