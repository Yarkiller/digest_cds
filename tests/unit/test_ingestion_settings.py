"""RED→GREEN: ingestion Settings + proxy clients + 07-01 verify-only (D-16…D-20)."""

from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_settings_from_env_reads_youtube_proxy_url() -> None:
    from ingestion_service.composition.settings import Settings

    settings = Settings.from_env(
        {"YOUTUBE_PROXY_URL": "socks5://192.168.1.68:1080"}
    )
    assert settings.youtube_proxy_url == "socks5://192.168.1.68:1080"


def test_settings_from_env_unset_youtube_proxy_url_is_none() -> None:
    from ingestion_service.composition.settings import Settings

    settings = Settings.from_env({})
    assert settings.youtube_proxy_url is None


def test_build_youtube_transcript_api_injects_generic_proxy_when_set() -> None:
    from ingestion_service.composition.clients import build_youtube_transcript_api
    from ingestion_service.composition.settings import Settings
    from youtube_transcript_api.proxies import GenericProxyConfig

    settings = Settings.from_env(
        {"YOUTUBE_PROXY_URL": "socks5://192.168.1.68:1080"}
    )
    api = build_youtube_transcript_api(settings)
    proxy_config = api._fetcher._proxy_config
    assert proxy_config is not None
    assert isinstance(proxy_config, GenericProxyConfig)


def test_build_youtube_transcript_api_direct_when_unset() -> None:
    from ingestion_service.composition.clients import build_youtube_transcript_api
    from ingestion_service.composition.settings import Settings

    settings = Settings.from_env({})
    api = build_youtube_transcript_api(settings)
    assert api._fetcher._proxy_config is None


def test_build_httpx_client_uses_proxy_when_set() -> None:
    import asyncio

    import httpx
    from ingestion_service.composition.clients import build_httpx_client
    from ingestion_service.composition.settings import Settings

    settings = Settings.from_env(
        {"YOUTUBE_PROXY_URL": "socks5://192.168.1.68:1080"}
    )
    client = build_httpx_client(settings)
    assert isinstance(client, httpx.AsyncClient)
    # httpx 0.28 stores proxy as mounted AsyncHTTPTransport entries
    assert len(client._mounts) > 0
    asyncio.run(client.aclose())


def test_build_httpx_client_direct_when_unset() -> None:
    import asyncio

    import httpx
    from ingestion_service.composition.clients import build_httpx_client
    from ingestion_service.composition.settings import Settings

    settings = Settings.from_env({})
    client = build_httpx_client(settings)
    assert isinstance(client, httpx.AsyncClient)
    assert len(client._mounts) == 0
    asyncio.run(client.aclose())


def test_verify_07_01_socks_deps_remain_in_data_collection_pyproject() -> None:
    """D-18 verify-only: do not re-add — confirm leftovers from 07-01."""
    text = (REPO_ROOT / "data-collection" / "pyproject.toml").read_text(
        encoding="utf-8"
    )
    assert "httpx[socks]" in text
    assert "requests[socks]" in text or "PySocks" in text


def test_verify_07_01_integration_marker_registered() -> None:
    """D-20 verify-only: root pytest still registers integration marker."""
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "integration:" in text or '"integration"' in text
    assert "integration" in text


def test_adapters_do_not_read_environ() -> None:
    adapter_root = (
        REPO_ROOT / "data-collection" / "src" / "data_collection" / "adapters"
    )
    for path in adapter_root.glob("*.py"):
        if path.name == "__init__.py":
            continue
        body = path.read_text(encoding="utf-8")
        assert "os.environ" not in body, path.name
        assert "os.getenv" not in body, path.name
