from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import spam_rules
from app.models import Post, Suggestion
from app.schemas.suggestion import SuggestionIn, SuggestionStatus


class PostNotFoundError(Exception):
    pass


async def get_post(session: AsyncSession, slug: str) -> Post:
    post = await session.scalar(select(Post).where(Post.slug == slug))
    if post is None:
        raise PostNotFoundError(slug)
    return post


async def create_suggestion(session: AsyncSession, slug: str, data: SuggestionIn) -> Suggestion:
    """Store an anonymous suggestion as pending."""
    post = await get_post(session, slug)
    s = Suggestion(
        post_id=post.id,
        anchor_start=data.anchor_start,
        anchor_end=data.anchor_end,
        paragraph_id=data.paragraph_id,
        original_text=data.original_text,
        replacement=data.replacement,
        reason=data.reason or None,
        name=data.name or None,
        honeypot=data.website or None,
    )
    session.add(s)
    await session.commit()
    await session.refresh(s)
    return s


async def list_suggestions(
    session: AsyncSession, slug: str, status: SuggestionStatus | None
) -> list[Suggestion]:
    post = await get_post(session, slug)
    q = select(Suggestion).where(Suggestion.post_id == post.id).order_by(Suggestion.id)
    if status is not None:
        q = q.where(Suggestion.status == status)
    return list((await session.scalars(q)).all())


async def run_rules_filter(session: AsyncSession, slug: str) -> dict[str, int]:
    """Classify all pending suggestions by rules; spam moves to filtered."""
    post = await get_post(session, slug)
    pending = (
        await session.scalars(
            select(Suggestion).where(Suggestion.post_id == post.id, Suggestion.status == "pending")
        )
    ).all()
    spam = 0
    for s in pending:
        verdict = spam_rules.classify(s.replacement, s.reason, s.name, s.honeypot)
        s.spam_score = verdict.score
        if verdict.is_spam:
            s.status = "filtered"
            spam += 1
    await session.commit()
    filtered_total = await session.scalar(
        select(func.count()).where(Suggestion.post_id == post.id, Suggestion.status == "filtered")
    )
    return {
        "checked": len(pending),
        "spam": spam,
        "ham": len(pending) - spam,
        "filtered_total": filtered_total or 0,
    }
