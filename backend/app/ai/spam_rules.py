"""Rules-first spam classifier: honeypot, links, keywords. Pure, no I/O."""

from dataclasses import dataclass, field

from app.ai.spam_utils import find_keywords, has_link

SPAM_THRESHOLD = 0.5


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
    if has_link(text):
        score += 0.6
        reasons.append("link")
    hits = find_keywords(text)
    if hits:
        score += min(0.5 * len(hits), 0.9)
        reasons.extend(f"keyword:{k}" for k in hits)
    score = min(score, 1.0)
    return Verdict(score >= SPAM_THRESHOLD, score, reasons)
