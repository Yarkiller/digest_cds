"""Env-backed settings for ingestion composition (D-16)."""

from __future__ import annotations

import os
from dataclasses import dataclass

from ingestion_service.composition.config_error import ConfigurationError


_DEFAULT_MAX_TRANSCRIPT_CHARS = 80000


def _max_transcript_chars(env: dict[str, str]) -> int:
    raw = env.get("MAX_TRANSCRIPT_CHARS")
    if raw is None or raw.strip() == "":
        return _DEFAULT_MAX_TRANSCRIPT_CHARS
    try:
        value = int(raw.strip())
    except ValueError as exc:
        raise ConfigurationError(
            "MAX_TRANSCRIPT_CHARS must be a positive integer"
        ) from exc
    if value <= 0:
        raise ConfigurationError("MAX_TRANSCRIPT_CHARS must be a positive integer")
    return value


@dataclass(frozen=True)
class Settings:
    youtube_proxy_url: str | None = None
    max_transcript_chars: int = _DEFAULT_MAX_TRANSCRIPT_CHARS
    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-flash"

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> Settings:
        env = environ if environ is not None else os.environ
        raw_proxy = env.get("YOUTUBE_PROXY_URL")
        proxy = raw_proxy.strip() if raw_proxy is not None else None
        proxy = proxy or None

        raw_key = env.get("DEEPSEEK_API_KEY")
        key = raw_key.strip() if raw_key is not None else None
        key = key or None

        raw_base = env.get("DEEPSEEK_BASE_URL")
        base_url = raw_base.strip() if raw_base is not None else "https://api.deepseek.com"

        raw_model = env.get("DEEPSEEK_MODEL")
        model = raw_model.strip() if raw_model is not None else "deepseek-flash"

        return cls(
            youtube_proxy_url=proxy,
            max_transcript_chars=_max_transcript_chars(env),
            deepseek_api_key=key,
            deepseek_base_url=base_url,
            deepseek_model=model,
        )
