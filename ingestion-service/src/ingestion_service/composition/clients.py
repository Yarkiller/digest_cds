"""Ready YouTube / httpx clients — proxy only here, never in adapters (D-17)."""

from __future__ import annotations

import httpx
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig

from ingestion_service.composition.settings import Settings

_DEFAULT_TIMEOUT = 30.0


def build_youtube_transcript_api(settings: Settings) -> YouTubeTranscriptApi:
    proxy = settings.youtube_proxy_url
    if proxy:
        return YouTubeTranscriptApi(
            proxy_config=GenericProxyConfig(http_url=proxy, https_url=proxy)
        )
    return YouTubeTranscriptApi()


def build_httpx_client(settings: Settings) -> httpx.AsyncClient:
    proxy = settings.youtube_proxy_url
    if proxy:
        return httpx.AsyncClient(proxy=proxy, timeout=_DEFAULT_TIMEOUT)
    return httpx.AsyncClient(timeout=_DEFAULT_TIMEOUT)
