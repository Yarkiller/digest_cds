"""RED→GREEN: CONSISTENCY-01, provenance suffix, captions-then-metadata, CAP-02 (CLI-04)."""

from __future__ import annotations

import asyncio

import pytest
from data_collection.dto.article_draft import ArticleDraft
from data_collection.dto.template_kind import TemplateKind
from data_collection.dto.transcript import Transcript
from data_collection.dto.video_metadata import VideoMetadata
from data_collection.errors.captions import CaptionsUnavailable
from data_collection.tests_support.fakes import (
    FakeArticleGenerator,
    FakeTranscriptProvider,
    FakeVideoMetadataProvider,
)
from ingestion_service.application.ports.persist import PersistResult
from ingestion_service.application.use_cases.ingest_pipeline import run_ingest_pipeline
from ingestion_service.domain.errors import IngestError
from ingestion_service.provenance import ENGLISH_TRANSLATION_SUFFIX
from ingestion_service.tests_support.fakes import FakeDraftPersister, RecordingDiagnostics

VIDEO_ID = "dQw4w9WgXcQ"
OTHER_VIDEO_ID = "oHg5SJYRHA0"
URL = f"https://youtu.be/{VIDEO_ID}"


def _transcript(*, language: str = "ru", video_id: str = VIDEO_ID) -> Transcript:
    return Transcript(text="ok captions", language=language, video_id=video_id)


def _article() -> ArticleDraft:
    return ArticleDraft(title="T", dek="D", body_markdown="B")


def _metadata(*, video_id: str = VIDEO_ID, author: str = "Rick Astley") -> VideoMetadata:
    return VideoMetadata(
        video_id=video_id,
        source_url=f"https://www.youtube.com/watch?v={video_id}",
        author=author,
    )


def _persist() -> FakeDraftPersister:
    return FakeDraftPersister(
        PersistResult(material_id=1, slug="t-dQw4w9WgXcQ", batch_id=1, rank=1)
    )


def test_consistency_mismatch_raises_before_llm_and_persist() -> None:
    """CONSISTENCY-01: mismatched ids → stage=consistency, reason=video_id_mismatch."""
    captions = FakeTranscriptProvider(result=_transcript(video_id=VIDEO_ID))
    metadata = FakeVideoMetadataProvider(result=_metadata(video_id=OTHER_VIDEO_ID))
    article = FakeArticleGenerator(result=_article())
    persist = _persist()

    with pytest.raises(IngestError) as exc_info:
        asyncio.run(
            run_ingest_pipeline(
                URL,
                TemplateKind.LECTURE,
                captions=captions,
                metadata_provider=metadata,
                article=article,
                persist=persist,
            )
        )

    err = exc_info.value
    assert err.stage == "consistency"
    assert err.reason == "video_id_mismatch"
    assert set(err.context.keys()) == {"transcript_video_id", "metadata_video_id"}
    assert err.context["transcript_video_id"] == VIDEO_ID
    assert err.context["metadata_video_id"] == OTHER_VIDEO_ID
    assert article.calls == []
    assert persist.calls == []


def test_captions_failure_leaves_article_and_persist_empty() -> None:
    """CAP-02 through full pipeline: captions failure → no LLM, no persist."""
    captions = FakeTranscriptProvider(
        result=_transcript(),
        failures={VIDEO_ID: CaptionsUnavailable(VIDEO_ID)},
    )
    metadata = FakeVideoMetadataProvider(result=_metadata())
    article = FakeArticleGenerator(result=_article())
    persist = _persist()

    with pytest.raises(IngestError) as exc_info:
        asyncio.run(
            run_ingest_pipeline(
                URL,
                TemplateKind.LECTURE,
                captions=captions,
                metadata_provider=metadata,
                article=article,
                persist=persist,
            )
        )

    assert exc_info.value.stage == "captions"
    assert article.calls == []
    assert persist.calls == []
    assert metadata.calls == []


