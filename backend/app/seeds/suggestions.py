"""Ten seeded suggestions for the demo: 7 spam, 3 real fixes. Lan's live one is not seeded."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import Post, Suggestion
from app.seeds.post import SOURCE

AUTHOR_NAME = "Demo Author"  # seeded author, always logged in (no auth model in the demo)


@dataclass(frozen=True)
class Seed:
    original: str
    replacement: str
    reason: str | None = None
    name: str | None = None
    honeypot: str | None = None


REAL = [
    Seed(
        "leader accepts client writes",
        "leader accepts all client writes",
        "followers should redirect writes to the leader",
        "Minh",
    ),
    Seed(
        "they resolve on the next term",
        "they resolve in a later term",
        "a split vote can repeat, so it may take several terms",
        "Hana",
    ),
    Seed("a randomized timeout", "a randomized election timeout", None, None),
]
SPAM = [
    Seed("Raft keeps", "Buy now cheap crypto, click here for free money", None, "CryptoKing"),
    Seed("a majority", "Best casino bonus at www.win-big.example", "limited offer", "Bob"),
    Seed("heartbeat", "Cheap loan approval, apply at https://loans.example", None, "LoanBot"),
    Seed("quorum", "Work from home and earn bitcoin, join our telegram", None, "Earn"),
    Seed("candidate", "nice post", None, "seo", honeypot="http://seo.example"),
    Seed("Leader election", "great article thanks", None, None, honeypot="1"),
    Seed("split votes", "visit my site", "buy now", "x", honeypot="spam"),
]


def seed_suggestions(session: Session, post: Post) -> list[Suggestion]:
    """Insert the 10 items, interleaved so the filter visibly moves spam out of the queue."""
    items = [
        REAL[0],
        SPAM[0],
        SPAM[1],
        REAL[1],
        SPAM[2],
        SPAM[3],
        REAL[2],
        SPAM[4],
        SPAM[5],
        SPAM[6],
    ]
    rows: list[Suggestion] = []
    for it in items:
        start = SOURCE.index(it.original)
        rows.append(
            Suggestion(
                post_id=post.id,
                anchor_start=start,
                anchor_end=start + len(it.original),
                original_text=it.original,
                replacement=it.replacement,
                reason=it.reason,
                name=it.name,
                honeypot=it.honeypot,
            )
        )
    session.add_all(rows)
    session.commit()
    return rows
