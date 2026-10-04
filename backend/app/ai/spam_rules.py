"""Rules-first spam classifier. Spam = honeypot alone, or >= 2 signals (link, keywords).

Pure, no I/O.
"""

from dataclasses import dataclass, field

from app.ai.spam_utils import find_keywords, has_link

MIN_SIGNALS = 2  # a link or keyword alone is not enough; honeypot alone is


@dataclass(frozen=True)
class Verdict:
    is_spam: bool
    score: float
    reasons: list[str] = field(default_factory=list)


def classify(
    replacement: str, reason: str | None, name: str | None, honeypot: str | None
) -> Verdict:
    """Score a suggestion in [0, 1]; spam when honeypot is filled or >= MIN_SIGNALS signals."""
    if honeypot:
        return Verdict(True, 1.0, ["honeypot"])
    text = " ".join(t for t in (replacement, reason, name) if t)
    signals = (["link"] if has_link(text) else []) + [f"keyword:{k}" for k in find_keywords(text)]
    return Verdict(len(signals) >= MIN_SIGNALS, min(len(signals) / 3, 1.0), signals)
