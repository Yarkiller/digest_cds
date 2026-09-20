"""Select the current digest issue — latest published_at (D-24)."""

from __future__ import annotations

from backend.application.ports.issue_repository import IssueRepository
from backend.domain.issue import Issue


def get_current_issue(issues: IssueRepository) -> Issue | None:
    return issues.get_latest_published()
