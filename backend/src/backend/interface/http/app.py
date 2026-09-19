"""FastAPI application factory — HTTP edge only."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.composition.settings import Settings
from backend.interface.http.middleware import RequestIdMiddleware, configure_structlog
from backend.interface.http.routes import health


def create_app(settings: Settings, container: Any | None = None) -> FastAPI:
    """Build the public API app. Auth routes arrive in later plans."""
    configure_structlog()
    app = FastAPI(title="Digest CDS API", version="0.1.0")
    app.state.container = container
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
    app.add_middleware(RequestIdMiddleware)

    app.include_router(health.router)
    return app
