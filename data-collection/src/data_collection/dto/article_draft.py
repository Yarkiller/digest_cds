"""Internal ArticleDraft — LLM output only; not public package API (D-06)."""

from pydantic import BaseModel, Field, field_validator

from data_collection.dto._validators import strip_non_blank


class ArticleDraft(BaseModel):
    title: str = Field(min_length=1)
    dek: str = Field(min_length=1)
    body_markdown: str = Field(min_length=1)

    @field_validator("title", "dek", "body_markdown")
    @classmethod
    def _strip_non_blank(cls, value: str) -> str:
        return strip_non_blank(value)
