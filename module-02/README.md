# task — CLI Task Manager

A single-file, zero-dependency terminal task manager. State is saved to `./tasks.json` in whatever directory you run the command from.

## Requirements

Python 3.11+

## Install

```bash
# Make executable and drop on your PATH
chmod +x task.py
cp task.py ~/bin/task        # or any directory on $PATH
```

Or run without installing:

```bash
python3 task.py <command> [args]
```

## Commands

| Command | Description | Example |
|---|---|---|
| `task add "<text>"` | Add a new task | `task add "Write the spec"` |
| `task list` | List all tasks | `task list` |
| `task done <id>` | Mark a task as done | `task done 1` |
| `task delete <id>` | Delete a task | `task delete 1` |

## Examples

```
$ task add "Write the spec"
Added task #1: Write the spec

$ task add "Review PR"
Added task #2: Review PR

$ task list
ID  STATUS   CREATED              TEXT
─────────────────────────────────────────────────
1   pending  2024-01-15 09:00 UTC  Write the spec
2   pending  2024-01-15 09:01 UTC  Review PR

$ task done 1
Marked #1 as done

$ task delete 99
No task with id 99          # exits with code 1
```

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | User error (bad id, unknown command, missing argument) |
| `2` | Internal error (unreadable/corrupt `tasks.json`, disk write failure) |
