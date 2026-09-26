"""MaterialDraft DTO — prepared article + provenance for draft persist (D-05, D-13)."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class MaterialDraft(BaseModel):
    title: str = Field(min_length=1)
    dek: str = Field(min_length=1)
    body_markdown: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    youtube_video_id: str = Field(min_length=1)
    source_author: str = Field(min_length=1)
    provenance_label: str = Field(min_length=1)
    source_published_at: datetime | None = None

    @field_validator(
        "title",
        "dek",
        "body_markdown",
        "source_url",
        "youtube_video_id",
        "source_author",
        "provenance_label",
    )
    @classmethod
    def _strip_non_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned
