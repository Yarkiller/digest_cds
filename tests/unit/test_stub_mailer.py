"""StubMailer honesty + SMTP fail-fast (ADMIN-07/08, D-87)."""

from __future__ import annotations

import pytest

from backend.composition.settings import Settings
from backend.infrastructure.stub_mailer import SmtpMailer, StubMailer, resolve_mailer


def test_stub_mailer_returns_stubbed_delivery_and_zero_recipients() -> None:
    """D-87: delivery_status=stubbed; recipient_count=0; body retains issue_url."""
    mailer = StubMailer()
    issue_url = "/issues/7"
    body = f"Читать выпуск: {issue_url}"

    result = mailer.send_digest(
        batch_id=42,
        issue_url=issue_url,
        subject="Digest CDS — выпуск 7",
        body_text=body,
        recipient_count=0,
    )

    assert result["delivery_status"] == "stubbed"
    assert result["recipient_count"] == 0
    assert result["issue_url"] == issue_url
    assert issue_url in mailer.last_body_text
    assert mailer.last_subject == "Digest CDS — выпуск 7"
    assert mailer.last_batch_id == 42


def test_smtp_mailer_send_raises_not_implemented() -> None:
    """D-87: SmtpMailer exists but send is NotImplementedError."""
    mailer = SmtpMailer()
    with pytest.raises(NotImplementedError):
        mailer.send_digest(
            batch_id=1,
            issue_url="/issues/1",
            subject="x",
            body_text="y",
            recipient_count=0,
        )


def test_settings_mailer_defaults_to_stub() -> None:
    settings = Settings.from_env({})
    assert settings.mailer == "stub"


def test_resolve_mailer_smtp_fails_fast_at_startup() -> None:
    """D-87: MAILER=smtp → clear startup error; no send attempt."""
    settings = Settings.from_env({"MAILER": "smtp"})
    assert settings.mailer == "smtp"
    with pytest.raises(RuntimeError, match="SMTP не настроен"):
        resolve_mailer(settings.mailer)
