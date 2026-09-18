"""Supabase integration public API."""

from pathlib import Path


def migrations_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "migrations"


__all__ = ["migrations_dir"]
