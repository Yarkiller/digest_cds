"""Build AdminShortlist for the current unsent batch (ADMIN-01/05, D-79…D-81)."""

from __future__ import annotations

from backend.application.ports.shortlist_repository import ShortlistRepository
from backend.domain.shortlist import (
    AdminShortlist,
    AdminShortlistItem,
    honest_factor_labels,
)

_MAX_SHORTLIST_ITEMS = 5


def get_admin_shortlist(shortlist: ShortlistRepository) -> AdminShortlist:
    batch = shortlist.get_current_batch()
    if batch is None:
        return AdminShortlist(batch_id=None, items=())

    ranked = sorted(batch.items, key=lambda item: item.rank)[:_MAX_SHORTLIST_ITEMS]
    items = tuple(
        AdminShortlistItem(
            material_id=item.material_id,
            rank=item.rank,
            title=item.title,
            material_status=item.material_status,
            decision=item.decision,
            score=float(item.score) if item.score is not None else None,
            factor_labels=tuple(honest_factor_labels(item.score_factors)),
        )
        for item in ranked
    )
    return AdminShortlist(batch_id=batch.id, items=items)
