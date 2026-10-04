from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from app.api.deps import SessionDep
from app.models import Post

router = APIRouter(prefix="/api/posts", tags=["posts"])


class RevisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    number: int
    credit_name: str | None = None
    change_start: int | None = None
    change_end: int | None = None
    previous_text: str | None = None
    created_at: datetime


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    title: str
    source: str
    revisions: list[RevisionOut]


@router.get("/{slug}", response_model=PostOut)
async def get_post(slug: str, session: SessionDep) -> Post:
    """Current MDX source plus all revisions (oldest first)."""
    post = await session.scalar(select(Post).where(Post.slug == slug))
    if post is None:
        raise HTTPException(404, "post not found")
    return post
