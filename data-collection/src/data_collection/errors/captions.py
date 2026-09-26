"""Captions adapter errors — module-local taxonomy only (D-11, D-12)."""

from __future__ import annotations

from typing import Any


class CaptionsError(Exception):
    """Base captions failure at the adapter boundary."""

    def __init__(self, video_id: str, **context: Any) -> None:
        self.video_id = video_id
        self.context = context
        for key, value in context.items():
            setattr(self, key, value)
        super().__init__(f"captions error for {video_id}: {context}")


class CaptionsNoPreferredLanguage(CaptionsError):
    """Tracks exist but none normalize to ru/en (D-09)."""

    def __init__(self, video_id: str, available_languages: list[str]) -> None:
        super().__init__(video_id, available_languages=list(available_languages))
        self.available_languages = list(available_languages)


class CaptionsEmpty(CaptionsError):
    """Joined caption text is blank after strip (CAP-02)."""

    def __init__(self, video_id: str) -> None:
        super().__init__(video_id)
