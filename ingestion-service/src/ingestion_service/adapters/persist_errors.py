"""Draft persist adapter errors — module-local taxonomy (D-04)."""

from __future__ import annotations

from typing import Any


class DraftPersistError(Exception):
    """Base persist failure at the adapter boundary."""

    def __init__(
        self,
        reason: str,
        *,
        video_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        self.reason = reason
        self.video_id = video_id
        self.context = context or {}
        super().__init__(f"persist {reason}")
