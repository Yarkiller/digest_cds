"""Env-backed settings for HTTP edge and later JWT/Supabase wiring."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _split_csv(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


@dataclass(frozen=True)
class Settings:
    api_cors_origins: str = ""
    allowed_email_domains: str = ""
    supabase_url: str = ""
    supabase_publishable_key: str = ""
    supabase_secret_key: str = ""
    supabase_jwks_url: str = ""
    supabase_jwt_issuer: str = ""
    # memory (default, unit tests) | live (Supabase adapters via composition/live.py)
    app_container: str = "memory"
    # Local filesystem root for authenticated .ipynb FileResponse (RAZB-03 / A5)
    notebook_root: str = ""
    # stub (default, D-87) | smtp (fail-fast at resolve — not implemented)
    mailer: str = "stub"
    # Absolute site origin for email material links (D-11 / RESEARCH Q2)
    site_url: str = "http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> tuple[str, ...]:
        return _split_csv(self.api_cors_origins)

    @property
    def email_domains(self) -> tuple[str, ...]:
        return _split_csv(self.allowed_email_domains)

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> Settings:
        env = environ if environ is not None else os.environ
        mode = (env.get("APP_CONTAINER") or "memory").strip().lower() or "memory"
        if mode not in ("memory", "live"):
            mode = "memory"
        mailer = (env.get("MAILER") or "stub").strip().lower() or "stub"
        default_site = "http://127.0.0.1:5173"
        site_url = (
            (env.get("SITE_URL") or "").strip()
            or (env.get("PUBLIC_SITE_URL") or "").strip()
            or default_site
        )
        return cls(
            api_cors_origins=env.get("API_CORS_ORIGINS", ""),
            allowed_email_domains=env.get("ALLOWED_EMAIL_DOMAINS", ""),
            supabase_url=env.get("SUPABASE_URL", ""),
            supabase_publishable_key=env.get("SUPABASE_PUBLISHABLE_KEY", ""),
            supabase_secret_key=env.get("SUPABASE_SECRET_KEY", ""),
            supabase_jwks_url=env.get("SUPABASE_JWKS_URL", ""),
            supabase_jwt_issuer=env.get("SUPABASE_JWT_ISSUER", ""),
            app_container=mode,
            notebook_root=env.get("NOTEBOOK_ROOT", ""),
            mailer=mailer,
            site_url=site_url,
        )
