import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict


DB_PATH = Path("notes.db")

app = FastAPI()


class Note(BaseModel):
    id: int
    title: str
    body: str
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class NoteCreate(BaseModel):
    title: str
    body: str


class NoteUpdate(BaseModel):
    title: str | None = None
    body: str | None = None


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)


@app.on_event("startup")
def startup():
    init_db()


@app.post("/notes", status_code=201)
def create_note(payload: NoteCreate) -> Note:
    now = now_iso()
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (title, body, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (payload.title, payload.body, now, now),
        )
        conn.commit()
        note_id = cursor.lastrowid

    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()

    return Note(**row_to_dict(row))


@app.get("/notes")
def list_notes(q: str | None = Query(None)) -> list[Note]:
    with get_db() as conn:
        if q:
            rows = conn.execute(
                "SELECT * FROM notes WHERE title LIKE ? OR body LIKE ? ORDER BY created_at DESC",
                (f"%{q}%", f"%{q}%"),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM notes ORDER BY created_at DESC"
            ).fetchall()

    return [Note(**row_to_dict(row)) for row in rows]


@app.get("/notes/{note_id}")
def get_note(note_id: int) -> Note:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="not found")

    return Note(**row_to_dict(row))


@app.put("/notes/{note_id}")
def update_note(note_id: int, payload: NoteUpdate) -> Note:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="not found")

    now = now_iso()
    title = payload.title if payload.title is not None else row["title"]
    body = payload.body if payload.body is not None else row["body"]

    with get_db() as conn:
        conn.execute(
            "UPDATE notes SET title = ?, body = ?, updated_at = ? WHERE id = ?",
            (title, body, now, note_id),
        )
        conn.commit()

    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()

    return Note(**row_to_dict(row))


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="not found")

    with get_db() as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
