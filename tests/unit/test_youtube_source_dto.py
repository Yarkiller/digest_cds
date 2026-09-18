"""RED→GREEN: YouTube API payload must normalize to YoutubeSourceDto."""

from datetime import datetime, timezone

import pytest


def test_youtube_source_dto_requires_stable_external_identity() -> None:
    from data_collection.dto.youtube import YoutubeSourceDto

    dto = YoutubeSourceDto(
        video_id="dQw4w9WgXcQ",
        canonical_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        title="Example talk",
        channel_id="UCabc",
        channel_title="SVA Channel",
        published_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
        duration_seconds=600,
        view_count=1200,
        like_count=40,
        description="Short desc",
        thumbnail_url="https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        etag="etag-1",
        fetched_at=datetime(2026, 3, 2, tzinfo=timezone.utc),
        adapter_version="1.0.0",
    )

    assert dto.video_id == "dQw4w9WgXcQ"
    assert dto.source_system == "youtube"
    assert dto.external_id == "dQw4w9WgXcQ"


def test_youtube_source_dto_rejects_empty_video_id() -> None:
    from data_collection.dto.youtube import YoutubeSourceDto
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        YoutubeSourceDto(
            video_id="",
            canonical_url="https://www.youtube.com/watch?v=x",
            title="t",
            channel_id="c",
            channel_title="ch",
            published_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            duration_seconds=None,
            view_count=None,
            like_count=None,
            description="",
            thumbnail_url=None,
            etag=None,
            fetched_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            adapter_version="1.0.0",
        )
