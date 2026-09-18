from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Default FoundryModels embedding size until model ID is locked in ADR/spec.
EMBEDDING_DIM = 1024

RoleHint = Literal["analyst", "ds", "sva"]


class TranscriptResultDto(BaseModel):
    source_ref: str = Field(min_length=1)
    text: str = Field(min_length=1)
    language: str = Field(min_length=2)
    confidence: float | None = None
    model_id: str = Field(min_length=1)
    duration_ms: int | None = None

    @field_validator("text")
    @classmethod
    def _non_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("transcript text must not be blank")
        return value


class SummaryResultDto(BaseModel):
    summary_ru: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)


class TagItem(BaseModel):
    slug: str = Field(min_length=1)
    label: str = Field(min_length=1)


class TaggingResultDto(BaseModel):
    tags: list[TagItem]
    role_hints: list[RoleHint]
    model_id: str = Field(min_length=1)


class EmbeddingResultDto(BaseModel):
    vector: list[float]
    model_id: str = Field(min_length=1)
    input_hash: str = Field(min_length=1)

    @field_validator("vector")
    @classmethod
    def _fixed_dim(cls, value: list[float]) -> list[float]:
        if len(value) != EMBEDDING_DIM:
            raise ValueError(f"embedding must have length {EMBEDDING_DIM}")
        return value


class ArticleAssistDto(BaseModel):
    title: str = Field(min_length=1)
    dek: str = Field(min_length=1)
    body_markdown: str = Field(min_length=1)
    related_material_ids: list[str] = Field(default_factory=list)
    tags: list[TagItem] = Field(default_factory=list)
    role_hints: list[RoleHint] = Field(default_factory=list)
    model_id: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
    format: Literal["статья"] = "статья"
