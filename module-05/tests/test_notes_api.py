"""End-to-end tests for the Notes API (module-04/winner/notes.py).

Coverage: create, list, search, get-one, update, delete, 404, 422.

Every test runs against an in-process ASGI app over httpx with a fresh
SQLite database (see conftest.py). No sockets are opened and no HTTP layer
is mocked.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.anyio


async def _create(client, title="Title", body="Body"):
    """Helper: create a note and return the parsed JSON payload."""
    resp = await client.post("/notes", json={"title": title, "body": body})
    assert resp.status_code == 201, resp.text
    return resp.json()


# ----- create ---------------------------------------------------------------


async def test_create_returns_201_with_full_note(client):
    resp = await client.post("/notes", json={"title": "Groceries", "body": "Milk"})

    assert resp.status_code == 201
    note = resp.json()
    assert note["id"] >= 1
    assert note["title"] == "Groceries"
    assert note["body"] == "Milk"
    # Timestamps are set on create and equal at this point.
    assert note["created_at"]
    assert note["created_at"] == note["updated_at"]


async def test_create_autoincrements_ids(client):
    first = await _create(client, title="One")
    second = await _create(client, title="Two")
    assert second["id"] == first["id"] + 1


# ----- list -----------------------------------------------------------------


async def test_list_empty_returns_empty_array(client):
    resp = await client.get("/notes")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_returns_all_notes_ordered_by_id(client):
    await _create(client, title="Alpha")
    await _create(client, title="Beta")
    await _create(client, title="Gamma")

    resp = await client.get("/notes")
    assert resp.status_code == 200
    titles = [n["title"] for n in resp.json()]
    assert titles == ["Alpha", "Beta", "Gamma"]


# ----- search ---------------------------------------------------------------


async def test_search_matches_title_and_body(client):
    await _create(client, title="Shopping ideas", body="buy milk")
    await _create(client, title="Daily log", body="go Shopping later")
    await _create(client, title="Random", body="nothing relevant here")

    # LIKE is case-insensitive for ASCII, so "shopping" matches both the
    # title of note 1 and the body of note 2.
    resp = await client.get("/notes", params={"q": "shopping"})
    assert resp.status_code == 200
    titles = {n["title"] for n in resp.json()}
    assert titles == {"Shopping ideas", "Daily log"}


async def test_search_no_match_returns_empty(client):
    await _create(client, title="Hello", body="World")
    resp = await client.get("/notes", params={"q": "zzz-no-match"})
    assert resp.status_code == 200
    assert resp.json() == []


# ----- get-one --------------------------------------------------------------


async def test_get_one_returns_the_note(client):
    created = await _create(client, title="Find me", body="here")

    resp = await client.get(f"/notes/{created['id']}")
    assert resp.status_code == 200
    assert resp.json() == created


# ----- update ---------------------------------------------------------------


async def test_update_changes_only_provided_fields(client):
    created = await _create(client, title="Old title", body="Old body")

    resp = await client.patch(f"/notes/{created['id']}", json={"title": "New title"})
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["title"] == "New title"
    assert updated["body"] == "Old body"  # untouched
    assert updated["id"] == created["id"]
    assert updated["created_at"] == created["created_at"]


async def test_update_persists(client):
    created = await _create(client, title="t", body="b")
    await client.patch(f"/notes/{created['id']}", json={"body": "changed body"})

    resp = await client.get(f"/notes/{created['id']}")
    assert resp.json()["body"] == "changed body"


# ----- delete ---------------------------------------------------------------


async def test_delete_returns_204_then_note_is_gone(client):
    created = await _create(client, title="Delete me")

    resp = await client.delete(f"/notes/{created['id']}")
    assert resp.status_code == 204
    assert resp.content == b""

    follow_up = await client.get(f"/notes/{created['id']}")
    assert follow_up.status_code == 404


# ----- 404 ------------------------------------------------------------------


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
async def test_missing_note_returns_404(client, method):
    if method == "get":
        resp = await client.get("/notes/9999")
    elif method == "patch":
        resp = await client.patch("/notes/9999", json={"title": "x"})
    else:
        resp = await client.delete("/notes/9999")

    assert resp.status_code == 404
    assert resp.json() == {"error": "not found"}


# ----- 422 ------------------------------------------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        {},                                  # both fields missing
        {"title": "only title"},             # body missing
        {"body": "only body"},               # title missing
        {"title": "", "body": "ok"},         # title violates min_length=1
        {"title": "ok", "body": ""},         # body violates min_length=1
    ],
)
async def test_create_invalid_body_returns_422(client, payload):
    resp = await client.post("/notes", json=payload)
    assert resp.status_code == 422
    assert resp.json() == {"error": "invalid body"}


async def test_update_empty_field_returns_422(client):
    created = await _create(client, title="t", body="b")
    resp = await client.patch(f"/notes/{created['id']}", json={"title": ""})
    assert resp.status_code == 422
    assert resp.json() == {"error": "invalid body"}


async def test_non_integer_id_returns_422(client):
    resp = await client.get("/notes/not-an-int")
    assert resp.status_code == 422
    assert resp.json() == {"error": "invalid body"}
