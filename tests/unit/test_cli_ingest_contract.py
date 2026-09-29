"""RED→GREEN: Typer ingest happy-path stdout contract (D-01…D-07, D-09, D-11; CLI-01; CLI-04)."""

from __future__ import annotations

from data_collection.dto.article_draft import ArticleDraft
from data_collection.dto.transcript import Transcript
from data_collection.dto.video_metadata import VideoMetadata
from data_collection.tests_support.fakes import (
    FakeArticleGenerator,
    FakeTranscriptProvider,
    FakeVideoMetadataProvider,
)
from ingestion_service.application.ports.persist import PersistResult
from ingestion_service.tests_support.fakes import FakeDraftPersister

VIDEO_ID = "dQw4w9WgXcQ"
URL = f"https://youtu.be/{VIDEO_ID}"
EXPECTED_SLUG = "kak-ispolzovat-pgvector-dQw4w9WgXcQ"

EXPECTED_SUCCESS_LINES = [
    "✓ transcript",
    "✓ LLM",
    "✓ saved",
    "material_id: 42",
    f"slug: {EXPECTED_SLUG}",
    "batch_id: 7",
    "rank: 1",
    "already_saved: false",
]


def _transcript() -> Transcript:
    return Transcript(text="ok captions", language="ru", video_id=VIDEO_ID)


def _article() -> ArticleDraft:
    return ArticleDraft(
        title="Как использовать pgvector",
        dek="dek",
        body_markdown="body text here",
    )


def _metadata() -> VideoMetadata:
    return VideoMetadata(
        video_id=VIDEO_ID,
        source_url=f"https://www.youtube.com/watch?v={VIDEO_ID}",
        author="Rick Astley",
    )


def _persist_result(*, already_saved: bool = False) -> PersistResult:
    return PersistResult(
        material_id=42,
        slug=EXPECTED_SLUG,
        batch_id=7,
        rank=1,
        already_saved=already_saved,
    )


def _fake_deps(persist: FakeDraftPersister | None = None) -> object:
    from types import SimpleNamespace

    return SimpleNamespace(
        captions=FakeTranscriptProvider(result=_transcript()),
        metadata_provider=FakeVideoMetadataProvider(result=_metadata()),
        article=FakeArticleGenerator(result=_article()),
        persist=persist or FakeDraftPersister(_persist_result()),
    )


def test_cli_happy_path_stdout_contract(monkeypatch) -> None:
    from typer.testing import CliRunner

    from ingestion_service import cli as cli_mod

    deps = _fake_deps()
    monkeypatch.setattr(cli_mod, "build_ingest_deps", lambda: deps)

    result = CliRunner().invoke(cli_mod.app, [URL, "--template", "lecture"])
    assert result.exit_code == 0
    assert result.stdout.splitlines() == EXPECTED_SUCCESS_LINES
    assert result.stderr == ""


def test_cli_requires_template_flag(monkeypatch) -> None:
    from typer.testing import CliRunner

    from ingestion_service import cli as cli_mod

    monkeypatch.setattr(cli_mod, "build_ingest_deps", lambda: _fake_deps())

    result = CliRunner().invoke(cli_mod.app, [URL])
    assert result.exit_code != 0
    assert "material_id:" not in result.stdout
