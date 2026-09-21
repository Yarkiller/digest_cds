"""DigestPublisher adapter — atomic claim+publish via claim_and_publish_digest RPC (CR-01/WR-01).

Wraps migration 005's ``public.claim_and_publish_digest(p_batch_id, p_sent_at, p_period_label,
p_title, p_delivery_status, p_recipient_count)`` SECURITY INVOKER function (service_role only).
The RPC claims the unsent batch, inserts digest_issues + items for approved∩ready, and stamps
delivery columns — all in a single transaction, so a publish failure rolls the claim back too.

When ``material_ids`` is provided (G-05-1), ranks on ``digest_shortlist_items`` are rewritten to
match that order before the RPC so published issue positions follow admin block order.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Protocol

from backend.application.ports.digest_publisher import DigestPublication
from backend.domain.errors import AlreadySentError, EmptySendPoolError, PersistenceError


class _SupabaseClient(Protocol):
    def rpc(self, name: str, params: dict[str, Any]) -> Any: ...

    def table(self, name: str) -> Any: ...


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _map_rpc_error(exc: Exception, batch_id: int) -> Exception | None:
    """Translate Postgres errcodes raised by claim_and_publish_digest into domain errors.

    The RPC raises SQLSTATE ``P0001`` when the batch is already sent/missing (D-89) and a
    ``check_violation`` (``23514``) for an empty approved∩ready pool. PostgREST surfaces these
    as an APIError carrying ``code``/``message``; we also match on message text as a fallback.
    """
    code = str(getattr(exc, "code", "") or "")
    message = str(getattr(exc, "message", "") or exc)
    text = f"{code} {message}".lower()
    if code == "P0001" or "already sent" in text or "already claimed" in text:
        return AlreadySentError(batch_id)
    if code == "23514" or "check_violation" in text or "empty approved" in text:
        return EmptySendPoolError(batch_id=batch_id)
    return None


class SupabaseDigestPublisher:
    """DigestPublisher against the claim_and_publish_digest RPC (service_role client)."""

    def __init__(self, client: _SupabaseClient) -> None:
        self._client = client

    def _apply_publication_ranks(self, *, batch_id: int, material_ids: list[int]) -> None:
        """Rewrite shortlist item ranks to match material_ids order (temp swap avoids unique conflicts)."""
        # Two-phase update: first move to high temporary ranks, then to 1..N.
        # digest_shortlist_items typically unique(batch_id, rank).
        temp_base = 10_000
        try:
            for index, material_id in enumerate(material_ids):
                (
                    self._client.table("digest_shortlist_items")
                    .update({"rank": temp_base + index})
                    .eq("batch_id", batch_id)
                    .eq("material_id", material_id)
                    .execute()
                )
            for index, material_id in enumerate(material_ids, start=1):
                (
                    self._client.table("digest_shortlist_items")
                    .update({"rank": index})
                    .eq("batch_id", batch_id)
                    .eq("material_id", material_id)
                    .execute()
                )
        except PersistenceError:
            raise
        except Exception as exc:  # noqa: BLE001 — map SDK failures at boundary
            raise PersistenceError(f"shortlist rank rewrite failed: {exc}") from exc

    def claim_and_publish(
        self,
        *,
        batch_id: int,
        sent_at: datetime,
        period_label: str,
        title: str,
        material_ids: list[int] | None = None,
    ) -> DigestPublication:
        if material_ids:
            self._apply_publication_ranks(batch_id=batch_id, material_ids=material_ids)

        params: dict[str, Any] = {
            "p_batch_id": batch_id,
            "p_sent_at": _iso(sent_at),
            "p_period_label": period_label,
            "p_title": title,
        }
        try:
            result = self._client.rpc("claim_and_publish_digest", params).execute()
        except PersistenceError:
            raise
        except Exception as exc:  # noqa: BLE001 — map SDK/Postgres failures at boundary
            mapped = _map_rpc_error(exc, batch_id)
            if mapped is not None:
                raise mapped from exc
            raise PersistenceError(f"claim_and_publish_digest failed: {exc}") from exc

        data = getattr(result, "data", None)
        row = data[0] if isinstance(data, list) and data else data
        if not isinstance(row, dict):
            raise PersistenceError("claim_and_publish_digest returned no row")

        return DigestPublication(
            batch_id=int(row.get("batch_id", batch_id)),
            issue_number=int(row["issue_number"]),
            issue_url=str(row["issue_url"]),
            delivery_status=str(row.get("delivery_status") or "stubbed"),
            recipient_count=int(row.get("recipient_count") or 0),
        )
