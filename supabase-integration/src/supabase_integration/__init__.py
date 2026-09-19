"""Supabase integration public API."""

from pathlib import Path

from supabase_integration.client import create_publishable_client, create_service_role_client
from supabase_integration.ping_recorder import SupabasePingRecorder
from supabase_integration.profile_repository import SupabaseProfileRepository


def migrations_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "migrations"


__all__ = [
    "SupabasePingRecorder",
    "SupabaseProfileRepository",
    "create_publishable_client",
    "create_service_role_client",
    "migrations_dir",
]
