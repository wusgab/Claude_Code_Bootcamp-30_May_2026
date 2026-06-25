# CLAUDE.md

## Stack
- Python 3.11, standard library only — no third-party packages.
- State persists to `./tasks.json` (JSON array) in the process working directory.
- Lint: `ruff`. Format: `black`. Tests: `pytest`.

## Conventions
- One script: `task.py`. No submodules unless the file grows past 300 lines.
- snake_case for functions and variables; PascalCase for `TypedDict` classes only.
- Every command function is named `cmd_<verb>` and accepts `list[str]` as its sole argument.
- Use `TypedDict` for structured data — not bare dicts, not dataclasses.
- Print errors to `sys.stderr`; never mix errors into `stdout`.
- All user-visible strings in English.

## Commands
- Run:   `python3 task.py <add|list|done|delete> [args]`
- Lint:  `ruff check . && black --check .`
- Fix:   `ruff check . --fix && black .`
- Test:  `pytest -q`

## Do-not
- Do NOT add any third-party dependency — stdlib only; ask before adding anything.
- Do NOT swallow exceptions; surface them as exit-code-2 messages to stderr.
- Do NOT write to `tasks.json` except through `save_tasks()`.
- Do NOT add background processes, threads, or network calls.
- Do NOT create extra files (config, lock, cache) beyond `task.py` and `tasks.json`.

## Glossary
- **task**: A `Task` TypedDict — `{id: int, status: Status, created_at: str, text: str}`.
- **Status**: `Literal["pending", "done"]` — the only two valid task states.
- **exit 1**: user error — bad id, unknown command, or missing argument.
- **exit 2**: internal error — corrupt `tasks.json` or disk write failure.
- **GCOE**: Goal · Constraints · Output format · Examples — the prompt structure taught in Module 2.
