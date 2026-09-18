from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class YoutubeSourceDto(BaseModel):
    """Normalized YouTube Data API source (no media blobs)."""

    video_id: str = Field(min_length=1)
    canonical_url: str = Field(min_length=1)
    title: str = Field(min_length=1)
    channel_id: str = Field(min_length=1)
    channel_title: str = Field(min_length=1)
    published_at: datetime
    duration_seconds: int | None = None
    view_count: int | None = None
    like_count: int | None = None
    description: str = ""
    thumbnail_url: str | None = None
    etag: str | None = None
    fetched_at: datetime
    adapter_version: str = Field(min_length=1)

    @property
    def source_system(self) -> str:
        return "youtube"

    @property
    def external_id(self) -> str:
        return self.video_id

    @field_validator("video_id")
    @classmethod
    def _strip_video_id(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("video_id must not be empty")
        return cleaned
