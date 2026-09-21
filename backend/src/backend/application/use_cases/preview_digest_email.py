"""Build digest email preview for approved∩ready materials (ADMIN-04, D-86)."""

from __future__ import annotations

from dataclasses import dataclass

from backend.application.ports.shortlist_repository import ShortlistRepository
from backend.domain.errors import EmptySendPoolError
from backend.domain.shortlist import ShortlistItem


@dataclass(frozen=True)
class DigestPreviewItem:
    material_id: int
    rank: int
    title: str


@dataclass(frozen=True)
class DigestEmailPreview:
    batch_id: int
    subject: str
    body: str
    items: tuple[DigestPreviewItem, ...]


def _approved_ready(items: tuple[ShortlistItem, ...]) -> list[ShortlistItem]:
    return sorted(
        [
            item
            for item in items
            if item.decision == "approved" and item.material_status == "ready"
        ],
        key=lambda item: item.rank,
    )


def preview_digest_email(shortlist: ShortlistRepository) -> DigestEmailPreview:
    """Return subject/body/items for approved∩ready only; never marks sent_at."""
    batch = shortlist.get_current_batch()
    if batch is None:
        raise EmptySendPoolError()

    pool = _approved_ready(batch.items)
    if not pool:
        raise EmptySendPoolError(batch_id=batch.id)

    preview_items = tuple(
        DigestPreviewItem(
            material_id=item.material_id,
            rank=item.rank,
            title=item.title,
        )
        for item in pool
    )
    titles = "\n".join(f"- {item.title}" for item in preview_items)
    subject = f"Digest CDS — превью ({batch.week_start.isoformat()})"
    body = (
        f"Превью письма для партии {batch.id} ({batch.week_start.isoformat()}).\n"
        f"Материалы (только approved ready):\n{titles}\n"
    )
    return DigestEmailPreview(
        batch_id=batch.id,
        subject=subject,
        body=body,
        items=preview_items,
    )
