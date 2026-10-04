from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.models import Suggestion
from app.schemas.post import RevisionOut
from app.schemas.suggestion import (
    ApproveOut,
    RunFilterOut,
    SuggestionIn,
    SuggestionOut,
    SuggestionStatus,
)
from app.services import revision as revision_service
from app.services import suggestions as service

router = APIRouter(prefix="/api/posts/{slug}/suggestions", tags=["suggestions"])
filter_router = APIRouter(prefix="/api/posts/{slug}", tags=["suggestions"])


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


@filter_router.post("/run-filter", response_model=RunFilterOut)
async def run_filter(slug: str, session: SessionDep) -> RunFilterOut:
    """Classify pending suggestions; spam moves to filtered. Returns counts."""
    try:
        return RunFilterOut(**await service.run_rules_filter(session, slug))
    except service.PostNotFoundError:
        raise HTTPException(404, "post not found") from None


approve_router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])


@approve_router.post("/{suggestion_id}/approve", response_model=ApproveOut)
async def approve(suggestion_id: int, session: SessionDep) -> ApproveOut:
    """Apply the suggestion to the post as a new credited revision."""
    try:
        s, rev, new_text = await revision_service.approve_suggestion(session, suggestion_id)
    except revision_service.SuggestionNotFoundError:
        raise HTTPException(404, "suggestion not found") from None
    except revision_service.SuggestionStateError as e:
        raise HTTPException(409, str(e)) from None
    assert rev.change_start is not None and rev.change_end is not None
    return ApproveOut(
        suggestion=SuggestionOut.model_validate(s),
        revision=RevisionOut.model_validate(rev),
        old_text=rev.previous_text or "",
        new_text=new_text,
        change_start=rev.change_start,
        change_end=rev.change_end,
        credit_name=rev.credit_name or revision_service.ANONYMOUS_CREDIT,
    )
