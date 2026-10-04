from app.ai.spam_rules import classify


def test_real_fix_is_ham() -> None:
    assert not classify("at least 2f+1 nodes", "quorum needs a majority", "Lan", None).is_spam


def test_honeypot_is_spam() -> None:
    v = classify("fine text", None, None, "http://x")
    assert v.is_spam and v.reasons == ["honeypot"]


def test_link_is_spam() -> None:
    assert classify("see https://pills.example for cheap deals", None, None, None).is_spam
    assert classify("visit www.best-seo.com buy now", None, None, None).is_spam


def test_keyword_is_spam() -> None:
    assert classify("Buy now, free money casino", None, None, None).is_spam


def test_utils_match() -> None:
    from app.ai.spam_utils import find_keywords, has_link

    assert has_link("see www.x.com") and not has_link("2f+1 nodes")
    assert not has_link("use socket.io")
    assert find_keywords("Free Money") == ["free money"]


def test_legit_text_with_single_signal_is_ham() -> None:
    for text in (
        "cheap leader election",
        "crypto hashes are stable",
        "use socket.io",
        "send via telegram bot API",
        "see https://raft.github.io/raft.pdf",
    ):
        assert not classify(text, None, None, None).is_spam, text


def test_keywords_match_whole_words_only() -> None:
    from app.ai.spam_utils import find_keywords

    assert find_keywords("a cheaper loaner scrypto") == []
    assert find_keywords("CASINO, loan.") == ["casino", "loan"]


def test_seeded_style_spam_still_caught() -> None:
    assert classify("Buy now, free money casino", None, None, None).is_spam
    assert classify("Cheap crypto loan", None, None, None).is_spam
    assert classify("Win at https://spam.xyz casino", None, None, None).is_spam
