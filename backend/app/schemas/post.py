from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
