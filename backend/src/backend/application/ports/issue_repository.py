"""Issue persistence port — published digest issues for readers."""

from __future__ import annotations

from typing import Protocol

from backend.domain.issue import Issue


class IssueRepository(Protocol):
    def get_latest_published(self) -> Issue | None:
        """Return the published issue with the latest published_at (D-24), or None."""
        ...
