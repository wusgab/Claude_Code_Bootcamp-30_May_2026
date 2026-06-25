# Module 04 — Notes API scoring (side-by-side)

Three candidates, same prompt, Track A (FastAPI + Pydantic v2 + sqlite3), built by different models:
- candidate-a → Opus
- candidate-b → Haiku (recreated after a 404-body fix)
- candidate-c → Sonnet

Manual validation: each candidate started under uvicorn and driven with the supplied curl script.
notes.db is created at startup and preserved for all candidates (never deleted).

## Manual curl results

| Step | Request              | a   | b   | c   | Expected |
|------|----------------------|-----|-----|-----|----------|
| 1    | POST   /notes        | 201 | 201 | 201 | 201      |
| 2    | GET    /notes        | 200 | 200 | 200 | 200      |
| 3    | GET    /notes?q=hi   | 200 | 200 | 200 | 200      |
| 4    | GET    /notes/1      | 200 | 200 | 200 | 200      |
| 5    | PUT    /notes/1      | 200 | 200 | 200 | 200      |
| 6    | DELETE /notes/1      | 204 | 204 | 204 | 204      |
| 7    | GET    /notes/999    | 404 | 404 | 404 | 404      |
|      | 404 body             | {"error":"not found"} | {"error":"not found"} | {"error":"not found"} | {"error":"not found"} |
|      | 422 on invalid body  | 422 | 422 | 422 | 422      |

Note: the update step uses PUT /notes/{id} — the spec's update verb, implemented by all three
candidates. (An earlier draft of the validation script used PATCH, which returned 405 since none
of the candidates expose a PATCH route; corrected to PUT here.)

---

Candidate: a   (model: Opus)
Correctness (0–3): 3 — all five endpoints exercised via curl, 404 = {"error":"not found"}, invalid body → 422, empty title/body rejected (min_length=1).
Simplicity   (0–3): 3 — single file, short handlers, DRY helpers (row_to_note, not_found).
Fit          (0–3): 3 — snake_case, PascalCase models, ISO 8601 UTC, DB init errors surfaced to sys.stderr, deps in requirements.txt, modern lifespan startup.
Total: 9 / 9

Candidate: b   (model: Haiku, recreated)
Correctness (0–3): 3 — all five endpoints work, 404 = {"error":"not found"} (fixed). No empty-string validation (accepts title="").
Simplicity   (0–3): 2 — repetitive: Note(...) hand-built in four handlers, open/close boilerplate everywhere, unused ErrorResponse model.
Fit          (0–3): 2 — conventions mostly followed, but no stderr error surfacing and deprecated @app.on_event("startup").
Total: 7 / 9

Candidate: c   (model: Sonnet)
Correctness (0–3): 3 — all five endpoints exercised via curl, 404 = {"error":"not found"}, invalid body → 422, PUT update → 200.
Simplicity   (0–3): 3 — cleanest structure: contextmanager _db() with commit/rollback, _not_found()/_row_to_dict() helpers, no repetition.
Fit          (0–3): 2 — snake_case, PascalCase models, ISO 8601 UTC, requirements.txt present; but no stderr error surfacing and deprecated @app.on_event("startup").
Total: 8 / 9

---

Ranking: candidate-a (9) > candidate-c (8) > candidate-b (7).
Winner: candidate-a — the only one that surfaces DB init errors to sys.stderr and uses the modern
lifespan startup, which are the two CLAUDE.md/convention points c and b both miss.

Promotion: candidate-a's source files (app.py, requirements.txt, README.md) copied to module-04/winner/.
Excluded from the copy: .venv/ and notes.db (environment/runtime artifacts, not deliverables).

Post-promotion changes (winner/ no longer matches the candidate-a scored above):
- app.py renamed to notes.py (and the run command in README/docstring updated to match).
- Update endpoint refactored from PUT /notes/{id} (full replace via NoteIn) to
  PATCH /notes/{id} (partial update via a new NotePatch model). The curl table above —
  which says the update verb is PUT and "none of the candidates expose a PATCH route" —
  describes the original candidates, not the current winner. See PATCH-0*.png.
- Added test_notes.py (pytest, 13 cases) and a .gitignore for runtime artifacts.
