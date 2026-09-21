"""send_digest — validate, atomic claim+publish, stub mail (ADMIN-03/07/08, D-85…D-90)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from backend.application.ports.digest_publisher import DigestPublisher
from backend.application.ports.mailer import Mailer
from backend.application.ports.ping_recorder import PingRecorder
from backend.application.ports.shortlist_repository import ShortlistRepository
from backend.domain.errors import (
    AlreadySentError,
    DraftInSendPoolError,
    EmptySendPoolError,
    InvalidSendOrderError,
)
from backend.domain.shortlist import ShortlistItem


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


def _ordered_pool(
    pool: list[ShortlistItem],
    material_ids: list[int] | None,
    *,
    batch_id: int,
) -> list[ShortlistItem]:
    """Validate optional material_ids as exact permutation; return publication order."""
    if material_ids is None:
        return pool
    pool_ids = {item.material_id for item in pool}
    if len(material_ids) != len(pool_ids) or set(material_ids) != pool_ids:
        raise InvalidSendOrderError(batch_id=batch_id)
    by_id = {item.material_id: item for item in pool}
    return [by_id[mid] for mid in material_ids]


def send_digest(
    shortlist: ShortlistRepository,
    publisher: DigestPublisher,
    mailer: Mailer,
    pings: PingRecorder,
    *,
    actor_user_id: str,
    now: datetime | None = None,
    material_ids: list[int] | None = None,
) -> SendDigestResult:
    """Validate pool → atomic claim+publish → mail → audit (D-88 mandatory publish-on-send).

    CR-01/WR-01: the claim, digest_issues publish, and delivery-column stamp are a single
    transaction inside ``DigestPublisher.claim_and_publish`` (migration 005 RPC on live), so a
    publish failure can never leave a batch stamped ``sent_at`` with no issue.

    When ``material_ids`` is provided it must be an exact permutation of the approved∩ready
    pool; that order becomes publication and mail order (G-05-1).
    """
    clock = now or datetime.now(timezone.utc)
    batch = shortlist.get_current_batch()
    if batch is None:
        # No unsent batch. Distinguish "already sent this week" (D-89 → AlreadySentError/409,
        # «Уже отправлено») from a genuinely empty pool (→ EmptySendPoolError/400). WR-03: both
        # live and in-memory hide sent batches from get_current_batch, so consult the latest.
        latest = shortlist.get_latest_batch()
        if latest is not None and latest.sent_at is not None:
            raise AlreadySentError(latest.id)
        raise EmptySendPoolError()

    drafts = _approved_drafts(batch.items)
    if drafts:
        raise DraftInSendPoolError(drafts, batch_id=batch.id)

    pool = _approved_ready(batch.items)
    if not pool:
        raise EmptySendPoolError(batch_id=batch.id)

    ordered = _ordered_pool(pool, material_ids, batch_id=batch.id)
    ordered_ids = [item.material_id for item in ordered]

    publication = publisher.claim_and_publish(
        batch_id=batch.id,
        sent_at=clock,
        period_label=batch.week_start.isoformat(),
        title=f"Digest CDS — {batch.week_start.isoformat()}",
        material_ids=ordered_ids,
    )

    issue_url = publication.issue_url
    titles = "\n".join(f"- {item.title}" for item in ordered)
    subject = f"Digest CDS — выпуск {publication.issue_number}"
    body_text = (
        f"Новый выпуск Digest CDS №{publication.issue_number}.\n"
        f"Читать: {issue_url}\n\n"
        f"Материалы:\n{titles}\n"
    )
    mailer.send_digest(
        batch_id=publication.batch_id,
        issue_url=issue_url,
        subject=subject,
        body_text=body_text,
        recipient_count=publication.recipient_count,
    )

    pings.record(
        user_id=actor_user_id,
        kind="digest_send",
        payload={
            "action": "send",
            "batch_id": publication.batch_id,
            "issue_number": publication.issue_number,
            "issue_url": issue_url,
            "delivery_status": publication.delivery_status,
            "recipient_count": publication.recipient_count,
        },
    )

    return SendDigestResult(
        batch_id=publication.batch_id,
        issue_number=publication.issue_number,
        issue_url=issue_url,
        delivery_status=publication.delivery_status,
        recipient_count=publication.recipient_count,
        message="Отправка записана",
    )
