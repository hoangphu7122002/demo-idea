from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SuggestionStatus = Literal["pending", "filtered", "approved"]


class SuggestionIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    anchor_start: int | None = Field(default=None, ge=0)
    anchor_end: int | None = Field(default=None, ge=0)
    paragraph_id: str | None = Field(default=None, max_length=100)
    original_text: str = Field(min_length=1)
    replacement: str = Field(min_length=1)
    reason: str | None = None
    name: str | None = Field(default=None, max_length=100)
    website: str | None = None  # honeypot: real readers leave it empty

    @model_validator(mode="after")
    def _anchor(self) -> "SuggestionIn":
        span = self.anchor_start is not None and self.anchor_end is not None
        if span and self.anchor_end is not None and self.anchor_start is not None:
            if self.anchor_end <= self.anchor_start:
                raise ValueError("anchor_end must be greater than anchor_start")
        elif not self.paragraph_id:
            raise ValueError("anchor needs a start/end span or a paragraph_id")
        return self


class SuggestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    anchor_start: int | None = None
    anchor_end: int | None = None
    paragraph_id: str | None = None
    original_text: str
    replacement: str
    reason: str | None = None
    name: str | None = None
    status: SuggestionStatus
    spam_score: float | None = None
    created_at: datetime
