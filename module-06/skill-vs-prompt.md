# Skill vs. Prompt-only — same diff, two methods

Same input both times: the staged `module-05` diff (12 files, +687), branch
`feat/task-validation-cleanup` over base `m06-base`.

- **Prompt-only** = the two ad-hoc prompts in `commits.md` (Take 1) and `pr.md` (Take 2).
- **Skill** = `skills/git-workflow/SKILL.md` run against the same diff (below).

---

## Skill output — Take 1 (commit splitter)

The skill mandates a table and `<type>(<scope>): <summary>` with 1–3 line bodies.

| Subject | Body (why) | Files |
|---|---|---|
| `test(notes-api): add end-to-end regression suite` | Gives the module-04 winner a safety net; makes the seeded-bug exercise observable — a regression flips a specific test red. | `module-05/tests/conftest.py`, `test_notes_api.py`, `requirements-test.txt` |
| `docs(module-05): record two seeded-bug fixes` | Preserves the symptom→cause→fix trail for the DELETE-204 and PATCH-null defects (known LLM blind spots). | `module-05/bug-fix-notes.md`, `bug-fix-notes-06-22-2026.md` |
| `docs(module-05): add AI-code review rubric` | Turns the bug lessons into an 8-check merge gate; keeps the dated draft beside the final. | `module-05/code-review-rubric.md`, `ex5_code-review-rubric-06-22-2026.md` |
| `chore(module-05): snapshot reconstructed originals` | Provenance for pre-VCS edits; `MANIFEST.md` flags reconstruction confidence per file. | `module-05/_originals/*` |
| `docs(module-05): add exercise screenshot` | Grading evidence of the green suite. | `module-05/exercise-05.png` |

Apply: `git reset` then per-row `git add -p` / `git add <paths>`, verify `git log --oneline`.

## Skill output — Take 2 (PR description)

Identical 6-section contract to the prompt-only `pr.md` (Summary · Why · What changed ·
How to test · Risk · Rollback · Reviewer checklist, ≤ 40 lines). The only material
difference is the diff source: the skill says `git diff main..HEAD`, which here would
also pull in the `m06-base` scaffold commit — so for this reconstructed-base exercise
`git diff m06-base..HEAD` is the correct range. Content is otherwise the same as `pr.md`.

---

## Comparison

| Dimension | Prompt-only | Skill (`git-workflow`) |
|---|---|---|
| Splitter format | Prose sections per commit | **Markdown table** `subject \| body \| files` — denser, scannable |
| Subject style | Bare `type:` (`test:`, `docs:`) | `type(scope):` — adds scope (`notes-api`, `module-05`) |
| Body length | 4–6 lines, richer rationale | **1–3 lines**, terser by contract |
| Mechanics | Not specified | Prescribes `git reset` + `git add -p`, `/tmp/diff.patch` |
| PR diff source | `m06-base..HEAD` (chosen by hand) | `git diff main..HEAD` (needs adjusting for our base) |
| PR sections | 6 + checklist (matched the prompt) | 6 + checklist (same contract) |
| Reusability | One-off prompt text | Versioned, project-agnostic, has a worked example |

### Where they converged
Both produced the **same 5-way logical split** and the **same 6-section PR**. The
substance of the review didn't change — the discriminator was *form*, not *decisions*.

### Where the skill won
- **Consistency.** Scope + table + line caps are enforced every run, not retyped.
- **Hand-off.** The worked example and explicit `git reset`/`add -p` steps make it
  runnable by someone who's never seen the prompt.
- **Less drift.** The prompt-only bodies grew long (4–6 lines); the skill's 1–3 line
  cap keeps commit logs skimmable.

### Where the prompt won
- **Richer "why".** The longer prompt-only bodies carried more reasoning (e.g. the full
  absent-vs-None explanation) that the skill's 1–3 line cap trims.
- **Zero setup.** No file to maintain for a true one-off.
- **Base flexibility.** We picked `m06-base..HEAD` directly; the skill's hard-coded
  `main..HEAD` is wrong for this reconstructed-base exercise and needs overriding.

### Takeaway
Use the **skill** for anything recurring or handed off — it standardizes form and
mechanics. Use a **bare prompt** for a genuine one-off, or when the rationale needs
more room than the skill's line caps allow. Neither changed *what* to commit; the
skill changed *how reliably* the output comes out the same way twice.
