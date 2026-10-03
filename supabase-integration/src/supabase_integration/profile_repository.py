"""ProfileRepository adapter — upsert/read public.profiles via injected client."""

from __future__ import annotations

from typing import Any, Protocol

from backend.domain.current_user import CurrentUser
from backend.domain.errors import PersistenceError

_DEFAULT_APP_ROLE = "employee"


class _SupabaseClient(Protocol):
    def table(self, name: str) -> Any: ...


def _row_to_user(row: dict[str, Any]) -> CurrentUser:
    raw_name = row.get("display_name")
    display_name = str(raw_name) if raw_name is not None and str(raw_name).strip() else None
    return CurrentUser(
        id=str(row["id"]),
        email=str(row["email"]),
        role=str(row.get("role") or _DEFAULT_APP_ROLE),
        display_name=display_name,
    )


class SupabaseProfileRepository:
    """Idempotent get_or_upsert against profiles (app_role), safe if Auth trigger exists."""

    def __init__(self, client: _SupabaseClient) -> None:
        self._client = client

    def get_or_upsert(self, user_id: str, email: str) -> CurrentUser:
        try:
            existing = (
                self._client.table("profiles")
                .select("id,email,role,display_name")
                .eq("id", user_id)
                .execute()
            )
            rows = getattr(existing, "data", None) or []
            if rows:
                return _row_to_user(rows[0])

            upserted = (
                self._client.table("profiles")
                .upsert(
                    {
                        "id": user_id,
                        "email": email,
                        "role": _DEFAULT_APP_ROLE,
                    }
                )
                .execute()
            )
        except PersistenceError:
            raise
        except Exception as exc:  # noqa: BLE001 — map all SDK failures at boundary
            raise PersistenceError(f"profiles get_or_upsert failed: {exc}") from exc

        data = getattr(upserted, "data", None) or []
        if not data:
            raise PersistenceError("profiles upsert returned no rows")
        return _row_to_user(data[0])

    def set_display_name(self, user_id: str, display_name: str) -> CurrentUser:
        try:
            updated = (
                self._client.table("profiles")
                .update({"display_name": display_name})
                .eq("id", user_id)
                .execute()
            )
        except PersistenceError:
            raise
        except Exception as exc:  # noqa: BLE001 — map all SDK failures at boundary
            raise PersistenceError(f"profiles set_display_name failed: {exc}") from exc

        data = getattr(updated, "data", None) or []
        if not data:
            raise PersistenceError("profiles set_display_name returned no rows")
        return _row_to_user(data[0])
