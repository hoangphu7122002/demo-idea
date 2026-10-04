from fastapi.testclient import TestClient

from app.core.db import SyncSessionLocal
from app.seeds.post import SLUG, seed_post


def _seed() -> None:
    with SyncSessionLocal() as s:
        seed_post(s)


def test_get_post_returns_source_and_revisions(client: TestClient) -> None:
    _seed()
    r = client.get(f"/api/posts/{SLUG}")
    assert r.status_code == 200
    body = r.json()
    assert body["slug"] == SLUG
    assert "exactly 3 nodes" in body["source"]
    assert "```python" in body["source"]
    assert "$$" in body["source"]
    assert [rev["number"] for rev in body["revisions"]] == [1]
    assert body["revisions"][0]["credit_name"] is None


def test_seed_is_idempotent(client: TestClient) -> None:
    _seed()
    _seed()
    assert len(client.get(f"/api/posts/{SLUG}").json()["revisions"]) == 1


def test_unknown_post_404(client: TestClient) -> None:
    assert client.get("/api/posts/nope").status_code == 404
