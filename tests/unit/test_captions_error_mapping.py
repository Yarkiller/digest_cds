"""RED→GREEN: CaptionsError → IngestError(stage=captions) locked reasons (CAP-02, D-10, D-13)."""

from __future__ import annotations

import pytest
from youtube_transcript_api import (
    AgeRestricted,
    CouldNotRetrieveTranscript,
    IpBlocked,
    NoTranscriptFound,
    PoTokenRequired,
    RequestBlocked,
    TranscriptsDisabled,
    VideoUnavailable,
    VideoUnplayable,
    YouTubeRequestFailed,
)

from data_collection.errors.captions import (
    CaptionsBlocked,
    CaptionsBotChallenge,
    CaptionsDisabled,
    CaptionsEmpty,
    CaptionsError,
    CaptionsNetworkError,
    CaptionsNoPreferredLanguage,
    CaptionsUnavailable,
    CaptionsVideoUnavailable,
)


VIDEO_ID = "dQw4w9WgXcQ"

LOCKED_REASONS = frozenset(
    {
        "no_captions",
        "no_preferred_language",
        "captions_disabled",
        "video_unavailable",
        "youtube_blocked",
        "bot_challenge",
        "network_error",
        "empty_captions",
        "unknown_captions_error",
    }
)

SDK_EXCEPTION_NAMES = frozenset(
    {
        TranscriptsDisabled.__name__,
        NoTranscriptFound.__name__,
        VideoUnavailable.__name__,
        VideoUnplayable.__name__,
        AgeRestricted.__name__,
        IpBlocked.__name__,
        RequestBlocked.__name__,
        PoTokenRequired.__name__,
        YouTubeRequestFailed.__name__,
        CouldNotRetrieveTranscript.__name__,
    }
)


@pytest.mark.parametrize(
    ("error", "reason"),
    [
        (CaptionsUnavailable(VIDEO_ID), "no_captions"),
        (
            CaptionsNoPreferredLanguage(VIDEO_ID, ["de", "es"]),
            "no_preferred_language",
        ),
        (CaptionsDisabled(VIDEO_ID), "captions_disabled"),
        (CaptionsVideoUnavailable(VIDEO_ID), "video_unavailable"),
        (CaptionsBlocked(VIDEO_ID), "youtube_blocked"),
        (CaptionsBotChallenge(VIDEO_ID), "bot_challenge"),
        (CaptionsNetworkError(VIDEO_ID), "network_error"),
        (CaptionsEmpty(VIDEO_ID), "empty_captions"),
        (CaptionsError(VIDEO_ID), "unknown_captions_error"),
    ],
)
def test_map_captions_error_subtype_to_locked_reason(
    error: CaptionsError, reason: str
) -> None:
    from ingestion_service.mapping.captions import map_captions_error

    mapped = map_captions_error(error)

    assert mapped.stage == "captions"
    assert mapped.reason == reason
    assert mapped.context.get("video_id") == VIDEO_ID
    payload = mapped.to_dict()
    assert payload["ok"] is False
    assert payload["stage"] == "captions"
    assert payload["exit_code"] == 1


def test_locked_reason_set_equals_d10_exactly() -> None:
    from ingestion_service.mapping import captions as captions_mapping

    assert frozenset(captions_mapping.CAPTIONS_REASONS) == LOCKED_REASONS


def test_no_reason_equals_sdk_exception_class_name() -> None:
    from ingestion_service.mapping import captions as captions_mapping

    assert LOCKED_REASONS.isdisjoint(SDK_EXCEPTION_NAMES)
    assert frozenset(captions_mapping.CAPTIONS_REASONS).isdisjoint(SDK_EXCEPTION_NAMES)


def test_map_captions_error_redacts_credentialed_proxy_context() -> None:
    from ingestion_service.mapping.captions import map_captions_error

    error = CaptionsNetworkError(
        VIDEO_ID,
        exception_class="Timeout",
        proxy_url="socks5://user:secret@192.168.1.68:1080",
        YOUTUBE_PROXY_URL="socks5://user:secret@192.168.1.68:1080",
    )

    mapped = map_captions_error(error)

    assert mapped.context.get("video_id") == VIDEO_ID
    assert mapped.context.get("exception_class") == "Timeout"
    assert "proxy_url" not in mapped.context
    assert "YOUTUBE_PROXY_URL" not in mapped.context
    assert "secret" not in str(mapped.context)
    assert "socks5://" not in str(mapped.context)


def test_map_captions_error_forwards_available_languages() -> None:
    from ingestion_service.mapping.captions import map_captions_error

    error = CaptionsNoPreferredLanguage(VIDEO_ID, ["de", "es"])
    mapped = map_captions_error(error)
    assert mapped.context.get("available_languages") == ["de", "es"]


def test_roadmap_records_cap02_live_persist_spy_deferral() -> None:
    from pathlib import Path

    roadmap = Path(".planning/ROADMAP.md").read_text(encoding="utf-8")
    phase9 = roadmap.split("### Phase 9:")[1].split("### Phase 10:")[0]
    assert "persist.calls == []" in phase9
    assert "CAP-02" in phase9 or "D-14" in phase9