def test_captions_fetched_before_metadata() -> None:
    """Phase 7 D-24: captions.get awaited before metadata.get."""
    order: list[str] = []

    class OrderCaptions(FakeTranscriptProvider):
        async def get(self, video_id: str) -> Transcript:
            order.append("captions")
            return await super().get(video_id)

    class OrderMetadata(FakeVideoMetadataProvider):
        async def get(self, video_id: str) -> VideoMetadata:
            order.append("metadata")
            return await super().get(video_id)

    captions = OrderCaptions(result=_transcript())
    metadata = OrderMetadata(result=_metadata())
    article = FakeArticleGenerator(result=_article())
    persist = _persist()

    asyncio.run(
        run_ingest_pipeline(
            URL,
            TemplateKind.LECTURE,
            captions=captions,
            metadata_provider=metadata,
            article=article,
            persist=persist,
        )
    )

    assert order == ["captions", "metadata"]


def test_english_transcript_appends_translation_suffix() -> None:
    """Phase 8 D-05: language != ru → provenance ends with ENGLISH_TRANSLATION_SUFFIX."""
    captions = FakeTranscriptProvider(result=_transcript(language="en"))
    metadata = FakeVideoMetadataProvider(result=_metadata(author="Channel X"))
    article = FakeArticleGenerator(result=_article())
    persist = _persist()

    asyncio.run(
        run_ingest_pipeline(
            URL,
            TemplateKind.LECTURE,
            captions=captions,
            metadata_provider=metadata,
            article=article,
            persist=persist,
        )
    )

    assert len(persist.calls) == 1
    label = persist.calls[0].provenance_label
    assert label.endswith(ENGLISH_TRANSLATION_SUFFIX)
    assert label.startswith("YouTube · Channel X")


def test_russian_transcript_omits_translation_suffix() -> None:
    """Phase 8 D-05: language=ru → YouTube · {author} without suffix."""
    captions = FakeTranscriptProvider(result=_transcript(language="ru"))
    metadata = FakeVideoMetadataProvider(result=_metadata(author="Channel X"))
    article = FakeArticleGenerator(result=_article())
    persist = _persist()

    asyncio.run(
        run_ingest_pipeline(
            URL,
            TemplateKind.LECTURE,
            captions=captions,
            metadata_provider=metadata,
            article=article,
            persist=persist,
        )
    )

    assert len(persist.calls) == 1
    assert persist.calls[0].provenance_label == "YouTube · Channel X"
    assert ENGLISH_TRANSLATION_SUFFIX not in persist.calls[0].provenance_label


def test_pipeline_emits_stage_events_in_order() -> None:
    """D-04: start→complete fires for captions, metadata, llm, persist (in order)."""
    diagnostics = RecordingDiagnostics()
    captions = FakeTranscriptProvider(result=_transcript())
    metadata = FakeVideoMetadataProvider(result=_metadata())
    article = FakeArticleGenerator(result=_article())
    persist = _persist()

    result = asyncio.run(
        run_ingest_pipeline(
            URL,
            TemplateKind.LECTURE,
            captions=captions,
            metadata_provider=metadata,
            article=article,
            persist=persist,
            diagnostics=diagnostics,
        )
    )

    order = [(call[0], call[1]) for call in diagnostics.calls]
    assert order == [
        ("started", "captions"),
        ("completed", "captions"),
        ("started", "metadata"),
        ("completed", "metadata"),
        ("started", "llm"),
        ("completed", "llm"),
        ("started", "persist"),
        ("completed", "persist"),
    ]

    completed = {
        call[1]: call[2]
        for call in diagnostics.calls
        if call[0] == "completed" and len(call) > 2
    }
    # D-06: the metadata line exposes only video_id.
    assert completed["metadata"] == {"video_id": VIDEO_ID}
    # D-04: llm carries template + response length; persist carries the identifiers.
    assert completed["llm"] == {"template": "lecture", "response_chars": len("B")}
    assert completed["persist"]["material_id"] == result.material_id
    assert completed["persist"]["batch_id"] == result.batch_id
    assert completed["persist"]["rank"] == result.rank
    assert completed["persist"]["already_saved"] == result.already_saved
