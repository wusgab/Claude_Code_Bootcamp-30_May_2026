"""Endpoint tests for the Notes API.

Each test runs against a fresh temp-file database so they don't touch the
real notes.db. Run: pytest -q
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import notes_api as notes


@pytest.fixture()
def client(tmp_path: Path):
    # Point the app at a throwaway DB; the lifespan handler creates the schema.
    notes.DB_PATH = str(tmp_path / "test_notes.db")
    with TestClient(notes.app) as c:
        yield c


def _make(client: TestClient, title: str = "hi", body: str = "world") -> dict:
    r = client.post("/notes", json={"title": title, "body": body})
    assert r.status_code == 201
    return r.json()


def test_create_returns_201_with_timestamps(client):
    note = _make(client)
    assert note["id"] >= 1
    assert note["title"] == "hi"
    assert note["body"] == "world"
    assert note["created_at"] == note["updated_at"]
    assert note["created_at"].endswith("Z")


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "", "body": "x"},
        {"title": "x", "body": ""},
        {"title": "x"},
        {"body": "x"},
        {},
    ],
)
def test_create_invalid_body_returns_422(client, payload):
    r = client.post("/notes", json=payload)
    assert r.status_code == 422
    assert r.json() == {"error": "invalid body"}


def test_list_and_search(client):
    _make(client, title="grocery list", body="milk")
    _make(client, title="todo", body="buy milk")
    _make(client, title="unrelated", body="nothing")

    assert len(client.get("/notes").json()) == 3

    hits = client.get("/notes", params={"q": "milk"}).json()
    assert {n["title"] for n in hits} == {"grocery list", "todo"}

    assert client.get("/notes", params={"q": "nomatch"}).json() == []


def test_get_one_and_404(client):
    note = _make(client)
    assert client.get(f"/notes/{note['id']}").status_code == 200

    r = client.get("/notes/999")
    assert r.status_code == 404
    assert r.json() == {"error": "not found"}


def test_patch_partial_update(client):
    note = _make(client, title="old", body="old-body")

    r = client.patch(f"/notes/{note['id']}", json={"title": "new"})
    assert r.status_code == 200
    updated = r.json()
    assert updated["title"] == "new"
    assert updated["body"] == "old-body"  # untouched field preserved
    assert updated["created_at"] == note["created_at"]


def test_patch_empty_body_is_accepted(client):
    # Documents current behaviour: an empty patch is a no-op write (200).
    note = _make(client)
    r = client.patch(f"/notes/{note['id']}", json={})
    assert r.status_code == 200
    assert r.json()["title"] == note["title"]


def test_patch_invalid_field_returns_422(client):
    note = _make(client)
    r = client.patch(f"/notes/{note['id']}", json={"title": ""})
    assert r.status_code == 422


def test_patch_missing_returns_404(client):
    r = client.patch("/notes/999", json={"title": "x"})
    assert r.status_code == 404
    assert r.json() == {"error": "not found"}


def test_delete_and_404(client):
    note = _make(client)
    assert client.delete(f"/notes/{note['id']}").status_code == 204
    assert client.get(f"/notes/{note['id']}").status_code == 404

    r = client.delete("/notes/999")
    assert r.status_code == 404
    assert r.json() == {"error": "not found"}
