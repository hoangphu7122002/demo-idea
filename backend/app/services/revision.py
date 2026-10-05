import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Post, PostRevision, Suggestion

ANONYMOUS_CREDIT = "a reader"
_MDX_SPECIAL = re.compile(r"([{}<>])")


class SuggestionNotFoundError(Exception):
    pass


class SuggestionStateError(Exception):
    """Not pending, or its anchor no longer matches the post source."""


def escape_mdx(text: str) -> str:
    """Backslash-escape characters MDX treats as JSX/expressions: { } < >."""
    return _MDX_SPECIAL.sub(r"\\\1", text)


def in_literal_region(source: str, pos: int) -> bool:
    """True if pos is in a fenced code block or $...$ math, which MDX keeps literal."""
    before = source[:pos]
    if len(re.findall(r"^\s*(?:```|~~~)", before, re.M)) % 2:
        return True
    return before.count("$") % 2 == 1


def _locate(source: str, s: Suggestion) -> tuple[int, int]:
    """Find the span to replace: stored offsets if they still match, else the first match."""
    start, end = s.anchor_start, s.anchor_end
    if start is not None and end is not None and source[start:end] == s.original_text:
        return start, end
    found = source.find(s.original_text)
    if found < 0:
        raise SuggestionStateError("anchor text not found in current post source")
    return found, found + len(s.original_text)


async def approve_suggestion(
    session: AsyncSession, suggestion_id: int
) -> tuple[Suggestion, PostRevision, str]:
    """Apply the replacement as a new credited revision.

    Returns (suggestion, revision, escaped new text).
    """
    s = await session.get(Suggestion, suggestion_id, with_for_update=True)
    if s is None:
        raise SuggestionNotFoundError(suggestion_id)
    if s.status != "pending":
        raise SuggestionStateError(f"suggestion is {s.status}, only pending can be approved")
    post = await session.scalar(select(Post).where(Post.id == s.post_id).with_for_update())
    if post is None:
        raise SuggestionNotFoundError(suggestion_id)
    start, end = _locate(post.source, s)
    new_text = s.replacement if in_literal_region(post.source, start) else escape_mdx(s.replacement)
    new_source = post.source[:start] + new_text + post.source[end:]
    number = max((r.number for r in post.revisions), default=0) + 1
    revision = PostRevision(
        post_id=post.id,
        number=number,
        source=new_source,
        credit_name=s.name or ANONYMOUS_CREDIT,
        change_start=start,
        change_end=start + len(new_text),
        previous_text=post.source[start:end],
    )
    session.add(revision)
    post.source = new_source
    s.status = "approved"
    await session.commit()
    await session.refresh(revision)
    return s, revision, new_text
