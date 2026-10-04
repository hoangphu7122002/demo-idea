from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
