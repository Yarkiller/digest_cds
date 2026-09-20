"""Wave 0 scaffold — list_archive_issues excludes current (D-31).

Becomes active RED→GREEN when 02-03 lands list_archive_issues.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

list_archive_issues = pytest.importorskip(
    "backend.application.use_cases.list_archive_issues",
    reason="02-03 will add list_archive_issues",
).list_archive_issues
InMemoryIssueRepository = pytest.importorskip(
    "backend.tests_support.in_memory",
    reason="InMemoryIssueRepository required",
).InMemoryIssueRepository
Issue = pytest.importorskip("backend.domain.issue", reason="Issue domain required").Issue


def test_list_archive_excludes_current_latest_published() -> None:
    """D-31: archive lists past published issues only — excludes current."""
    older = Issue(
        id="iss-13",
        number=13,
        period_label="week-13",
        title="Past",
        editor=None,
        published_at=datetime(2026, 3, 10, tzinfo=timezone.utc),
        items=(),
    )
    current = Issue(
        id="iss-14",
        number=14,
        period_label="week-14",
        title="Current",
        editor=None,
        published_at=datetime(2026, 3, 17, tzinfo=timezone.utc),
        items=(),
    )
    repo = InMemoryIssueRepository([older, current])
    archive = list_archive_issues(repo)
    numbers = [i.number for i in archive]
    assert 14 not in numbers
    assert 13 in numbers
