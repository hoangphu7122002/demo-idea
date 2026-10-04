from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import SessionDep
from app.models import Post
from app.schemas.post import PostOut

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("/{slug}", response_model=PostOut)
async def get_post(slug: str, session: SessionDep) -> Post:
    """Current MDX source plus all revisions (oldest first)."""
    post = await session.scalar(select(Post).where(Post.slug == slug))
    if post is None:
        raise HTTPException(404, "post not found")
    return post
