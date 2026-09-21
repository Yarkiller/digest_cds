"""Mailer port — digest email delivery (ADMIN-07/08, D-87)."""

from __future__ import annotations

from typing import Protocol


class Mailer(Protocol):
    def send_digest(
        self,
        *,
        batch_id: int,
        issue_url: str,
        subject: str,
        body_text: str,
        recipient_count: int,
    ) -> dict[str, object]:
        """Return {delivery_status, recipient_count, issue_url} — stub always 'stubbed'."""
        ...
