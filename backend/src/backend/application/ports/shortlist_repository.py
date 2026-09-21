"""ShortlistRepository port — current unsent batch for admin triage (ADMIN-01/02, D-81/D-82)."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from backend.domain.shortlist import ShortlistBatch


class ShortlistRepository(Protocol):
    def get_current_batch(self) -> ShortlistBatch | None:
        """Latest unsent batch (sent_at IS NULL), or None when empty (D-80/D-81)."""
        ...

    def set_decision(
        self,
        *,
        batch_id: int,
        material_id: int,
        decision: str,
        actor_user_id: str,
        decided_at: datetime,
    ) -> ShortlistBatch:
        """Persist shortlist_decision for one material; return updated batch (D-82)."""
        ...
