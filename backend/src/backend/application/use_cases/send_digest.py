"""send_digest — claim, publish issue, stub mail (ADMIN-03/07/08, D-85…D-90)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from backend.application.ports.issue_repository import IssueRepository
from backend.application.ports.mailer import Mailer
from backend.application.ports.ping_recorder import PingRecorder
from backend.application.ports.shortlist_repository import ShortlistRepository
from backend.domain.errors import (
    AlreadySentError,
    DraftInSendPoolError,
    EmptySendPoolError,
    ShortlistNotFoundError,
)
from backend.domain.issue import IssueItem
from backend.domain.shortlist import ShortlistItem

_EDITOR_BYLINE = "Редакция Digest CDS"


@dataclass(frozen=True)
class SendDigestResult:
    batch_id: int
    issue_number: int
    issue_url: str
    delivery_status: str
    recipient_count: int
    message: str


def _approved_drafts(items: tuple[ShortlistItem, ...]) -> list[int]:
    return [
        item.material_id
        for item in items
        if item.decision == "approved" and item.material_status == "draft"
    ]


def _approved_ready(items: tuple[ShortlistItem, ...]) -> list[ShortlistItem]:
    return sorted(
        [
            item
            for item in items
            if item.decision == "approved" and item.material_status == "ready"
        ],
        key=lambda item: item.rank,
    )


def send_digest(
    shortlist: ShortlistRepository,
    issues: IssueRepository,
    mailer: Mailer,
    pings: PingRecorder,
    *,
    actor_user_id: str,
    now: datetime | None = None,
) -> SendDigestResult:
    """Validate pool → claim → publish → mail → audit (D-88 mandatory publish-on-send)."""
    clock = now or datetime.now(timezone.utc)
    batch = shortlist.get_current_batch()
    if batch is None:
        raise EmptySendPoolError()

    if batch.sent_at is not None:
        raise AlreadySentError(batch.id)

    drafts = _approved_drafts(batch.items)
    if drafts:
        raise DraftInSendPoolError(drafts, batch_id=batch.id)

    pool = _approved_ready(batch.items)
    if not pool:
        raise EmptySendPoolError(batch_id=batch.id)

    try:
        claimed = shortlist.claim_sent(batch_id=batch.id, sent_at=clock)
    except AlreadySentError:
        raise
    except ShortlistNotFoundError as exc:
        raise AlreadySentError(batch.id) from exc

    issue_items = tuple(
        IssueItem(
            slug=f"material-{item.material_id}",
            title=item.title,
            position=item.rank,
            format="article",
            reading_minutes=5,
        )
        for item in pool
    )
    published = issues.publish(
        period_label=claimed.week_start.isoformat(),
        title=f"Digest CDS — {claimed.week_start.isoformat()}",
        editor=_EDITOR_BYLINE,
        published_at=clock,
        items=issue_items,
    )
    issue_url = f"/issues/{published.number}"
    titles = "\n".join(f"- {item.title}" for item in pool)
    subject = f"Digest CDS — выпуск {published.number}"
    body_text = (
        f"Новый выпуск Digest CDS №{published.number}.\n"
        f"Читать: {issue_url}\n\n"
        f"Материалы:\n{titles}\n"
    )
    delivery = mailer.send_digest(
        batch_id=claimed.id,
        issue_url=issue_url,
        subject=subject,
        body_text=body_text,
        recipient_count=0,
    )
    delivery_status = str(delivery.get("delivery_status", "stubbed"))
    recipient_count = int(delivery.get("recipient_count", 0) or 0)

    pings.record(
        user_id=actor_user_id,
        kind="digest_send",
        payload={
            "action": "send",
            "batch_id": claimed.id,
            "issue_number": published.number,
            "issue_url": issue_url,
            "delivery_status": delivery_status,
            "recipient_count": recipient_count,
        },
    )

    return SendDigestResult(
        batch_id=claimed.id,
        issue_number=published.number,
        issue_url=issue_url,
        delivery_status=delivery_status,
        recipient_count=recipient_count,
        message="Отправка записана",
    )
