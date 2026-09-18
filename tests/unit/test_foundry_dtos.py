"""RED→GREEN: FoundryModels operation DTOs with model versioning."""

import pytest
from pydantic import ValidationError


def test_embedding_result_dto_fixed_dimension() -> None:
    from data_collection.dto.foundry import EMBEDDING_DIM, EmbeddingResultDto

    vector = [0.1] * EMBEDDING_DIM
    dto = EmbeddingResultDto(
        vector=vector,
        model_id="foundry-embed-v1",
        input_hash="abc123",
    )
    assert len(dto.vector) == EMBEDDING_DIM
    assert dto.model_id == "foundry-embed-v1"


def test_embedding_result_dto_rejects_wrong_dimension() -> None:
    from data_collection.dto.foundry import EmbeddingResultDto

    with pytest.raises(ValidationError):
        EmbeddingResultDto(
            vector=[0.1, 0.2],
            model_id="foundry-embed-v1",
            input_hash="abc123",
        )


def test_transcript_result_dto_rejects_empty_text() -> None:
    from data_collection.dto.foundry import TranscriptResultDto

    with pytest.raises(ValidationError):
        TranscriptResultDto(
            source_ref="youtube:dQw4w9WgXcQ",
            text="   ",
            language="ru",
            confidence=0.9,
            model_id="whisper-like",
            duration_ms=1000,
        )


def test_article_assist_dto_format_is_article() -> None:
    from data_collection.dto.foundry import ArticleAssistDto

    dto = ArticleAssistDto(
        title="RAG for audit",
        dek="Как искать по регламентам СВА.",
        body_markdown="# Intro\n\nBody",
        related_material_ids=["anomaly-detection"],
        tags=[{"slug": "rag", "label": "RAG"}],
        role_hints=["ds", "sva"],
        model_id="article-assist-v1",
        prompt_version="2026-03-01",
    )
    assert dto.format == "статья"
    assert dto.role_hints == ["ds", "sva"]
