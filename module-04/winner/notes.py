"""Notes API — FastAPI + Pydantic v2 + sqlite3 (stdlib).

Single process. Schema is initialised at startup; no migrations framework.
Run: python3 notes.py   (or: uvicorn notes:app)
"""

from __future__ import annotations

import sqlite3
import sys
from contextlib import asynccontextmanager, closing
from datetime import datetime, timezone

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

DB_PATH = "notes.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    body       TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def now_iso() -> str:
    """Current time as ISO 8601 in UTC, e.g. 2026-06-22T12:00:00Z."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    try:
        with closing(get_db()) as conn:
            conn.executescript(SCHEMA)
            conn.commit()
    except sqlite3.Error as exc:  # surface as a startup failure
        print(f"error: failed to initialise database: {exc}", file=sys.stderr)
        raise


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Notes API", lifespan=lifespan)


# ----- Schemas --------------------------------------------------------------


class NoteIn(BaseModel):
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)


class NotePatch(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    body: str | None = Field(default=None, min_length=1)


class NoteOut(BaseModel):
    id: int
    title: str
    body: str
    created_at: str
    updated_at: str


# ----- Error handling -------------------------------------------------------


@app.exception_handler(RequestValidationError)
async def on_invalid_body(_: Request, __: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"error": "invalid body"})


def not_found() -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": "not found"})


def row_to_note(row: sqlite3.Row) -> dict:
    return {k: row[k] for k in row.keys()}


# ----- Routes ---------------------------------------------------------------


@app.post("/notes", status_code=201)
def create_note(note: NoteIn) -> NoteOut:
    ts = now_iso()
    with closing(get_db()) as conn:
        cur = conn.execute(
            "INSERT INTO notes (title, body, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (note.title, note.body, ts, ts),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (cur.lastrowid,)).fetchone()
    return NoteOut(**row_to_note(row))


@app.get("/notes")
def list_notes(q: str | None = None) -> list[NoteOut]:
    with closing(get_db()) as conn:
        if q:
            like = f"%{q}%"
            rows = conn.execute(
                "SELECT * FROM notes WHERE title LIKE ? OR body LIKE ? ORDER BY id",
                (like, like),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM notes ORDER BY id").fetchall()
    return [NoteOut(**row_to_note(r)) for r in rows]


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    with closing(get_db()) as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if row is None:
        return not_found()
    return NoteOut(**row_to_note(row))


@app.patch("/notes/{note_id}")
def update_note(note_id: int, patch: NotePatch):
    ts = now_iso()
    with closing(get_db()) as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        if row is None:
            return not_found()
        title = patch.title if patch.title is not None else row["title"]
        body = patch.body if patch.body is not None else row["body"]
        conn.execute(
            "UPDATE notes SET title = ?, body = ?, updated_at = ? WHERE id = ?",
            (title, body, ts, note_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    return NoteOut(**row_to_note(row))


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    with closing(get_db()) as conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
    if cur.rowcount == 0:
        return not_found()
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
