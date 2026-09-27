"""RED→GREEN: SupabaseDraftPersister mocked-client contract (D-01, D-04, D-05)."""

from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
from typing import Any

from data_collection.dto.material_draft import MaterialDraft


VIDEO_ID = "dQw4w9WgXcQ"
SLUG = "kak-ispolzovat-pgvector-dQw4w9WgXcQ"
PLANTED_SECRET = "SUPABASE_SECRET_KEY=s3cr3t-k3y-09"
RAW_POSTGRES = 'duplicate key value violates unique constraint "materials_youtube_video_id_key"'


class APIConnectionError(Exception):
    """Mock of the supabase/httpx network failure type."""


class PostgrestAPIError(Exception):
    """Mock PostgREST/Postgres error with a SQLSTATE `.code`."""

    def __init__(self, code: str, message: str = RAW_POSTGRES) -> None:
        self.code = code
        super().__init__(message)


class _FakeExecuteResult:
    def __init__(self, data: object) -> None:
        self.data = data


class _FakeRpc:
    def __init__(self, owner: "_FakeClient") -> None:
        self._owner = owner

    def execute(self) -> _FakeExecuteResult:
        if self._owner.error is not None:
            raise self._owner.error
        return _FakeExecuteResult(self._owner.data)


class _FakeClient:
    def __init__(self, data: object, error: BaseException | None = None) -> None:
        self.data = data
        self.error = error
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def rpc(self, name: str, params: dict[str, Any]) -> _FakeRpc:
        self.calls.append((name, params))
        return _FakeRpc(self)


def _draft(**overrides: object) -> MaterialDraft:
    published = datetime(2026, 3, 20, 12, 0, tzinfo=timezone.utc)
    base: dict[str, object] = {
        "title": "Как использовать pgvector",
        "dek": "dek",
        "body_markdown": "body",
        "source_url": f"https://www.youtube.com/watch?v={VIDEO_ID}",
        "youtube_video_id": VIDEO_ID,
        "source_author": "Author",
        "provenance_label": "YouTube · Author",
        "source_published_at": published,
        "roles": ["employee", "ds"],
        "slug": SLUG,
        "reading_minutes": 2,
    }
    base.update(overrides)
    return MaterialDraft(**base)


def _happy_data() -> dict[str, object]:
    return {
        "material_id": 101,
        "slug": SLUG,
        "batch_id": 7,
        "rank": 3,
    }


def test_persist_returns_result_from_mocked_rpc() -> None:
    spec = importlib.util.find_spec("ingestion_service.adapters.supabase_persist")
    assert spec is not None, "supabase_persist adapter must exist"

    from ingestion_service.adapters.supabase_persist import SupabaseDraftPersister
    from ingestion_service.application.ports.persist import PersistResult

    client = _FakeClient(_happy_data())
    persister = SupabaseDraftPersister(client, batch_size=5)
    result = persister.persist(_draft())

    assert result == PersistResult(101, SLUG, 7, 3)
    assert client.calls[0][0] == "persist_draft_and_enqueue"
    params = client.calls[0][1]
    assert params["p_youtube_video_id"] == VIDEO_ID
    assert params["p_slug"] == SLUG
    assert params["p_roles"] == ["employee", "ds"]
    assert params["p_batch_size"] == 5
    assert params["p_source_published_at"] == "2026-03-20T12:00:00+00:00"


def test_persist_passes_none_published_at() -> None:
    from ingestion_service.adapters.supabase_persist import SupabaseDraftPersister

    client = _FakeClient(_happy_data())
    SupabaseDraftPersister(client, batch_size=5).persist(
        _draft(source_published_at=None)
    )
    assert client.calls[0][1]["p_source_published_at"] is None


def test_api_connection_error_maps_to_network_error() -> None:
    from ingestion_service.adapters.persist_errors import DraftPersistNetworkError
    from ingestion_service.adapters.supabase_persist import SupabaseDraftPersister

    client = _FakeClient(_happy_data(), error=APIConnectionError(PLANTED_SECRET))
    try:
        SupabaseDraftPersister(client, batch_size=5).persist(_draft())
    except DraftPersistNetworkError as exc:
        _assert_safe_error(exc)
        return
    raise AssertionError("expected DraftPersistNetworkError")


def test_unique_violation_23505_maps_to_conflict_error() -> None:
    from ingestion_service.adapters.persist_errors import DraftPersistConflictError
    from ingestion_service.adapters.supabase_persist import SupabaseDraftPersister

    client = _FakeClient(
        _happy_data(), error=PostgrestAPIError("23505", RAW_POSTGRES)
    )
    try:
        SupabaseDraftPersister(client, batch_size=5).persist(_draft())
    except DraftPersistConflictError as exc:
        _assert_safe_error(exc)
        return
    raise AssertionError("expected DraftPersistConflictError")


def test_rpc_p0001_maps_to_batch_error() -> None:
    from ingestion_service.adapters.persist_errors import DraftPersistBatchError
    from ingestion_service.adapters.supabase_persist import SupabaseDraftPersister

    client = _FakeClient(
        _happy_data(), error=PostgrestAPIError("P0001", RAW_POSTGRES)
    )
    try:
        SupabaseDraftPersister(client, batch_size=5).persist(_draft())
    except DraftPersistBatchError as exc:
        _assert_safe_error(exc)
        return
    raise AssertionError("expected DraftPersistBatchError")


def test_check_violation_maps_to_batch_error() -> None:
    from ingestion_service.adapters.persist_errors import DraftPersistBatchError
    from ingestion_service.adapters.supabase_persist import SupabaseDraftPersister

    client = _FakeClient(
        _happy_data(),
        error=PostgrestAPIError("check_violation", RAW_POSTGRES),
    )
    try:
        SupabaseDraftPersister(client, batch_size=5).persist(_draft())
    except DraftPersistBatchError as exc:
        _assert_safe_error(exc)
        return
    raise AssertionError("expected DraftPersistBatchError")


def test_other_sdk_error_maps_to_rpc_error() -> None:
    from ingestion_service.adapters.persist_errors import DraftPersistRpcError
    from ingestion_service.adapters.supabase_persist import SupabaseDraftPersister

    client = _FakeClient(
        _happy_data(), error=PostgrestAPIError("PGRST116", RAW_POSTGRES)
    )
    try:
        SupabaseDraftPersister(client, batch_size=5).persist(_draft())
    except DraftPersistRpcError as exc:
        _assert_safe_error(exc)
        return
    raise AssertionError("expected DraftPersistRpcError")


def test_unexpected_exception_maps_to_unknown_error() -> None:
    from ingestion_service.adapters.persist_errors import DraftPersistUnknownError
    from ingestion_service.adapters.supabase_persist import SupabaseDraftPersister

    client = _FakeClient(_happy_data(), error=RuntimeError(PLANTED_SECRET))
    try:
        SupabaseDraftPersister(client, batch_size=5).persist(_draft())
    except DraftPersistUnknownError as exc:
        _assert_safe_error(exc)
        return
    raise AssertionError("expected DraftPersistUnknownError")


def _assert_safe_error(exc: Any) -> None:
    assert exc.video_id == VIDEO_ID
    dumped = f"{exc} {exc.context}"
    assert PLANTED_SECRET not in dumped
    assert "SUPABASE_SECRET_KEY" not in dumped
    assert RAW_POSTGRES not in dumped
    assert "Traceback" not in dumped
    assert set(exc.context).issubset({"video_id", "slug", "batch_id", "reason"})
