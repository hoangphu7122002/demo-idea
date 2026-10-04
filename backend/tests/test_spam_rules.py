from typing import Any

from fastapi.testclient import TestClient

from app.ai.spam_rules import classify
from app.core.db import SyncSessionLocal
from app.seeds.post import SLUG, seed_post

URL = f"/api/posts/{SLUG}/suggestions"


def test_real_fix_is_ham() -> None:
    assert not classify("at least 2f+1 nodes", "quorum needs a majority", "Lan", None).is_spam


def test_honeypot_is_spam() -> None:
    v = classify("fine text", None, None, "http://x")
    assert v.is_spam and v.reasons == ["honeypot"]


def test_link_is_spam() -> None:
    assert classify("see https://cheap-pills.example", None, None, None).is_spam
    assert classify("visit best-seo.com now", None, None, None).is_spam


def test_keyword_is_spam() -> None:
    assert classify("Buy now, free money casino", None, None, None).is_spam


def _payload(**kw: Any) -> dict[str, Any]:
    return {
        "anchor_start": 1,
        "anchor_end": 5,
        "original_text": "abcd",
        "replacement": "at least 2f+1 nodes",
    } | kw


def test_run_filter_moves_spam_and_returns_counts(client: TestClient) -> None:
    with SyncSessionLocal() as s:
        seed_post(s)
    client.post(URL, json=_payload())
    client.post(URL, json=_payload(replacement="Win free money at casino"))
    client.post(URL, json=_payload(website="bot"))
    client.post(URL, json=_payload(replacement="go to http://spam.xyz"))
    r = client.post(f"/api/posts/{SLUG}/run-filter")
    assert r.status_code == 200
    assert r.json() == {"checked": 4, "spam": 3, "ham": 1, "filtered_total": 3}
    assert len(client.get(URL, params={"status": "pending"}).json()) == 1
    filtered = client.get(URL, params={"status": "filtered"}).json()
    assert len(filtered) == 3 and all(f["spam_score"] >= 0.5 for f in filtered)
    again = client.post(f"/api/posts/{SLUG}/run-filter").json()
    assert again == {"checked": 1, "spam": 0, "ham": 1, "filtered_total": 3}


def test_run_filter_unknown_post(client: TestClient) -> None:
    assert client.post("/api/posts/nope/run-filter").status_code == 404
