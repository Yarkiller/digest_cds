"""get_admin_shortlist use-case — ADMIN-01/05, D-79…D-81."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from backend.application.use_cases.get_admin_shortlist import get_admin_shortlist
from backend.domain.errors import PersistenceError
from backend.domain.shortlist import ShortlistBatch, ShortlistItem
from backend.tests_support.in_memory import InMemoryShortlistRepository
import pytest


def _item(
    *,
    material_id: int = 1,
    rank: int = 1,
    title: str = "Кандидат",
    material_status: str = "ready",
    decision: str = "pending",
    score: float | None = 0.91,
    score_factors: dict | None = None,
) -> ShortlistItem:
    return ShortlistItem(
        material_id=material_id,
        rank=rank,
        title=title,
        material_status=material_status,
        decision=decision,
        score=score,
        score_factors=score_factors
        or {
            "factors": [
                {"label": "Релевантность"},
                {"label": "Свежесть"},
            ]
        },
    )


def test_get_admin_shortlist_empty_batch_returns_empty_items() -> None:
    """D-80 / D-81: no current unsent batch → honest empty DTO (not an exception)."""
    repo = InMemoryShortlistRepository(batch=None)
    result = get_admin_shortlist(repo)
    assert result.batch_id is None
    assert result.items == ()


def test_get_admin_shortlist_caps_at_five_ranked_items() -> None:
    """ADMIN-01: ≤5 ranked candidates."""
    items = tuple(
        _item(material_id=i, rank=i, title=f"Item {i}") for i in range(1, 8)
    )
    batch = ShortlistBatch(
        id=10,
        week_start=date(2026, 9, 15),
        sent_at=None,
        items=items,
    )
    result = get_admin_shortlist(InMemoryShortlistRepository(batch=batch))
    assert result.batch_id == 10
    assert len(result.items) == 5
    assert [it.rank for it in result.items] == [1, 2, 3, 4, 5]


def test_get_admin_shortlist_maps_factor_honesty_and_passes_score() -> None:
    """ADMIN-05 / D-79: ≥2 labels kept; <2 → empty factor_labels; score passed through."""
    batch = ShortlistBatch(
        id=1,
        week_start=date(2026, 9, 15),
        sent_at=None,
        items=(
            _item(
                material_id=1,
                rank=1,
                score=0.88,
                score_factors={"A": 1, "B": 2},
            ),
            _item(
                material_id=2,
                rank=2,
                material_status="draft",
                score=Decimal("0.5"),
                score_factors={"only": 1},
            ),
        ),
    )
    result = get_admin_shortlist(InMemoryShortlistRepository(batch=batch))
    assert result.items[0].factor_labels == ("A", "B")
    assert result.items[0].score == 0.88
    assert result.items[1].factor_labels == ()
    assert result.items[1].material_status == "draft"
    assert float(result.items[1].score) == 0.5


def test_get_admin_shortlist_propagates_persistence_error() -> None:
    class _Failing:
        def get_current_batch(self):
            raise PersistenceError("db down")

    with pytest.raises(PersistenceError):
        get_admin_shortlist(_Failing())
