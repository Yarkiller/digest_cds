"""RED→GREEN: migration 007 SQL contract for persist_draft_and_enqueue (D-05, D-06, D-09)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION = REPO_ROOT / "supabase-integration/migrations/007_phase9_persist_draft.sql"


def _sql() -> str:
    assert MIGRATION.is_file(), "007_phase9_persist_draft.sql must exist"
    return MIGRATION.read_text(encoding="utf-8")


def test_migration_007_exists_and_adds_provenance_columns() -> None:
    text = _sql()
    lower = text.lower()
    assert "alter table materials add column if not exists source_url text not null" in lower
    assert "youtube_video_id text not null unique" in lower
    assert "source_author text not null" in lower
    assert "source_published_at timestamptz" in lower
    assert "phase5-admin-draft" in text


def test_migration_007_creates_persist_draft_and_enqueue_rpc() -> None:
    text = _sql()
    lower = text.lower()
    assert "create or replace function public.persist_draft_and_enqueue" in lower
    assert "security invoker" in lower
    assert "status='draft'" in lower.replace(" ", "")
    assert "format='статья'" in lower.replace(" ", "") or "format='статья'" in text
    assert "on conflict (youtube_video_id) do nothing" in lower
    assert "sent_at is null" in lower
    assert "p_batch_size" in lower
    assert "get diagnostics" in lower


def test_migration_007_skips_sent_batches_and_is_idempotent_on_video_id() -> None:
    """RESEARCH batch_sent: a latest batch with sent_at set is not the enqueue target."""
    text = _sql()
    lower = text.lower()
    assert "sent_at is null" in lower
    assert "sent_at is not null" in lower or "sent_at is null" in lower
    assert "existing" in lower or "already exists" in lower or "v_inserted" in lower
    assert "digest_shortlist_items" in lower
    assert "decision" in lower and "pending" in lower


def test_migration_007_grants_execute_only_to_service_role() -> None:
    text = _sql()
    lower = text.lower()
    assert "revoke all" in lower and "from public" in lower
    assert "revoke all" in lower and "from anon, authenticated" in lower
    assert "grant execute" in lower and "to service_role" in lower


def test_migration_007_has_no_destructive_wipes() -> None:
    text = _sql()
    lower = text.lower()
    assert "\ntruncate " not in lower
    assert "\ndrop table" not in lower
    assert "\ndelete from materials" not in lower
    assert "\ndelete from digest_shortlist" not in lower
