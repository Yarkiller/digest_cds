"""ProfileRepository adapter — upsert/read public.profiles via injected client."""

from __future__ import annotations

from typing import Any, Protocol

from backend.domain.current_user import CurrentUser
from backend.domain.errors import PersistenceError

_DEFAULT_APP_ROLE = "employee"


class _SupabaseClient(Protocol):
    def table(self, name: str) -> Any: ...


class SupabaseProfileRepository:
    """Idempotent get_or_upsert against profiles (app_role), safe if Auth trigger exists."""

    def __init__(self, client: _SupabaseClient) -> None:
        self._client = client

    def get_or_upsert(self, user_id: str, email: str) -> CurrentUser:
        try:
            existing = (
                self._client.table("profiles")
                .select("id,email,role")
                .eq("id", user_id)
                .execute()
            )
            rows = getattr(existing, "data", None) or []
            if rows:
                row = rows[0]
                return CurrentUser(
                    id=str(row["id"]),
                    email=str(row["email"]),
                    role=str(row.get("role") or _DEFAULT_APP_ROLE),
                )

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
        row = data[0]
        return CurrentUser(
            id=str(row["id"]),
            email=str(row["email"]),
            role=str(row.get("role") or _DEFAULT_APP_ROLE),
        )
