"""Pattern data and matchers for the rules spam classifier."""

import re

LINK = re.compile(r"https?://|\bwww\.", re.I)  # bare domains (socket.io) are not links
KEYWORDS = (
    "viagra",
    "casino",
    "crypto",
    "bitcoin",
    "free money",
    "click here",
    "buy now",
    "cheap",
    "seo service",
    "backlink",
    "loan",
    "porn",
    "work from home",
    "limited offer",
    "whatsapp",
    "telegram",
)


def has_link(text: str) -> bool:
    return LINK.search(text) is not None


def find_keywords(text: str) -> list[str]:
    """Whole-word, case-insensitive keyword hits (each keyword once)."""
    return [k for k in KEYWORDS if re.search(rf"\b{re.escape(k)}\b", text, re.I)]
