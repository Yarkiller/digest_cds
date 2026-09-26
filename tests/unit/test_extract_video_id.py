"""RED→GREEN: extract_video_id accept/reject (CAP-01, D-01…D-05)."""

from __future__ import annotations

import pytest


VIDEO_ID = "dQw4w9WgXcQ"


@pytest.mark.parametrize(
    "value",
    [
        f"https://www.youtube.com/watch?v={VIDEO_ID}",
        f"https://youtu.be/{VIDEO_ID}",
        f"https://m.youtube.com/shorts/{VIDEO_ID}",
        f"https://youtube.com/embed/{VIDEO_ID}",
        VIDEO_ID,
    ],
)
def test_extract_video_id_accepts_url_families(value: str) -> None:
    from ingestion_service.url import extract_video_id

    assert extract_video_id(value) == VIDEO_ID


@pytest.mark.parametrize(
    "value",
    [
        "https://example.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch",
    ],
)
def test_extract_video_id_rejects_invalid_inputs(value: str) -> None:
    from ingestion_service.url import InvalidYouTubeUrl, extract_video_id

    with pytest.raises(InvalidYouTubeUrl) as exc_info:
        extract_video_id(value)

    err = exc_info.value
    assert isinstance(err.reason, str)
    assert err.reason  # production-owned snake_case code
    assert err.reason == err.reason.lower()
    assert " " not in err.reason
