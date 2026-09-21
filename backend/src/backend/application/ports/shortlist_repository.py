"""ShortlistRepository port — current unsent batch for admin triage (ADMIN-01, D-81)."""

from __future__ import annotations

from typing import Protocol

from backend.domain.shortlist import ShortlistBatch


class ShortlistRepository(Protocol):
    def get_current_batch(self) -> ShortlistBatch | None:
        """Latest unsent batch (sent_at IS NULL), or None when empty (D-80/D-81)."""
        ...
