# Notes API Scoring

## Comparison

| Criterion | Candidate A | Candidate B |
|:---|:---:|:---:|
| **Correctness** | **3/3** ✓ | **3/3** ✓ |
| **Simplicity** | **3/3** ✓ | **2/3** |
| **Fit** | **0/3** | **0/3** |
| **TOTAL** | **6/9** 🏆 | **5/9** |

---

## Details

### Correctness (0–3)
**What:** Can I exercise all five endpoints with curl?

**Candidate A: 3/3**
- ✓ POST /notes → 201 (create note)
- ✓ GET /notes → 200 (list all)
- ✓ GET /notes?q=hi → 200 (search)
- ✓ GET /notes/1 → 200 (get one)
- ✓ PUT /notes/1 → 200 (update), 404 (not found)
- ✓ DELETE /notes/1 → 204 (success), 404 (not found)

**Candidate B: 3/3**
- ✓ All same endpoints, same functionality
- ✓ Bonus: supports partial updates (optional fields)

---

### Simplicity (0–3)
**What:** Is the source single-glance readable?

**Candidate A: 3/3** ⭐
- **133 lines** — compact and focused
- Modern async patterns (lifespan context manager)
- Clear helper functions (`now_iso()`, `not_found()`)
- Field() validation is explicit
- No redundant operations
- Easy to scan and understand

**Candidate B: 2/3**
- **162 lines** — 29 lines longer
- Older pattern (@app.on_event instead of lifespan)
- Redundant database operations (3+ per request)
- Repeated existence checks
- ConfigDict adds Pydantic-specific patterns
- Requires careful reading to follow logic

---

### Fit (0–3)
**What:** Does it follow CLAUDE.md conventions?

**Candidate A: 0/3**
- ✗ Uses FastAPI (third-party) — violates "stdlib only"
- ✗ Uses Pydantic (third-party) — violates "stdlib only"
- ✗ File is main.py, not task.py
- ✗ Uses BaseModel, not TypedDict

**Candidate B: 0/3**
- ✗ Uses FastAPI (third-party) — violates "stdlib only"
- ✗ Uses Pydantic (third-party) — violates "stdlib only"
- ✗ Uses uvicorn (third-party) — violates "stdlib only"
- ✗ File is main.py, not task.py
- ✗ Uses BaseModel + ConfigDict, not TypedDict

---

## 🏆 Winner: Candidate A

**Why?** Cleaner implementation with modern patterns. Both equally violate CLAUDE.md's stdlib-only constraint, but Candidate A wins on code quality: 33 fewer lines, modern async patterns, and zero redundancy.
