"""RED→GREEN: CAP-02 deferred proof — captions/article failure writes zero persist rows."""

from __future__ import annotations

import asyncio

import pytest

from data_collection.dto.article_draft import ArticleDraft
from data_collection.dto.template_kind import TemplateKind
from data_collection.dto.transcript import Transcript
from data_collection.errors.article import ArticleError, ArticleNetworkError
from data_collection.errors.captions import CaptionsError, CaptionsUnavailable
from data_collection.tests_support.fakes import FakeArticleGenerator, FakeTranscriptProvider
from ingestion_service.application.ports.persist import PersistResult
from ingestion_service.tests_support.fakes import FakeDraftPersister

VIDEO_ID = "dQw4w9WgXcQ"


def _unused_transcript() -> Transcript:
    return Transcript(text="unused", language="ru", video_id=VIDEO_ID)


def _unused_article() -> ArticleDraft:
    return ArticleDraft(title="T", dek="D", body_markdown="B")


def _persist_spy() -> FakeDraftPersister:
    return FakeDraftPersister(
        PersistResult(material_id=1, slug="unused", batch_id=1, rank=1)
    )


async def attempt_captions(provider: FakeTranscriptProvider, video_id: str) -> None:
    raise NotImplementedError("CAP-02 captions boundary")


async def attempt_article(
    generator: FakeArticleGenerator, transcript: Transcript
) -> None:
    raise NotImplementedError("CAP-02 article boundary")


def test_captions_failure_leaves_persist_calls_empty() -> None:
    provider = FakeTranscriptProvider(
        result=_unused_transcript(),
        failures={VIDEO_ID: CaptionsUnavailable(VIDEO_ID)},
    )
    spy = _persist_spy()

    with pytest.raises(CaptionsError):
        asyncio.run(attempt_captions(provider, VIDEO_ID))

    assert spy.calls == []


def test_article_failure_leaves_persist_calls_empty() -> None:
    transcript = Transcript(text="ok", language="ru", video_id=VIDEO_ID)
    generator = FakeArticleGenerator(
        result=_unused_article(),
        failures={VIDEO_ID: ArticleNetworkError(VIDEO_ID)},
    )
    spy = _persist_spy()

    with pytest.raises(ArticleError):
        asyncio.run(attempt_article(generator, transcript))

    assert spy.calls == []
