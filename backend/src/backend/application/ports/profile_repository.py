"""Profile persistence port — upsert on first authenticated /me."""

from __future__ import annotations

from typing import Protocol

from backend.domain.current_user import CurrentUser


class ProfileRepository(Protocol):
    def get_or_upsert(self, user_id: str, email: str) -> CurrentUser: ...

    def set_display_name(self, user_id: str, display_name: str) -> CurrentUser: ...
