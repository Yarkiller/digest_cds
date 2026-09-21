"""preview_digest_email — approved∩ready preview DTO (ADMIN-04, D-86)."""

from __future__ import annotations

from datetime import date

import pytest

from backend.application.use_cases.preview_digest_email import preview_digest_email
from backend.domain.errors import EmptySendPoolError
from backend.domain.shortlist import ShortlistBatch, ShortlistItem
from backend.tests_support.in_memory import InMemoryShortlistRepository


def _item(
    *,
    material_id: int,
    rank: int,
    title: str,
    material_status: str,
    decision: str,
) -> ShortlistItem:
    return ShortlistItem(
        material_id=material_id,
        rank=rank,
        title=title,
        material_status=material_status,
        decision=decision,
        score=0.5,
        score_factors={"factors": [{"label": "A"}, {"label": "B"}]},
    )


def _batch(*items: ShortlistItem) -> ShortlistBatch:
    return ShortlistBatch(
        id=42,
        week_start=date(2026, 9, 15),
        sent_at=None,
        items=items,
    )


def test_preview_lists_only_approved_ready_items() -> None:
    """ADMIN-04 / D-83 / D-86: preview items = approved ∩ ready only."""
    repo = InMemoryShortlistRepository(
        batch=_batch(
            _item(
                material_id=101,
                rank=1,
                title="Ready approved",
                material_status="ready",
                decision="approved",
            ),
            _item(
                material_id=102,
                rank=2,
                title="Draft approved",
                material_status="draft",
                decision="approved",
            ),
            _item(
                material_id=103,
                rank=3,
                title="Ready pending",
                material_status="ready",
                decision="pending",
            ),
            _item(
                material_id=104,
                rank=4,
                title="Ready rejected",
                material_status="ready",
                decision="rejected",
            ),
        )
    )

    preview = preview_digest_email(repo)

    assert [item.material_id for item in preview.items] == [101]
    assert preview.items[0].title == "Ready approved"
    assert preview.subject
    assert preview.body
    assert repo.get_current_batch() is not None
    assert repo.get_current_batch().sent_at is None


def test_preview_empty_approved_ready_raises() -> None:
    """ADMIN-04 / ADMIN-07 empty probe: no approved∩ready → EmptySendPoolError."""
    repo = InMemoryShortlistRepository(
        batch=_batch(
            _item(
                material_id=102,
                rank=1,
                title="Draft approved",
                material_status="draft",
                decision="approved",
            ),
            _item(
                material_id=103,
                rank=2,
                title="Ready pending",
                material_status="ready",
                decision="pending",
            ),
        )
    )

    with pytest.raises(EmptySendPoolError):
        preview_digest_email(repo)

    assert repo.get_current_batch().sent_at is None


def test_preview_no_batch_raises_empty_pool() -> None:
    repo = InMemoryShortlistRepository(batch=None)

    with pytest.raises(EmptySendPoolError):
        preview_digest_email(repo)
