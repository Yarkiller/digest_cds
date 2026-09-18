from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class TextImportDto(BaseModel):
    """Manual text / URL import into the ingestion pipeline."""

    source_url: str | None = None
    title_hint: str | None = None
    raw_text: str = Field(min_length=1)
    content_sha256: str = Field(min_length=64, max_length=64)
    imported_by: str = Field(min_length=1)
    imported_at: datetime
    adapter_version: str = Field(min_length=1)

    @property
    def source_system(self) -> str:
        return "text_import"

    @field_validator("raw_text")
    @classmethod
    def _non_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("raw_text must not be blank")
        return value
