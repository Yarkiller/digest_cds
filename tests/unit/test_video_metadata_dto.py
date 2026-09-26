"""RED→GREEN: VideoMetadata DTO (D-11, DTO-01)."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError


def test_video_metadata_constructs_required_fields() -> None:
    from data_collection.dto.video_metadata import VideoMetadata

    dto = VideoMetadata(
        video_id="dQw4w9WgXcQ",
        source_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        author="Rick Astley",
    )
    assert dto.video_id == "dQw4w9WgXcQ"
    assert dto.source_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert dto.author == "Rick Astley"
    assert dto.published_at is None


def test_video_metadata_published_at_optional() -> None:
    from data_collection.dto.video_metadata import VideoMetadata

    published = datetime(2009, 10, 25, tzinfo=timezone.utc)
    dto = VideoMetadata(
        video_id="dQw4w9WgXcQ",
        source_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        author="Rick Astley",
        published_at=published,
    )
    assert dto.published_at == published


def test_video_metadata_rejects_blank_video_id() -> None:
    from data_collection.dto.video_metadata import VideoMetadata

    with pytest.raises(ValidationError):
        VideoMetadata(
            video_id="   ",
            source_url="https://example.com",
            author="Author",
        )
