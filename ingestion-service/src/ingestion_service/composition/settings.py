"""Env-backed settings for ingestion composition (D-16)."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    youtube_proxy_url: str | None = None

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> Settings:
        env = environ if environ is not None else os.environ
        raw = env.get("YOUTUBE_PROXY_URL")
        if raw is None:
            return cls(youtube_proxy_url=None)
        stripped = raw.strip()
        return cls(youtube_proxy_url=stripped or None)
