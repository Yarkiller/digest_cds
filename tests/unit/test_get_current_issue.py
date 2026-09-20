"""get_current_issue use-case — D-24 latest published_at wins; empty when none."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.application.use_cases.get_current_issue import get_current_issue
from backend.domain.issue import Issue, IssueItem
from backend.tests_support.in_memory import InMemoryIssueRepository


def _item(slug: str, position: int) -> IssueItem:
    return IssueItem(
        slug=slug,
        title=f"Title {slug}",
        position=position,
        format="Статья",
        reading_minutes=5,
        dek=None,
    )


def _issue(
    *,
    issue_id: str,
    number: int,
    published_at: datetime,
    items: tuple[IssueItem, ...] = (),
) -> Issue:
    return Issue(
        id=issue_id,
        number=number,
        period_label=f"week-{number}",
        title=f"Issue {number}",
        editor="Редакция Digest CDS",
        published_at=published_at,
        items=items,
    )


def test_get_current_issue_returns_latest_published_by_published_at() -> None:
    older = _issue(
        issue_id="iss-13",
        number=13,
        published_at=datetime(2026, 3, 10, tzinfo=timezone.utc),
        items=(_item("old-mat", 1),),
    )
    newer = _issue(
        issue_id="iss-14",
        number=14,
        published_at=datetime(2026, 3, 17, tzinfo=timezone.utc),
        items=(_item("rag-systems", 1), _item("anomaly-detection", 2)),
    )
    repo = InMemoryIssueRepository([older, newer])

    current = get_current_issue(repo)

    assert current is not None
    assert current.number == 14
    assert current.id == "iss-14"
    assert [i.slug for i in current.items] == ["rag-systems", "anomaly-detection"]


def test_get_current_issue_returns_none_when_no_published() -> None:
    repo = InMemoryIssueRepository([])
    assert get_current_issue(repo) is None


def test_get_current_issue_returns_issue_with_empty_items() -> None:
    bare = _issue(
        issue_id="iss-15",
        number=15,
        published_at=datetime(2026, 3, 24, tzinfo=timezone.utc),
        items=(),
    )
    repo = InMemoryIssueRepository([bare])
    current = get_current_issue(repo)
    assert current is not None
    assert current.number == 15
    assert current.items == ()
