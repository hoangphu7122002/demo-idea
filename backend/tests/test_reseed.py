import time

from fastapi.testclient import TestClient

from app.ai.spam_rules import classify
from app.seeds.post import SLUG, SOURCE
from app.seeds.reseed import reseed
from app.seeds.suggestions import REAL, SPAM


def test_reseed_is_fast_and_repeatable(client: TestClient) -> None:
    t = time.perf_counter()
    assert reseed() == {"posts": 1, "suggestions": 10}
    assert reseed() == {"posts": 1, "suggestions": 10}
    assert time.perf_counter() - t < 10
    assert len(client.get(f"/api/posts/{SLUG}/suggestions").json()) == 10
    assert len(client.get(f"/api/posts/{SLUG}").json()["revisions"]) == 1


def test_seed_originals_exist_in_source() -> None:
    for s in REAL + SPAM:
        assert s.original in SOURCE


def test_rules_split_seeds_7_spam_3_ham_and_lan_is_ham(client: TestClient) -> None:
    reseed()
    r = client.post(f"/api/posts/{SLUG}/run-filter")
    assert r.json() == {"checked": 10, "spam": 7, "ham": 3, "filtered_total": 7}
    assert not classify("at least 2f+1 nodes", None, "Lan", None).is_spam
    pending = client.get(f"/api/posts/{SLUG}/suggestions", params={"status": "pending"}).json()
    assert {p["name"] for p in pending} == {"Minh", "Hana", None}


def test_seeded_spam_caught_by_rules_alone_and_real_fixes_pass() -> None:
    for s in SPAM:
        assert classify(s.replacement, s.reason, s.name, s.honeypot).is_spam, s
    for s in REAL:
        assert not classify(s.replacement, s.reason, s.name, s.honeypot).is_spam, s
