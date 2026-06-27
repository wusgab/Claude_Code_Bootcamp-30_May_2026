# Module 8 — Refactoring & Documentation at Scale

## Goal

Refactor a deliberately messy Python module under hard written constraints. Ship `HANDOFF.md` and `ARCHITECTURE.md` from the diff.

## Scenario

You've inherited a 200-line Python module nobody wants to touch. You have 24 minutes. You will write the constraints **first**, run a constrained refactor, and produce two short docs from the diff.

## Starter instructions

1. Read `solution/before/`. The mess is intentional — note what bothers you.
2. Copy `solution/before/` to `module-08/after/`.
3. Create `module-08/constraints.md` and write your constraint list **before** prompting Claude.

## Claude Code prompt to use

```text
CONSTRAINED REFACTOR
You will refactor the module below for readability only.

HARD CONSTRAINTS
- No new files. No new dependencies.
- Public function signatures unchanged. Module-level imports unchanged.
- Behavior on all existing tests must be byte-identical.
- Replace nested conditionals with early returns where it shortens code.
- Rename local variables only when the new name is materially clearer.
- No comments unless they explain a non-obvious *why*.

Output: a unified diff. No prose around it.
```

```text
HANDOFF.md
Generate a one-page HANDOFF.md from the diff below. Sections:
- What changed (3 bullets max)
- Why
- Risk + how to roll back
- Watch-outs for the next engineer (specific, not generic)
Keep under 40 lines.
```

```text
ARCHITECTURE.md
Read the refactored module and produce ARCHITECTURE.md.
- One ASCII diagram (boxes and arrows) of components and data flow.
- A short paragraph per component (purpose, inputs, outputs).
- A "Known limitations" list with at most 5 items.
Keep under 80 lines.
```

## Manual validation steps

```bash
cd module-08/after
python -m pytest    # all tests still green
wc -l ../HANDOFF.md         # ≤ 40
wc -l ../ARCHITECTURE.md    # ≤ 80
```

Diff `module-08/after/` against `solution/before/` and confirm every change is justified by a line in `constraints.md`.

## Expected deliverable

```text
module-08/
├── after/             # refactored source
├── HANDOFF.md
├── ARCHITECTURE.md
└── constraints.md
```

## Definition of done

- [ ] Existing tests still pass on `after/`.
- [ ] `constraints.md` was written before the refactor (commit timestamp confirms).
- [ ] `HANDOFF.md` ≤ 40 lines, all four sections present.
- [ ] `ARCHITECTURE.md` ≤ 80 lines, has a diagram + per-component paragraphs + ≤ 5 limitations.

## Stretch challenge

Run the **unconstrained** refactor first. Save its diff. Compare line counts and "things changed unnecessarily" between the two diffs in `module-08/comparison.md`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Claude rewrites public signatures | Tighten the constraint list; re-prompt. |
| Tests now fail | Reset and re-run with the byte-identical-behavior constraint reinforced. |
| Docs describe the prompt, not the diff | Always paste the **diff** as input, not the prompt. |
| `ARCHITECTURE.md` is 200 lines | Hard cap at 80; trim limitations + paragraphs. |
