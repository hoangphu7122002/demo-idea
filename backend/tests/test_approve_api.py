from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.core.db import SyncSessionLocal
from app.seeds.post import SLUG, SOURCE, seed_post

URL = f"/api/posts/{SLUG}/suggestions"
pytestmark = pytest.mark.db

TARGET = "exactly 3 nodes"


def _seed() -> None:
    with SyncSessionLocal() as s:
        seed_post(s)


def _submit(client: TestClient, **kw: Any) -> int:
    start = SOURCE.index(TARGET)
    body: dict[str, Any] = {
        "anchor_start": start,
        "anchor_end": start + len(TARGET),
        "original_text": TARGET,
        "replacement": "at least 2f+1 nodes",
        "name": "Lan",
    } | kw
    r = client.post(URL, json=body)
    assert r.status_code == 201, r.text
    return int(r.json()["id"])


def test_approve_creates_credited_revision(client: TestClient) -> None:
    _seed()
    sid = _submit(client)
    r = client.post(f"/api/suggestions/{sid}/approve")
    assert r.status_code == 200
    body = r.json()
    assert body["credit_name"] == "Lan"
    assert body["old_text"] == TARGET
    assert body["new_text"] == "at least 2f+1 nodes"
    assert body["suggestion"]["status"] == "approved"
    assert body["revision"]["number"] == 2
    start, end = body["change_start"], body["change_end"]
    post = client.get(f"/api/posts/{SLUG}").json()
    assert "at least 2f+1 nodes" in post["source"] and TARGET not in post["source"]
    assert post["source"][start:end] == "at least 2f+1 nodes"
    assert [rv["number"] for rv in post["revisions"]] == [1, 2]
    assert post["revisions"][1]["credit_name"] == "Lan"
    assert post["revisions"][1]["previous_text"] == TARGET
    assert client.get(URL, params={"status": "pending"}).json() == []
    assert len(client.get(URL, params={"status": "approved"}).json()) == 1


def test_anonymous_credit_is_a_reader(client: TestClient) -> None:
    _seed()
    sid = _submit(client, name=None)
    assert client.post(f"/api/suggestions/{sid}/approve").json()["credit_name"] == "a reader"


def test_replacement_is_mdx_escaped(client: TestClient) -> None:
    _seed()
    sid = _submit(client, replacement="<script>{alert(1)}</script>")
    body = client.post(f"/api/suggestions/{sid}/approve").json()
    assert body["new_text"] == r"\<script\>\{alert(1)\}\</script\>"
    source = client.get(f"/api/posts/{SLUG}").json()["source"]
    assert "<script>" not in source and r"\{alert(1)\}" in source


def test_second_approve_409_and_unknown_404(client: TestClient) -> None:
    _seed()
    sid = _submit(client)
    assert client.post(f"/api/suggestions/{sid}/approve").status_code == 200
    assert client.post(f"/api/suggestions/{sid}/approve").status_code == 409
    assert client.post("/api/suggestions/9999/approve").status_code == 404


def test_offsets_shift_after_earlier_approval(client: TestClient) -> None:
    _seed()
    first = _submit(client, replacement="a much longer replacement for the first span")
    second_text = "split votes rare"
    start = SOURCE.index(second_text)
    second = _submit(
        client,
        anchor_start=start,
        anchor_end=start + len(second_text),
        original_text=second_text,
        replacement="split votes unlikely",
        name="Hana",
    )
    assert client.post(f"/api/suggestions/{first}/approve").status_code == 200
    r = client.post(f"/api/suggestions/{second}/approve")
    assert r.status_code == 200
    source = client.get(f"/api/posts/{SLUG}").json()["source"]
    assert "split votes unlikely" in source and "a much longer replacement" in source
    assert r.json()["revision"]["number"] == 3


def test_stale_anchor_409(client: TestClient) -> None:
    _seed()
    first = _submit(client)
    second = _submit(client, replacement="different")
    assert client.post(f"/api/suggestions/{first}/approve").status_code == 200
    assert client.post(f"/api/suggestions/{second}/approve").status_code == 409


def test_filtered_cannot_be_approved(client: TestClient) -> None:
    _seed()
    sid = _submit(client, replacement="buy now casino", name="x")
    client.post(f"/api/posts/{SLUG}/run-filter")
    assert client.post(f"/api/suggestions/{sid}/approve").status_code == 409
