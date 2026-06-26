# _originals/ — reconstructed pre-change versions

**Honest provenance:** no backup was taken before the edits this session, and the
working tree is not a git repo. These files were **reconstructed from the session
transcript**, not copied from a pristine on-disk source. For each file below I
either wrote the original myself or read it in full earlier this session, so the
content here is exact — but it is a reconstruction, so verify before relying on it.

| Backup file | Restores | Original location | Type of change | Confidence |
|---|---|---|---|---|
| `bug-fix-notes.ORIGINAL.md` | first version (review-findings list) | `module-05/bug-fix-notes.md` | overwritten (Write) | exact — I authored it |
| `conftest.ORIGINAL.py` | pre-edit conftest (`parents[1]`, root location) | `module-05/conftest.py` → now `module-05/tests/conftest.py` | moved + edited path | exact — read in full |
| `scoring.ORIGINAL-excerpt.md` | the 2 promotion lines pre-append | `module-04/scoring.md` (tail) | edited (block appended) | exact — read the section |

## Files changed but NOT needing a backup
- `module-04/winner/notes.py` — planted 2 bugs then reverted; current on-disk
  content is **byte-for-byte the original** (correct partial-update + delete-404).
  No diff to track.

## Files only moved (content intact, nothing lost)
- `test_notes_api.py`, `requirements-test.txt` → `module-05/tests/` (unmodified)

## Files deleted (regenerable only — no backup needed)
- `notes.db` (verified empty before delete), `__pycache__/`, `.pytest_cache/`
  in both `module-04/winner/` and `module-05/`. All regenerate automatically.

## How to diff later
    diff _originals/bug-fix-notes.ORIGINAL.md  bug-fix-notes.md
    diff _originals/conftest.ORIGINAL.py        tests/conftest.py

## Recommendation
`git init` at the repo root so future changes are tracked and reversible without
manual reconstruction.
