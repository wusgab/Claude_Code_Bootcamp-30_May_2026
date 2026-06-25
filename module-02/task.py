#!/usr/bin/env python3
"""Single-file CLI task manager — persists to ./tasks.json."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Literal, TypedDict

TASKS_FILE = "tasks.json"

Status = Literal["pending", "done"]


class Task(TypedDict):
    id: int
    status: Status
    created_at: str
    text: str


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

def load_tasks() -> list[Task]:
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, encoding="utf-8") as f:
            data: object = json.load(f)
        if not isinstance(data, list):
            raise ValueError("root element must be a JSON array")
        return data  # type: ignore[return-value]
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Error reading {TASKS_FILE}: {exc}", file=sys.stderr)
        sys.exit(2)


def save_tasks(tasks: list[Task]) -> None:
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2)
    except OSError as exc:
        print(f"Error writing {TASKS_FILE}: {exc}", file=sys.stderr)
        sys.exit(2)


def next_id(tasks: list[Task]) -> int:
    return max((t["id"] for t in tasks), default=0) + 1


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_add(args: list[str]) -> None:
    if not args:
        print("Usage: task add <text>", file=sys.stderr)
        sys.exit(1)
    text = " ".join(args)
    tasks = load_tasks()
    task: Task = {
        "id": next_id(tasks),
        "status": "pending",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "text": text,
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task #{task['id']}: {text}")


def cmd_list(args: list[str]) -> None:  # noqa: ARG001
    tasks = load_tasks()
    if not tasks:
        print("No tasks.")
        return

    id_w      = max(max(len(str(t["id"])) for t in tasks), 2)
    status_w  = max(max(len(t["status"])   for t in tasks), 6)
    created_w = max(max(len(t["created_at"]) for t in tasks), 7)
    text_w    = max(max(len(t["text"])     for t in tasks), 4)

    sep = "-" * (id_w + 2 + status_w + 2 + created_w + 2 + text_w)
    print(f"{'ID':<{id_w}}  {'STATUS':<{status_w}}  {'CREATED':<{created_w}}  TEXT")
    print(sep)
    for t in tasks:
        print(
            f"{t['id']:<{id_w}}  {t['status']:<{status_w}}  "
            f"{t['created_at']:<{created_w}}  {t['text']}"
        )


def _resolve_id(raw: str) -> int:
    try:
        return int(raw)
    except ValueError:
        print(f"Invalid id: {raw!r} — must be an integer.", file=sys.stderr)
        sys.exit(1)


def cmd_done(args: list[str]) -> None:
    if not args:
        print("Usage: task done <id>", file=sys.stderr)
        sys.exit(1)
    task_id = _resolve_id(args[0])
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = "done"
            save_tasks(tasks)
            print(f"Marked #{task_id} as done")
            return
    print(f"No task with id {task_id}", file=sys.stderr)
    sys.exit(1)


def cmd_delete(args: list[str]) -> None:
    if not args:
        print("Usage: task delete <id>", file=sys.stderr)
        sys.exit(1)
    task_id = _resolve_id(args[0])
    tasks = load_tasks()
    remaining = [t for t in tasks if t["id"] != task_id]
    if len(remaining) == len(tasks):
        print(f"No task with id {task_id}", file=sys.stderr)
        sys.exit(1)
    save_tasks(remaining)
    print(f"Deleted task #{task_id}")


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

COMMANDS: dict[str, object] = {
    "add":    cmd_add,
    "list":   cmd_list,
    "done":   cmd_done,
    "delete": cmd_delete,
}

_CommandFn = type(cmd_add)  # Callable[[list[str]], None]


def main() -> None:
    argv = sys.argv[1:]
    if not argv:
        print("Usage: task <add|list|done|delete> [args]", file=sys.stderr)
        sys.exit(1)

    name = argv[0]
    fn = COMMANDS.get(name)
    if fn is None:
        valid = ", ".join(COMMANDS)
        print(f"Unknown command {name!r}. Valid commands: {valid}.", file=sys.stderr)
        sys.exit(1)

    cast_fn: _CommandFn = fn  # type: ignore[assignment]
    cast_fn(argv[1:])


if __name__ == "__main__":
    main()
