# Bug-Fix Notes — Two Seeded Bugs (Notes API)

Exercise: plant two bugs into `module-04/winner/notes.py`, watch the suite in
`tests/` catch them, fix them, and document each **symptom → cause → diagnosis →
fix** end-to-end. Both bugs target a known Claude blind spot (error paths,
null/type assumptions). Final state: bugs fixed, suite green (20 passed).

Run: `pytest -q` (from `module-05/`, against the `module-04/winner` venv).

---

## Bug 1 — DELETE of a missing id returns 204 instead of 404  *(error path)*

**Symptom.** `DELETE /notes/9999` (no such note) returns **204 No Content** —
a success — instead of **404** `{"error": "not found"}`. The caller is told a
delete happened that never did.

**Cause.** The handler deleted unconditionally and never checked whether any row
matched:
```python
cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
conn.commit()
return Response(status_code=204)        # always 204
```
`DELETE ... WHERE id = 9999` is perfectly legal SQL that simply affects zero
rows, so nothing raised — the missing-row case has no code path of its own.

**Diagnosis.** Classic **error-path omission**: the happy path was written and
the "it wasn't there" branch silently dropped. `cur.rowcount` already carries the
fact (0 rows deleted); the code just never read it.

**Caught by.** `tests/test_notes_api.py::test_missing_note_returns_404[delete]`
→ `assert 204 == 404` fails. (The `get`/`patch` variants still passed, which
pinpointed delete.)

**Fix.** Re-add the zero-rows guard before reporting success:
```python
if cur.rowcount == 0:
    return not_found()
return Response(status_code=204)
```

---

## Bug 2 — PATCH wipes the field you didn't send  *(null / type assumption)*

**Symptom.** A partial update such as `PATCH /notes/1 {"body": "changed"}`
(title omitted) **500s** with
`sqlite3.IntegrityError: NOT NULL constraint failed: notes.title`. A request that
should leave `title` untouched instead tries to null it out.

**Cause.** The handler assigned the incoming optional fields directly:
```python
title = patch.title       # None when the client omitted "title"
body  = patch.body
conn.execute("UPDATE notes SET title = ?, body = ? ... ", (title, body, ...))
```
`NotePatch` makes both fields `Optional` and defaults them to `None`, so an
*omitted* field is indistinguishable here from "set this to None." The UPDATE
then writes `NULL` into a `NOT NULL` column.

**Diagnosis.** **Hidden assumption that "absent" == "empty/None."** Partial-update
(PATCH) semantics require *missing field → keep current value*; the code treated
missing as a value. The `NOT NULL` schema turned a silent data-wipe into a louder
500 — lucky, but still a real bug, and on a nullable column it would have
destroyed data quietly.

**Caught by.** `tests/test_notes_api.py::test_update_changes_only_provided_fields`
and `::test_update_persists` → both raise `IntegrityError`.

**Fix.** Coalesce against the existing row — only overwrite a field the client
actually sent:
```python
title = patch.title if patch.title is not None else row["title"]
body  = patch.body  if patch.body  is not None else row["body"]
```
(Use `is not None`, not truthiness, so a deliberately different non-empty value
is honored while empty strings are still rejected upstream by `min_length=1`.)

---

## Verification

| State                         | Result                                        |
|-------------------------------|-----------------------------------------------|
| Baseline (no bugs)            | 20 passed                                     |
| Bug 1 planted                 | `test_missing_note_returns_404[delete]` fails |
| Bug 2 planted                 | `test_update_changes_only_provided_fields`, `test_update_persists` fail |
| Both fixed                    | **20 passed**                                 |

Both seeded bugs are exactly the kinds an AI-generated handler hides: the success
path looks right, and the failure/edge branch is missing or makes a quiet
assumption about a value that isn't there. See `code-review-rubric.md` checks
#2 (error paths) and #3/#4 (null & type assumptions).
