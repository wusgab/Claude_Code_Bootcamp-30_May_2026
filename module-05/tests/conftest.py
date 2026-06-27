"""Shared fixtures for the Notes API test suite.

The app under test lives at module-04/winner/notes.py. We import it in-process
and drive it through httpx's ASGITransport — no network sockets, no HTTP mocking.

Each test gets a fresh, isolated SQLite database created in a pytest tmp_path.
We monkeypatch ``notes.DB_PATH`` (read on every ``get_db()`` call) and call
``init_db()`` ourselves, so the lifespan handler is never needed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make module-04/winner importable as the top-level module ``notes``.
# This file lives at module-05/tests/, so the repo root is parents[2].
WINNER_DIR = Path(__file__).resolve().parents[2] / "module-04" / "winner"
sys.path.insert(0, str(WINNER_DIR))

import notes  # noqa: E402  (import after sys.path tweak)

import httpx  # noqa: E402


@pytest.fixture
def anyio_backend() -> str:
    """Run @pytest.mark.anyio tests on asyncio only (anyio ships this plugin)."""
    return "asyncio"


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Point the app at a brand-new SQLite file and create its schema."""
    db_file = tmp_path / "notes.db"
    monkeypatch.setattr(notes, "DB_PATH", str(db_file))
    notes.init_db()
    return db_file


@pytest.fixture
async def client(temp_db):
    """An httpx AsyncClient wired to the ASGI app, backed by the temp DB."""
    transport = httpx.ASGITransport(app=notes.app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as ac:
        yield ac
