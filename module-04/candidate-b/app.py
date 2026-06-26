import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional


# Pydantic models
class NoteCreate(BaseModel):
    title: str
    body: str


class Note(BaseModel):
    id: int
    title: str
    body: str
    created_at: str
    updated_at: str


class ErrorResponse(BaseModel):
    error: str


# Initialize FastAPI app
app = FastAPI(title="Notes API")

# Database path
DB_PATH = Path("notes.db")


def get_db_connection():
    """Get a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database schema if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
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
    conn.close()


def get_utc_timestamp() -> str:
    """Get current timestamp in ISO 8601 UTC format."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    init_db()


@app.post("/notes", status_code=201, response_model=Note)
def create_note(note: NoteCreate) -> Note:
    """Create a new note."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = get_utc_timestamp()

    cursor.execute(
        "INSERT INTO notes (title, body, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (note.title, note.body, now, now)
    )
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()

    return Note(
        id=note_id,
        title=note.title,
        body=note.body,
        created_at=now,
        updated_at=now
    )


@app.get("/notes", response_model=list[Note])
def list_notes(q: Optional[str] = Query(None)) -> list[Note]:
    """List all notes, optionally filtered by search query."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if q:
        # Search in title and body
        query = "SELECT * FROM notes WHERE title LIKE ? OR body LIKE ?"
        search_pattern = f"%{q}%"
        cursor.execute(query, (search_pattern, search_pattern))
    else:
        cursor.execute("SELECT * FROM notes")

    rows = cursor.fetchall()
    conn.close()

    notes = [
        Note(
            id=row["id"],
            title=row["title"],
            body=row["body"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
        for row in rows
    ]
    return notes


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int) -> Note:
    """Get a note by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return JSONResponse(status_code=404, content={"error": "not found"})

    return Note(
        id=row["id"],
        title=row["title"],
        body=row["body"],
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )


@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note: NoteCreate) -> Note:
    """Update a note by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return JSONResponse(status_code=404, content={"error": "not found"})

    now = get_utc_timestamp()
    cursor.execute(
        "UPDATE notes SET title = ?, body = ?, updated_at = ? WHERE id = ?",
        (note.title, note.body, now, note_id)
    )
    conn.commit()
    conn.close()

    return Note(
        id=note_id,
        title=note.title,
        body=note.body,
        created_at=row["created_at"],
        updated_at=now
    )


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    """Delete a note by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return JSONResponse(status_code=404, content={"error": "not found"})

    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()

    return None
