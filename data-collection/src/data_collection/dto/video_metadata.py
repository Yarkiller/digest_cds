"""VideoMetadata DTO — YouTube provenance fields (D-11)."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class VideoMetadata(BaseModel):
    video_id: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    author: str = Field(min_length=1)
    published_at: datetime | None = None

    @field_validator("video_id", "source_url", "author")
    @classmethod
    def _strip_non_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned
