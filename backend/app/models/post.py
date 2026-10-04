from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.job import _now


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(300))
    source: Mapped[str] = mapped_column(Text)  # current MDX source (latest revision)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    revisions: Mapped[list["PostRevision"]] = relationship(
        back_populates="post", order_by="PostRevision.number", lazy="selectin"
    )


class PostRevision(Base):
    __tablename__ = "post_revisions"
    __table_args__ = (UniqueConstraint("post_id", "number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), index=True)
    number: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(Text)
    credit_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Span changed vs previous revision (source offsets in this revision); null for the original.
    change_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    change_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    previous_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    post: Mapped[Post] = relationship(back_populates="revisions")
