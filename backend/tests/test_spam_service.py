import asyncio

import pytest

from app.core.db import AsyncSessionLocal, SyncSessionLocal
from app.models import Post, Suggestion
from app.seeds.post import SLUG, seed_post
from app.services import suggestions as service


def _add(post_id: int, replacement: str, honeypot: str | None = None) -> None:
    with SyncSessionLocal() as s:
        s.add(
            Suggestion(
                post_id=post_id,
                anchor_start=1,
                anchor_end=5,
                original_text="abcd",
                replacement=replacement,
                honeypot=honeypot,
            )
        )
        s.commit()


async def _run() -> dict[str, int]:
    async with AsyncSessionLocal() as session:
        return await service.run_rules_filter(session, SLUG)


def test_run_rules_filter_counts_and_scores() -> None:
    with SyncSessionLocal() as s:
        post_id = seed_post(s).id
    _add(post_id, "at least 2f+1 nodes")
    _add(post_id, "buy now casino")
    _add(post_id, "ok", honeypot="bot")
    assert asyncio.run(_run()) == {"checked": 3, "spam": 2, "ham": 1, "filtered_total": 2}
    with SyncSessionLocal() as s:
        rows = {r.replacement: r for r in s.query(Suggestion).all()}
        assert rows["at least 2f+1 nodes"].status == "pending"
        assert rows["buy now casino"].status == "filtered"
        assert rows["ok"].spam_score == 1.0
        assert s.query(Post).count() == 1


def test_run_rules_filter_unknown_post() -> None:
    async def go() -> None:
        async with AsyncSessionLocal() as session:
            await service.run_rules_filter(session, "nope")

    with pytest.raises(service.PostNotFoundError):
        asyncio.run(go())
