"""Transcript DTO — captions text before LLM (D-09)."""

from pydantic import BaseModel, Field, field_validator


class Transcript(BaseModel):
    text: str = Field(min_length=1)
    language: str
    video_id: str = Field(min_length=1)

    @field_validator("text", "video_id")
    @classmethod
    def _strip_non_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned

    @field_validator("language")
    @classmethod
    def _strip_language(cls, value: str) -> str:
        cleaned = value.strip()
        if not (2 <= len(cleaned) <= 10):
            raise ValueError("language length must be 2–10")
        return cleaned
