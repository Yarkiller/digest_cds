"""RED→GREEN: YouTubeTranscriptAdapter mocked SDK (CAP-01/02, D-06…D-09, D-17)."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest


VIDEO_ID = "dQw4w9WgXcQ"


class _Snippet:
    def __init__(self, text: str) -> None:
        self.text = text


class _Track:
    def __init__(self, language_code: str, texts: list[str]) -> None:
        self.language_code = language_code
        self._texts = texts

    def fetch(self) -> list[_Snippet]:
        return [_Snippet(t) for t in self._texts]


class _FakeApi:
    def __init__(self, tracks: list[_Track]) -> None:
        self._tracks = tracks
        self.listed_ids: list[str] = []

    def list(self, video_id: str) -> list[_Track]:
        self.listed_ids.append(video_id)
        return list(self._tracks)


def test_adapter_prefers_ru_over_en_and_returns_transcript() -> None:
    from data_collection.adapters.youtube_transcript import YouTubeTranscriptAdapter
    from data_collection.dto.transcript import Transcript

    api = _FakeApi(
        [
            _Track("en", ["hello"]),
            _Track("ru", ["привет"]),
        ]
    )
    adapter = YouTubeTranscriptAdapter(api)

    out = asyncio.run(adapter.get(VIDEO_ID))

    assert isinstance(out, Transcript)
    assert out.language == "ru"
    assert out.video_id == VIDEO_ID
    assert "привет" in out.text
    assert api.listed_ids == [VIDEO_ID]


def test_adapter_normalizes_ru_ru_dialect_to_ru() -> None:
    from data_collection.adapters.youtube_transcript import YouTubeTranscriptAdapter

    api = _FakeApi([_Track("ru-RU", ["текст"])])
    adapter = YouTubeTranscriptAdapter(api)

    out = asyncio.run(adapter.get(VIDEO_ID))
    assert out.language == "ru"


def test_adapter_normalizes_en_us_dialect_to_en() -> None:
    from data_collection.adapters.youtube_transcript import YouTubeTranscriptAdapter

    api = _FakeApi([_Track("en-US", ["text"])])
    adapter = YouTubeTranscriptAdapter(api)

    out = asyncio.run(adapter.get(VIDEO_ID))
    assert out.language == "en"


def test_adapter_rejects_rue_and_enm_as_no_preferred_language() -> None:
    from data_collection.adapters.youtube_transcript import YouTubeTranscriptAdapter
    from data_collection.errors.captions import CaptionsNoPreferredLanguage

    api = _FakeApi(
        [
            _Track("rue", ["x"]),
            _Track("enm", ["y"]),
        ]
    )
    adapter = YouTubeTranscriptAdapter(api)

    with pytest.raises(CaptionsNoPreferredLanguage) as exc_info:
        asyncio.run(adapter.get(VIDEO_ID))

    err = exc_info.value
    assert err.video_id == VIDEO_ID
    assert "rue" in err.available_languages
    assert "enm" in err.available_languages


def test_adapter_raises_captions_empty_without_constructing_transcript() -> None:
    from data_collection.adapters.youtube_transcript import YouTubeTranscriptAdapter
    from data_collection.errors.captions import CaptionsEmpty

    api = _FakeApi([_Track("ru", ["   ", "\n"])])
    adapter = YouTubeTranscriptAdapter(api)

    with patch(
        "data_collection.adapters.youtube_transcript.Transcript"
    ) as mock_transcript:
        with pytest.raises(CaptionsEmpty) as exc_info:
            asyncio.run(adapter.get(VIDEO_ID))
        mock_transcript.assert_not_called()

    assert exc_info.value.video_id == VIDEO_ID


def test_adapter_constructor_has_no_environ_reads() -> None:
    import inspect

    from data_collection.adapters import youtube_transcript as mod

    source = inspect.getsource(mod)
    assert "os.environ" not in source
    assert "os.getenv" not in source
