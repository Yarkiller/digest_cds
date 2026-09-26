"""YouTube captions adapter — injected SDK client (CAP-01, D-06…D-09, D-17)."""

from __future__ import annotations

import asyncio
from typing import Any

from data_collection.dto.transcript import Transcript
from data_collection.errors.captions import CaptionsEmpty, CaptionsNoPreferredLanguage


def _base_lang(code: str) -> str:
    return code.split("-")[0].lower()


class YouTubeTranscriptAdapter:
    """TranscriptProvider implementation via list-then-pick (ru → en)."""

    def __init__(self, api: Any) -> None:
        self._api = api

    async def get(self, video_id: str) -> Transcript:
        return await asyncio.to_thread(self._fetch, video_id)

    def _fetch(self, video_id: str) -> Transcript:
        tracks = list(self._api.list(video_id))
        chosen = None
        language = None
        for preferred in ("ru", "en"):
            for track in tracks:
                if _base_lang(track.language_code) == preferred:
                    chosen = track
                    language = preferred
                    break
            if chosen is not None:
                break

        if chosen is None or language is None:
            available = sorted({t.language_code for t in tracks})
            raise CaptionsNoPreferredLanguage(
                video_id=video_id,
                available_languages=available,
            )

        snippets = chosen.fetch()
        joined = "".join(getattr(s, "text", str(s)) for s in snippets).strip()
        if not joined:
            raise CaptionsEmpty(video_id=video_id)

        return Transcript(text=joined, language=language, video_id=video_id)
