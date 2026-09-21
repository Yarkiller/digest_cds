"""send_digest — publish-on-send, draft/empty/already-sent gates (ADMIN-03/07/08, D-85…D-90)."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from backend.application.use_cases.send_digest import send_digest
from backend.domain.errors import (
    AlreadySentError,
    DraftInSendPoolError,
    EmptySendPoolError,
    PersistenceError,
)
from backend.domain.shortlist import ShortlistBatch, ShortlistItem
from backend.infrastructure.stub_mailer import StubMailer
from backend.tests_support.in_memory import (
    InMemoryDigestPublisher,
    InMemoryIssueRepository,
    InMemoryPingRecorder,
    InMemoryShortlistRepository,
)


def _item(
    *,
    material_id: int,
    rank: int = 1,
    title: str = "Ready approved",
    material_status: str = "ready",
    decision: str = "approved",
) -> ShortlistItem:
    return ShortlistItem(
        material_id=material_id,
        rank=rank,
        title=title,
        material_status=material_status,
        decision=decision,
        score=0.9,
        score_factors={"factors": [{"label": "A"}, {"label": "B"}]},
    )


def _batch(*items: ShortlistItem, sent_at: datetime | None = None) -> ShortlistBatch:
    return ShortlistBatch(
        id=42,
        week_start=date(2026, 9, 15),
        sent_at=sent_at,
        items=items,
    )


def _publisher(
    shortlist: InMemoryShortlistRepository,
    issues: InMemoryIssueRepository,
) -> InMemoryDigestPublisher:
    """Atomic claim+publish backed by the same in-memory repos the assertions inspect."""
    return InMemoryDigestPublisher(lambda: shortlist, lambda: issues)


def test_in_memory_get_current_batch_hides_sent_and_latest_exposes_it() -> None:
    """WR-03: in-memory must match the live `sent_at IS NULL` contract for get_current_batch;
    get_latest_batch still exposes the sent batch (used for the D-89 already-sent signal)."""
    now = datetime(2026, 9, 21, 15, 0, tzinfo=timezone.utc)
    shortlist = InMemoryShortlistRepository(batch=_batch(_item(material_id=101)))

    # Before claim: current batch is the unsent one.
    assert shortlist.get_current_batch() is not None

    shortlist.claim_sent(batch_id=42, sent_at=now)

    # After claim: current batch is hidden (sent_at set), but latest still exposes it.
    assert shortlist.get_current_batch() is None
    latest = shortlist.get_latest_batch()
    assert latest is not None
    assert latest.id == 42
    assert latest.sent_at == now


def test_send_happy_path_publishes_issue_claims_sent_and_stubs_mail() -> None:
    """ADMIN-07/08 / D-88/D-90: publish + claim + stub body with /issues/{n}."""
    shortlist = InMemoryShortlistRepository(
        batch=_batch(
            _item(material_id=101, rank=1, title="RAG в продакшене"),
            _item(
                material_id=102,
                rank=2,
                title="Rejected ready",
                decision="rejected",
            ),
        )
    )
    issues = InMemoryIssueRepository()
    mailer = StubMailer()
    pings = InMemoryPingRecorder()
    actor = "admin-uuid-1"
    now = datetime(2026, 9, 21, 15, 0, tzinfo=timezone.utc)

    result = send_digest(
        shortlist,
        _publisher(shortlist, issues),
        mailer,
        pings,
        actor_user_id=actor,
        now=now,
    )

    assert result.issue_number >= 1
    assert result.issue_url == f"/issues/{result.issue_number}"
    assert result.delivery_status == "stubbed"
    assert result.message == "Отправка записана"

    # WR-03: the claimed batch leaves the unsent pool (matches live `sent_at IS NULL`);
    # get_latest_batch still exposes it with the stamped sent_at.
    assert shortlist.get_current_batch() is None
    latest = shortlist.get_latest_batch()
    assert latest is not None
    assert latest.sent_at == now

    published = issues.get_by_number(result.issue_number)
    assert published is not None
    assert published.published_at == now
    assert len(published.items) == 1
    assert published.items[0].title == "RAG в продакшене"

    assert mailer.last_body_text is not None
    assert f"/issues/{result.issue_number}" in mailer.last_body_text
    assert pings.entries
    audit = pings.entries[-1]
    assert audit.user_id == actor
    assert audit.kind == "digest_send"
    assert audit.payload.get("action") == "send"
    assert audit.payload.get("batch_id") == 42
    assert audit.payload.get("delivery_status") == "stubbed"


def test_send_blocks_approved_draft_in_pool() -> None:
    """ADMIN-03 / D-85: any approved draft → DraftInSendPoolError; not sent."""
    shortlist = InMemoryShortlistRepository(
        batch=_batch(
            _item(material_id=101, rank=1),
            _item(
                material_id=102,
                rank=2,
                title="Черновик",
                material_status="draft",
                decision="approved",
            ),
        )
    )
    issues = InMemoryIssueRepository()
    mailer = StubMailer()
    pings = InMemoryPingRecorder()

    with pytest.raises(DraftInSendPoolError) as exc_info:
        send_digest(
            shortlist,
            _publisher(shortlist, issues),
            mailer,
            pings,
            actor_user_id="admin-uuid-1",
        )

    assert 102 in exc_info.value.draft_material_ids
    assert shortlist.get_current_batch().sent_at is None
    assert issues.get_latest_published() is None
    assert mailer.last_body_text is None
    assert pings.entries == []


def test_send_empty_approved_ready_raises() -> None:
    """ADMIN-07 empty probe: no approved∩ready → EmptySendPoolError."""
    shortlist = InMemoryShortlistRepository(
        batch=_batch(
            _item(
                material_id=101,
                decision="pending",
            ),
        )
    )
    issues = InMemoryIssueRepository()
    with pytest.raises(EmptySendPoolError):
        send_digest(
            shortlist,
            _publisher(shortlist, issues),
            StubMailer(),
            InMemoryPingRecorder(),
            actor_user_id="admin-uuid-1",
        )


def test_send_already_sent_raises_and_does_not_republish() -> None:
    """ADMIN-07 / D-89: second send → AlreadySentError; no second issue/mail."""
    sent_at = datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc)
    shortlist = InMemoryShortlistRepository(
        batch=_batch(_item(material_id=101), sent_at=sent_at)
    )
    issues = InMemoryIssueRepository()
    mailer = StubMailer()
    pings = InMemoryPingRecorder()

    with pytest.raises(AlreadySentError):
        send_digest(
            shortlist,
            _publisher(shortlist, issues),
            mailer,
            pings,
            actor_user_id="admin-uuid-1",
        )

    assert issues.get_latest_published() is None
    assert mailer.last_body_text is None
    # Sent batch stays hidden from the unsent pool; still visible via get_latest_batch (D-89).
    assert shortlist.get_current_batch() is None
    assert shortlist.get_latest_batch().sent_at == sent_at


class _FailingIssueRepository(InMemoryIssueRepository):
    """IssueRepository whose publish always fails (CR-01 atomicity probe)."""

    def publish(self, *args, **kwargs):  # type: ignore[override]
        raise PersistenceError("digest_issues publish failed (simulated)")


def test_send_publish_failure_releases_claim_for_retry() -> None:
    """CR-01: a publish failure inside the atomic op must leave the batch un-claimed for retry."""
    shortlist = InMemoryShortlistRepository(batch=_batch(_item(material_id=101)))
    issues = _FailingIssueRepository()
    mailer = StubMailer()
    pings = InMemoryPingRecorder()

    with pytest.raises(PersistenceError):
        send_digest(
            shortlist,
            _publisher(shortlist, issues),
            mailer,
            pings,
            actor_user_id="admin-uuid-1",
            now=datetime(2026, 9, 21, 15, 0, tzinfo=timezone.utc),
        )

    # The atomic claim+publish rolled back — otherwise the batch is permanently stuck as
    # "sent" with no published issue and no recoverable retry (CR-01).
    batch = shortlist.get_current_batch()
    assert batch is not None
    assert batch.sent_at is None
    # No side effects leaked from the failed send.
    assert issues.get_latest_published() is None
    assert mailer.last_body_text is None
    assert pings.entries == []


def test_send_repeat_after_success_is_idempotent_409_path() -> None:
    """D-89: after successful send, claim fails — no second stub send."""
    shortlist = InMemoryShortlistRepository(batch=_batch(_item(material_id=101)))
    issues = InMemoryIssueRepository()
    mailer = StubMailer()
    pings = InMemoryPingRecorder()
    publisher = _publisher(shortlist, issues)

    first = send_digest(
        shortlist,
        publisher,
        mailer,
        pings,
        actor_user_id="admin-uuid-1",
        now=datetime(2026, 9, 21, 15, 0, tzinfo=timezone.utc),
    )
    first_number = first.issue_number
    first_body = mailer.last_body_text
    ping_count = len(pings.entries)

    with pytest.raises(AlreadySentError):
        send_digest(
            shortlist,
            publisher,
            mailer,
            pings,
            actor_user_id="admin-uuid-1",
        )

    assert issues.get_by_number(first_number) is not None
    assert len([i for i in issues._issues if i.published_at is not None]) == 1
    assert mailer.last_body_text == first_body
    assert len(pings.entries) == ping_count


def test_send_material_ids_reversed_order_becomes_publication_and_mail_order() -> None:
    """G-05-1 / ADMIN-07: material_ids permutation is publication + mail order (not rank)."""
    shortlist = InMemoryShortlistRepository(
        batch=_batch(
            _item(material_id=101, rank=1, title="First by rank"),
            _item(material_id=102, rank=2, title="Second by rank"),
        )
    )
    issues = InMemoryIssueRepository()
    mailer = StubMailer()
    pings = InMemoryPingRecorder()

    result = send_digest(
        shortlist,
        _publisher(shortlist, issues),
        mailer,
        pings,
        actor_user_id="admin-uuid-1",
        now=datetime(2026, 9, 21, 15, 0, tzinfo=timezone.utc),
        material_ids=[102, 101],
    )

    published = issues.get_by_number(result.issue_number)
    assert published is not None
    assert [item.title for item in published.items] == ["Second by rank", "First by rank"]
    assert mailer.last_body_text is not None
    second_at = mailer.last_body_text.index("Second by rank")
    first_at = mailer.last_body_text.index("First by rank")
    assert second_at < first_at


def test_send_material_ids_mismatched_set_raises() -> None:
    """G-05-1: material_ids must be exact permutation of approved∩ready → domain error."""
    import backend.domain.errors as domain_errors

    InvalidSendOrderError = getattr(domain_errors, "InvalidSendOrderError", None)
    assert InvalidSendOrderError is not None, "InvalidSendOrderError domain error missing"

    shortlist = InMemoryShortlistRepository(
        batch=_batch(
            _item(material_id=101, rank=1, title="A"),
            _item(material_id=102, rank=2, title="B"),
        )
    )
    issues = InMemoryIssueRepository()
    mailer = StubMailer()
    pings = InMemoryPingRecorder()

    with pytest.raises(InvalidSendOrderError):
        send_digest(
            shortlist,
            _publisher(shortlist, issues),
            mailer,
            pings,
            actor_user_id="admin-uuid-1",
            material_ids=[101],
        )

    with pytest.raises(InvalidSendOrderError):
        send_digest(
            shortlist,
            _publisher(shortlist, issues),
            mailer,
            pings,
            actor_user_id="admin-uuid-1",
            material_ids=[101, 102, 999],
        )

    assert shortlist.get_current_batch().sent_at is None
    assert issues.get_latest_published() is None
    assert mailer.last_body_text is None
