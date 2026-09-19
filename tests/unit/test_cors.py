"""CORS allowlist from API_CORS_ORIGINS must reflect allowed Origin."""

from backend.composition.settings import Settings
from backend.interface.http.app import create_app
from fastapi.testclient import TestClient


def _settings_with_cors(origins: str) -> Settings:
    return Settings(
        api_cors_origins=origins,
        allowed_email_domains="@sberbank.ru,@omega.sbrf.ru",
        supabase_url="",
        supabase_publishable_key="",
        supabase_secret_key="",
        supabase_jwks_url="",
        supabase_jwt_issuer="",
    )


def test_allowed_origin_receives_access_control_allow_origin() -> None:
    origins = (
        "http://127.0.0.1:5173,http://localhost:5173,"
        "http://127.0.0.1:5174,http://localhost:5174"
    )
    client = TestClient(create_app(_settings_with_cors(origins)))
    origin = "http://127.0.0.1:5173"
    response = client.options(
        "/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin


def test_disallowed_origin_does_not_receive_allow_origin() -> None:
    client = TestClient(
        create_app(_settings_with_cors("http://127.0.0.1:5173,http://localhost:5173"))
    )
    response = client.get(
        "/health",
        headers={"Origin": "http://evil.example"},
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" not in {
        k.lower(): v for k, v in response.headers.items()
    } or response.headers.get("access-control-allow-origin") != "http://evil.example"
