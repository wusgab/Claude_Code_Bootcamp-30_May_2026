"""Notes API — FastAPI + SQLite, no migrations framework."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional

import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

DB_PATH = "notes.db"

_DDL = """
CREATE TABLE IF NOT EXISTS notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT    NOT NULL,
    body       TEXT    NOT NULL DEFAULT '',
    created_at TEXT    NOT NULL,
    updated_at TEXT    NOT NULL
);
"""


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def _db():
    conn = _get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _init_db() -> None:
    with _db() as conn:
        conn.executescript(_DDL)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class NoteCreate(BaseModel):
    title: str
    body: str = ""


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None


class NoteOut(BaseModel):
    id: int
    title: str
    body: str
    created_at: str
    updated_at: str


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="Notes API")


@app.on_event("startup")
def on_startup() -> None:
    _init_db()


# 404 helper — returns exactly {"error": "not found"}
def _not_found() -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": "not found"})


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "body": row["body"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/notes", status_code=201, response_model=NoteOut)
def create_note(payload: NoteCreate):
    now = _now_utc()
    with _db() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (title, body, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (payload.title, payload.body, now, now),
        )
        note_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    return _row_to_dict(row)


@app.get("/notes", status_code=200, response_model=list[NoteOut])
def list_notes(q: Optional[str] = Query(default=None)):
    with _db() as conn:
        if q:
            pattern = f"%{q}%"
            rows = conn.execute(
                "SELECT * FROM notes WHERE title LIKE ? OR body LIKE ? ORDER BY id",
                (pattern, pattern),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM notes ORDER BY id").fetchall()
    return [_row_to_dict(r) for r in rows]


@app.get("/notes/{note_id}", status_code=200, response_model=NoteOut)
def get_note(note_id: int):
    with _db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if row is None:
        return _not_found()
    return _row_to_dict(row)


@app.put("/notes/{note_id}", status_code=200, response_model=NoteOut)
def update_note(note_id: int, payload: NoteUpdate):
    with _db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        if row is None:
            return _not_found()
        title = payload.title if payload.title is not None else row["title"]
        body = payload.body if payload.body is not None else row["body"]
        now = _now_utc()
        conn.execute(
            "UPDATE notes SET title = ?, body = ?, updated_at = ? WHERE id = ?",
            (title, body, now, note_id),
        )
        updated = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
    return _row_to_dict(updated)


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    with _db() as conn:
        row = conn.execute("SELECT id FROM notes WHERE id = ?", (note_id,)).fetchone()
        if row is None:
            return _not_found()
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    return None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
