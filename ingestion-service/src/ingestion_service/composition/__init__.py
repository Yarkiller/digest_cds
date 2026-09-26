"""Ingestion composition package — Settings and ready-client factories."""

from ingestion_service.composition.clients import (
    build_httpx_client,
    build_youtube_transcript_api,
)
from ingestion_service.composition.settings import Settings

__all__ = [
    "Settings",
    "build_youtube_transcript_api",
    "build_httpx_client",
]
