from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.job import _now

STATUSES = ("pending", "filtered", "approved")


class Suggestion(Base):
    __tablename__ = "suggestions"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), index=True)
    # Span anchor: source offsets in the post MDX. Fallback: paragraph_id with null offsets.
    anchor_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    anchor_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    paragraph_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    original_text: Mapped[str] = mapped_column(Text)
    replacement: Mapped[str] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    honeypot: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    spam_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
