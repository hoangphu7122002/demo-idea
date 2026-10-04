from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import SessionDep
from app.models import Post, Suggestion
from app.schemas.suggestion import SuggestionIn, SuggestionOut, SuggestionStatus

router = APIRouter(prefix="/api/posts/{slug}/suggestions", tags=["suggestions"])


async def _post(slug: str, session: SessionDep) -> Post:
    post = await session.scalar(select(Post).where(Post.slug == slug))
    if post is None:
        raise HTTPException(404, "post not found")
    return post


@router.post("", response_model=SuggestionOut, status_code=201)
async def submit_suggestion(slug: str, data: SuggestionIn, session: SessionDep) -> Suggestion:
    """Anonymous submit. Lands as pending."""
    post = await _post(slug, session)
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


@router.get("", response_model=list[SuggestionOut])
async def list_suggestions(
    slug: str, session: SessionDep, status: SuggestionStatus | None = None
) -> list[Suggestion]:
    post = await _post(slug, session)
    q = select(Suggestion).where(Suggestion.post_id == post.id).order_by(Suggestion.id)
    if status is not None:
        q = q.where(Suggestion.status == status)
    return list((await session.scalars(q)).all())
