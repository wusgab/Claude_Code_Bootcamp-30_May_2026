# MCP run — scoped single action

- **Task:** Open one GitHub issue reporting the `notes-api-smoke` result for this run.
- **Server:** GitHub MCP server (`create_issue` tool).
- **Scope:** ONE repository only — `wusgab/Claude_Code_Bootcamp-30_May_2026`.
- **Allowed action:** Open exactly one issue. No edits, comments, labels, or further calls.
- **Stop condition:** Stop immediately after one issue is created (or, if no GitHub MCP server is configured, after recording the single call that would be made).

---

## Result — DRY RUN (no GitHub MCP server configured)

`claude mcp list` shows only Google Drive, Gmail, and Google Calendar
(all unauthenticated). No GitHub MCP server is available, so no issue
was created. Per the stop condition, exactly one call would be made:

**Tool call that WOULD be made:**

```json
{
  "tool": "mcp__github__create_issue",
  "arguments": {
    "owner": "wusgab",
    "repo": "Claude_Code_Bootcamp-30_May_2026",
    "title": "notes-api-smoke: PASS on 2026-06-28",
    "body": "PASS  POST   /notes  (HTTP 201)\nPASS  GET    /notes  (HTTP 200)\nPASS  GET    /notes/{id}  (HTTP 200)\nPASS  PATCH  /notes/{id}  (HTTP 200)\nPASS  DELETE /notes/{id}  (HTTP 204)\nPASS  GET    /notes/999  (HTTP 404)\n\nALL PASS"
  }
}
```

**Rendered issue body:**

```text
PASS  POST   /notes  (HTTP 201)
PASS  GET    /notes  (HTTP 200)
PASS  GET    /notes/{id}  (HTTP 200)
PASS  PATCH  /notes/{id}  (HTTP 200)
PASS  DELETE /notes/{id}  (HTTP 204)
PASS  GET    /notes/999  (HTTP 404)

ALL PASS
```

- Skill exit code: `0` (PASS) → title uses `PASS`.
- Source command: `bash module-09/.claude/hooks/notes-api-smoke.sh module-09/notes_api.py 8099`
- Run date: 2026-06-28

> To execute for real: configure a GitHub MCP server (e.g.
> `claude mcp add github -- <github-mcp-server cmd>` with a token scoped
> to `issues:write` on this one repo), then re-run. Scope and stop
> condition above still bound it to a single `create_issue` call.
