# `notes-api-smoke` invocation

- **Skill:** `module-09/skill/notes-api-smoke/SKILL.md`
- **Target:** `module-09/notes_api.py` (FastAPI app `notes_api:app`)
- **Port:** `8099`
- **Date:** 2026-06-28
- **Boot:** `uv run --with fastapi --with uvicorn uvicorn notes_api:app --app-dir module-09 --port 8099`
- **Environment note:** `uv` 0.11.25 was installed first; FastAPI and uvicorn
  were provisioned ephemerally by `uv run --with …` (nothing added to the project).

## Actual output

```text
PASS  POST   /notes  (HTTP 201)
PASS  GET    /notes  (HTTP 200)
PASS  GET    /notes/{id}  (HTTP 200)
PASS  PATCH  /notes/{id}  (HTTP 200)
PASS  DELETE /notes/{id}  (HTTP 204)
PASS  GET    /notes/999  (HTTP 404)

ALL PASS
```

Result: **6/6 checks passed**, process exit code `0`.
