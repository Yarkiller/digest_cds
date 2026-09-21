"""Admin shortlist domain DTOs and ADMIN-05 score_factors honesty (D-79)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Mapping


def honest_factor_labels(score_factors: Mapping[str, Any] | None) -> list[str]:
    """Return readable factor labels only when ≥2 exist; else [] for «обоснование недоступно».

    Accepts either ``{"factors": [{"label": "..."}, ...]}`` or a flat map whose keys
    are human labels (excluding the reserved ``factors`` key).
    """
    if not score_factors:
        return []
    factors = score_factors.get("factors")
    # WR-02: only treat the structured ``factors`` list as authoritative when it is
    # non-empty. An empty ``factors: []`` alongside flat human keys must fall through
    # to the flat-key branch, not shadow it with «обоснование недоступно».
    if isinstance(factors, list) and factors:
        labels = [
            str(f.get("label", "")).strip()
            for f in factors
            if isinstance(f, dict)
        ]
        labels = [x for x in labels if x]
    else:
        labels = [
            str(k).strip()
            for k, _v in score_factors.items()
            if str(k).strip() and k != "factors"
        ]
    if len(labels) < 2:
        return []
    return labels


@dataclass(frozen=True)
class ShortlistItem:
    material_id: int
    rank: int
    title: str
    material_status: str
    decision: str
    score: float | None
    score_factors: Mapping[str, Any]
    decided_by: str | None = None
    decided_at: datetime | None = None


@dataclass(frozen=True)
class ShortlistBatch:
    id: int
    week_start: date
    sent_at: datetime | None
    items: tuple[ShortlistItem, ...]


@dataclass(frozen=True)
class AdminShortlistItem:
    material_id: int
    rank: int
    title: str
    material_status: str
    decision: str
    score: float | None
    factor_labels: tuple[str, ...]


@dataclass(frozen=True)
class AdminShortlist:
    batch_id: int | None
    items: tuple[AdminShortlistItem, ...]
