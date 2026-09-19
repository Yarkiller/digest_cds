"""X-Request-ID correlation and structlog context binding."""

import structlog
from backend.composition.settings import Settings
from backend.interface.http.app import create_app
from fastapi.testclient import TestClient


def _settings() -> Settings:
    return Settings(
        api_cors_origins="http://127.0.0.1:5173",
        allowed_email_domains="@sberbank.ru,@omega.sbrf.ru",
        supabase_url="",
        supabase_publishable_key="",
        supabase_secret_key="",
        supabase_jwks_url="",
        supabase_jwt_issuer="",
    )


def test_response_includes_generated_x_request_id() -> None:
    client = TestClient(create_app(_settings()))
    response = client.get("/health")
    assert response.status_code == 200
    request_id = response.headers.get("x-request-id")
    assert request_id
    assert len(request_id) >= 8


def test_response_echoes_incoming_x_request_id() -> None:
    client = TestClient(create_app(_settings()))
    response = client.get("/health", headers={"X-Request-ID": "trace-abc-123"})
    assert response.status_code == 200
    assert response.headers.get("x-request-id") == "trace-abc-123"


def test_structlog_context_binds_request_id() -> None:
    bound: dict[str, object] = {}

    def capture_processor(logger, method_name, event_dict):  # noqa: ARG001
        bound.update(event_dict)
        return event_dict

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            capture_processor,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

    client = TestClient(create_app(_settings()))
    response = client.get("/health", headers={"X-Request-ID": "bound-rid-99"})
    assert response.status_code == 200
    assert bound.get("request_id") == "bound-rid-99"
