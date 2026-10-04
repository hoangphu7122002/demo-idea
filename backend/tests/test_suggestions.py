from typing import Any

from fastapi.testclient import TestClient

from app.core.db import SyncSessionLocal
from app.models import Suggestion
from app.seeds.post import SLUG, SOURCE, seed_post

URL = f"/api/posts/{SLUG}/suggestions"


def _seed() -> None:
    with SyncSessionLocal() as s:
        seed_post(s)


def _payload(**kw: Any) -> dict[str, Any]:
    start = SOURCE.index("exactly 3 nodes")
    base: dict[str, Any] = {
        "anchor_start": start,
        "anchor_end": start + len("exactly 3 nodes"),
        "original_text": "exactly 3 nodes",
        "replacement": "at least 2f+1 nodes",
        "name": "Lan",
    }
    return base | kw


def test_anonymous_submit_is_pending(client: TestClient) -> None:
    _seed()
    r = client.post(URL, json=_payload())
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "pending"
    assert body["name"] == "Lan"
    assert body["replacement"] == "at least 2f+1 nodes"


def test_empty_replacement_422(client: TestClient) -> None:
    _seed()
    assert client.post(URL, json=_payload(replacement="")).status_code == 422
    assert client.post(URL, json=_payload(replacement="   ")).status_code == 422


def test_paragraph_fallback_anchor(client: TestClient) -> None:
    _seed()
    p = _payload(anchor_start=None, anchor_end=None, paragraph_id="p-3")
    assert client.post(URL, json=p).status_code == 201


def test_missing_anchor_422(client: TestClient) -> None:
    _seed()
    p = _payload(anchor_start=None, anchor_end=None)
    assert client.post(URL, json=p).status_code == 422


def test_name_optional(client: TestClient) -> None:
    _seed()
    r = client.post(URL, json=_payload(name=None))
    assert r.status_code == 201
    assert r.json()["name"] is None


def test_list_filters_by_status(client: TestClient) -> None:
    _seed()
    client.post(URL, json=_payload())
    assert len(client.get(URL).json()) == 1
    assert len(client.get(URL, params={"status": "pending"}).json()) == 1
    assert client.get(URL, params={"status": "filtered"}).json() == []
    assert client.get(URL, params={"status": "bogus"}).status_code == 422


def test_unknown_post_404(client: TestClient) -> None:
    assert client.post("/api/posts/nope/suggestions", json=_payload()).status_code == 404
    assert client.get("/api/posts/nope/suggestions").status_code == 404


def test_half_anchor_span_422(client: TestClient) -> None:
    _seed()
    assert client.post(URL, json=_payload(anchor_end=None)).status_code == 422
    p = _payload(anchor_start=None, paragraph_id="p-1")
    assert client.post(URL, json=p).status_code == 422


def test_honeypot_is_stored(client: TestClient) -> None:
    _seed()
    assert client.post(URL, json=_payload(website="bot")).status_code == 201
    with SyncSessionLocal() as s:
        row = s.query(Suggestion).one()
        assert row.honeypot == "bot"
