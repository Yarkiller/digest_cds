"""StubMailer + SmtpMailer — honesty path for digest send (D-87)."""

from __future__ import annotations

import logging

from backend.composition.settings import Settings

logger = logging.getLogger(__name__)


class StubMailer:
    """In-process mailer: logs body, returns delivery_status=stubbed (no SMTP)."""

    def __init__(self) -> None:
        self.last_batch_id: int | None = None
        self.last_issue_url: str | None = None
        self.last_subject: str | None = None
        self.last_body_text: str | None = None
        self.last_recipient_count: int | None = None

    def send_digest(
        self,
        *,
        batch_id: int,
        issue_url: str,
        subject: str,
        body_text: str,
        recipient_count: int,
    ) -> dict[str, object]:
        self.last_batch_id = batch_id
        self.last_issue_url = issue_url
        self.last_subject = subject
        self.last_body_text = body_text
        self.last_recipient_count = recipient_count
        logger.info(
            "stub_mailer digest batch_id=%s issue_url=%s recipient_count=%s\n%s",
            batch_id,
            issue_url,
            recipient_count,
            body_text,
        )
        return {
            "delivery_status": "stubbed",
            "recipient_count": 0,
            "issue_url": issue_url,
        }


class SmtpMailer:
    """Placeholder for Phase 6+ SMTP — send is intentionally unimplemented (D-87)."""

    def send_digest(
        self,
        *,
        batch_id: int,
        issue_url: str,
        subject: str,
        body_text: str,
        recipient_count: int,
    ) -> dict[str, object]:
        raise NotImplementedError("SmtpMailer is not implemented; use MAILER=stub")


def resolve_mailer(settings: Settings) -> StubMailer:
    """Wire mailer from settings; MAILER=smtp fails fast at startup (D-87)."""
    mode = (settings.mailer or "stub").strip().lower() or "stub"
    if mode == "stub":
        return StubMailer()
    if mode == "smtp":
        raise RuntimeError(
            "SMTP не настроен, используйте stub (MAILER=stub). "
            "Live SMTP is deferred past Phase 5."
        )
    raise RuntimeError(f"Unknown MAILER={mode!r}; use stub")
