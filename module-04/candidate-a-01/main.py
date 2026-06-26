"""Notes API — FastAPI + Pydantic v2 + sqlite3 (stdlib).

Single-process. Schema is initialised at startup; no migrations framework.
"""

from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

DB_PATH = "notes.db"


def now_iso() -> str:
    """Current time as ISO 8601 in UTC, e.g. 2026-06-21T04:10:00.123456Z."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                body       TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Notes API", lifespan=lifespan)


class NoteIn(BaseModel):
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)


class Note(BaseModel):
    id: int
    title: str
    body: str
    created_at: str
    updated_at: str


def not_found() -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": "not found"})


@app.post("/notes", status_code=201, response_model=Note)
def create_note(payload: NoteIn) -> Note:
    ts = now_iso()
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO notes (title, body, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (payload.title, payload.body, ts, ts),
        )
        new_id = cur.lastrowid
    return Note(
        id=new_id,
        title=payload.title,
        body=payload.body,
        created_at=ts,
        updated_at=ts,
    )


@app.get("/notes", response_model=list[Note])
def list_notes(q: str | None = Query(default=None)) -> list[Note]:
    with connect() as conn:
        if q:
            like = f"%{q}%"
            rows = conn.execute(
                "SELECT * FROM notes WHERE title LIKE ? OR body LIKE ? ORDER BY id",
                (like, like),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM notes ORDER BY id").fetchall()
    return [Note(**dict(row)) for row in rows]


@app.get("/notes/{note_id}")
def get_note(note_id: int):
    with connect() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if row is None:
        return not_found()
    return Note(**dict(row))


@app.put("/notes/{note_id}")
def update_note(note_id: int, payload: NoteIn):
    ts = now_iso()
    with connect() as conn:
        cur = conn.execute(
            "UPDATE notes SET title = ?, body = ?, updated_at = ? WHERE id = ?",
            (payload.title, payload.body, ts, note_id),
        )
        if cur.rowcount == 0:
            return not_found()
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    return Note(**dict(row))


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    with connect() as conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        if cur.rowcount == 0:
            return not_found()
    return None
