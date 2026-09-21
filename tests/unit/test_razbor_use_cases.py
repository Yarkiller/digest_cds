"""list_razbors / get_razbor use-cases — ordering + not-found (RAZB-01)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.application.use_cases.get_razbor import get_razbor
from backend.application.use_cases.list_razbors import list_razbors
from backend.domain.errors import RazborNotFoundError
from backend.domain.razbor import Razbor, RazborStatus
from backend.tests_support.in_memory import InMemoryRazborRepository


def _razbor(
    *,
    razbor_id: int,
    title: str = "Razbor",
    status: RazborStatus = RazborStatus.PUBLISHED,
    meeting_at: datetime | None = None,
    created_at: datetime | None = None,
) -> Razbor:
    created = created_at or datetime(2026, 3, 1, tzinfo=timezone.utc)
    return Razbor(
        id=razbor_id,
        title=title,
        body_markdown="",
        meeting_at=meeting_at,
        status=status,
        notebook_path=None,
        created_at=created,
    )


def test_list_razbors_orders_meeting_at_desc_nulls_last_then_created_at() -> None:
    """RAZB-01: meeting_at DESC NULLS LAST, created_at DESC; equal meeting keeps created secondary."""
    shared_meeting = datetime(2026, 4, 14, tzinfo=timezone.utc)
    repo = InMemoryRazborRepository(
        [
            _razbor(
                razbor_id=1,
                title="null meeting newer",
                meeting_at=None,
                created_at=datetime(2026, 3, 20, tzinfo=timezone.utc),
            ),
            _razbor(
                razbor_id=2,
                title="same meeting older created",
                meeting_at=shared_meeting,
                created_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
            ),
            _razbor(
                razbor_id=3,
                title="same meeting newer created",
                meeting_at=shared_meeting,
                created_at=datetime(2026, 3, 10, tzinfo=timezone.utc),
            ),
            _razbor(
                razbor_id=4,
                title="earlier meeting",
                meeting_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
                created_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
            ),
        ]
    )
    result = list_razbors(repo)
    assert [r.id for r in result] == [3, 2, 4, 1]


def test_list_razbors_empty_returns_empty_list() -> None:
    """RAZB-01 empty ASSUMPTION: empty repository → []."""
    assert list_razbors(InMemoryRazborRepository()) == []


def test_get_razbor_missing_raises_not_found() -> None:
    """Stub path for 04-06: missing id → RazborNotFoundError."""
    with pytest.raises(RazborNotFoundError):
        get_razbor(InMemoryRazborRepository(), 99)
