"""FastAPI application factory — HTTP edge only."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.composition.settings import Settings
from backend.interface.http.middleware import RequestIdMiddleware, configure_structlog
from backend.interface.http.routes import health, me


def create_app(
    settings: Settings,
    container: Any | None = None,
    *,
    signing_key_resolver: Callable[[str], Mapping[str, Any] | Any] | None = None,
) -> FastAPI:
    """Build the public API app with health + authenticated /me and /me/ping."""
    configure_structlog()
    app = FastAPI(title="Digest CDS API", version="0.1.0")
    app.state.container = container
    app.state.settings = settings
    app.state.signing_key_resolver = signing_key_resolver

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
    app.add_middleware(RequestIdMiddleware)

    app.include_router(health.router)
    app.include_router(me.router)
    return app
