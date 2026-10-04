from app.ai.spam_rules import classify


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


def test_utils_match() -> None:
    from app.ai.spam_utils import find_keywords, has_link

    assert has_link("see www.x.com") and not has_link("2f+1 nodes")
    assert find_keywords("Free Money") == ["free money"]
