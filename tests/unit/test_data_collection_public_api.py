"""Public data_collection.__all__ whitelist + export negatives (D-01…D-04, D-06)."""

from __future__ import annotations

import importlib

import pytest

PUBLIC_NAMES = frozenset(
    {
        "Transcript",
        "VideoMetadata",
        "MaterialDraft",
        "TemplateKind",
        "TranscriptProvider",
        "ArticleGenerator",
    }
)

NEGATIVE_ROOT_NAMES = (
    "ArticleDraft",
    "FakeTranscriptProvider",
    "FakeArticleGenerator",
    "YoutubeSourceDto",
    "TranscriptResultDto",
    "ArticleAssistDto",
    "TextImportDto",
    "SummaryResultDto",
    "TaggingResultDto",
    "EmbeddingResultDto",
    "EMBEDDING_DIM",
)


def test_public_all_is_exactly_six_ingestion_names() -> None:
    """D-01, D-04: package root exports only the six public contracts."""
    import data_collection

    importlib.reload(data_collection)
    assert set(data_collection.__all__) == PUBLIC_NAMES
    for name in sorted(PUBLIC_NAMES):
        assert hasattr(data_collection, name), f"missing public export: {name}"


def test_ports_package_exports_transcript_provider() -> None:
    """WR-01: ports barrel re-exports TranscriptProvider alongside ArticleGenerator."""
    from data_collection.ports import ArticleGenerator, TranscriptProvider

    import data_collection.ports as ports

    importlib.reload(ports)
    assert "TranscriptProvider" in ports.__all__
    assert "ArticleGenerator" in ports.__all__
    assert ports.TranscriptProvider is TranscriptProvider
    assert ports.ArticleGenerator is ArticleGenerator


@pytest.mark.parametrize("name", NEGATIVE_ROOT_NAMES)
def test_negative_names_not_importable_from_package_root(name: str) -> None:
    """D-02, D-04, D-06: fakes, ArticleDraft, and old DTOs are not public exports."""
    import data_collection

    importlib.reload(data_collection)
    assert name not in data_collection.__all__
    with pytest.raises((ImportError, AttributeError)):
        getattr(data_collection, name)
    with pytest.raises(ImportError):
        exec(f"from data_collection import {name}")
