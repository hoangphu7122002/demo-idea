"""Rules-first spam classifier: honeypot, links, keywords. Pure, no I/O."""

import re
from dataclasses import dataclass, field

SPAM_THRESHOLD = 0.5
_LINK = re.compile(r"https?://|www\.|\b[a-z0-9-]+\.(?:com|net|org|io|xyz|ru|top|biz)\b", re.I)
_KEYWORDS = (
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


@dataclass(frozen=True)
class Verdict:
    is_spam: bool
    score: float
    reasons: list[str] = field(default_factory=list)


def classify(
    replacement: str, reason: str | None, name: str | None, honeypot: str | None
) -> Verdict:
    """Score a suggestion in [0, 1]; spam when score >= SPAM_THRESHOLD."""
    reasons: list[str] = []
    score = 0.0
    if honeypot:
        return Verdict(True, 1.0, ["honeypot"])
    text = " ".join(t for t in (replacement, reason, name) if t)
    if _LINK.search(text):
        score += 0.6
        reasons.append("link")
    hits = [k for k in _KEYWORDS if k in text.lower()]
    if hits:
        score += min(0.5 * len(hits), 0.9)
        reasons.extend(f"keyword:{k}" for k in hits)
    score = min(score, 1.0)
    return Verdict(score >= SPAM_THRESHOLD, score, reasons)
