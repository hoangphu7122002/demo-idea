from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.models import Suggestion
from app.schemas.suggestion import SuggestionIn, SuggestionOut, SuggestionStatus
from app.services import suggestions as service

router = APIRouter(prefix="/api/posts/{slug}/suggestions", tags=["suggestions"])


@router.post("", response_model=SuggestionOut, status_code=201)
async def submit_suggestion(slug: str, data: SuggestionIn, session: SessionDep) -> Suggestion:
    """Anonymous submit. Lands as pending."""
    try:
        return await service.create_suggestion(session, slug, data)
    except service.PostNotFoundError:
        raise HTTPException(404, "post not found") from None


@router.get("", response_model=list[SuggestionOut])
async def list_suggestions(
    slug: str, session: SessionDep, status: SuggestionStatus | None = None
) -> list[Suggestion]:
    try:
        return await service.list_suggestions(session, slug, status)
    except service.PostNotFoundError:
        raise HTTPException(404, "post not found") from None
