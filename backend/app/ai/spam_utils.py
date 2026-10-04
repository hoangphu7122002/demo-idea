"""Pattern data and matchers for the rules spam classifier."""

import re

LINK = re.compile(r"https?://|www\.|\b[a-z0-9-]+\.(?:com|net|org|io|xyz|ru|top|biz)\b", re.I)
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
    lowered = text.lower()
    return [k for k in KEYWORDS if k in lowered]
