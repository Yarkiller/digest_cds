"""RED→GREEN: GET/PUT /admin/pipeline/config tracer — PIPE-01/PIPE-03, D-08/D-10/D-11/D-13.

Reuses the ES256 JWT harness from tests/unit/test_http_admin.py and attaches the
in-memory PipelineConfigRepository/Validator fakes to the container post-build
(16-01 does not touch composition/container.py; field declaration + wiring is 16-02).
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any

import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient
from jwt.algorithms import ECAlgorithm

from backend.composition.container import AppContainer, build_in_memory_container
from backend.composition.settings import Settings
from backend.domain.current_user import CurrentUser
from backend.domain.pipeline_config import PipelineConfig
from backend.interface.http.app import create_app
from backend.tests_support.in_memory import (
    InMemoryPipelineConfigRepository,
    InMemoryPipelineConfigValidator,
)

ISSUER = "https://auth.example/auth/v1"
CONFIG_URL = "/admin/pipeline/config"


def _public_jwk(private_key: ec.EllipticCurvePrivateKey) -> dict[str, Any]:
    data = json.loads(ECAlgorithm.to_jwk(private_key.public_key()))
    data["kid"] = "test-kid-1"
    data["alg"] = "ES256"
    data["use"] = "sig"
    return data


def _mint(
    private_key: ec.EllipticCurvePrivateKey,
    *,
    email: str,
    sub: str = "user-uuid-1",
    role: str = "authenticated",
) -> str:
    now = int(time.time())
    return jwt.encode(
        {
            "sub": sub,
            "email": email,
            "role": role,
            "aud": "authenticated",
            "iss": ISSUER,
            "exp": now + 3600,
            "iat": now,
        },
        private_key,
        algorithm="ES256",
        headers={"kid": "test-kid-1"},
    )


def _client(signing_jwk: dict[str, Any], container: AppContainer) -> TestClient:
    settings = Settings(
        api_cors_origins="http://127.0.0.1:5173",
        allowed_email_domains="@sberbank.ru,@omega.sbrf.ru",
        supabase_url="",
        supabase_publishable_key="",
        supabase_secret_key="",
        supabase_jwks_url="https://unused.example/jwks.json",
        supabase_jwt_issuer=ISSUER,
    )
    app = create_app(
        settings,
        container=container,
        signing_key_resolver=lambda _token: signing_jwk,
    )
    return TestClient(app)


def _seed_profile(container: AppContainer, *, user_id: str, email: str, role: str) -> None:
    container.profiles._by_id[user_id] = CurrentUser(
        id=user_id,
        email=email,
        role=role,
        display_name=None,
    )


def _admin_env(
    *,
    config: PipelineConfig | None = None,
    attach_repo: bool = True,
    attach_validator: bool = True,
) -> tuple[TestClient, dict[str, str], Any]:
    """Admin-authenticated client with the tracer fakes attached post-build."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    jwk = _public_jwk(private_key)
    container = build_in_memory_container()
    if attach_repo:
        container.pipeline_config = InMemoryPipelineConfigRepository(config)
    if attach_validator:
        container.pipeline_config_validator = InMemoryPipelineConfigValidator()
    _seed_profile(
        container,
        user_id="admin-uuid-1",
        email="admin@sberbank.ru",
        role="admin",
    )
    client = _client(jwk, container)
    token = _mint(private_key, email="admin@sberbank.ru", sub="admin-uuid-1")
    return client, {"Authorization": f"Bearer {token}"}, container


def test_get_returns_empty_state_when_absent() -> None:
    """D-11: absent singleton row → 200 with exactly {yaml:'', updated_at:null}."""
    client, headers, _container = _admin_env(config=None)

    response = client.get(CONFIG_URL, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body == {"yaml": "", "updated_at": None}
    assert set(body.keys()) == {"yaml", "updated_at"}


def test_get_returns_saved_config() -> None:
    """PIPE-01/PIPE-03: a stored config round-trips through the read route (D-11)."""
    stored = PipelineConfig(
        yaml="template: podcast\nroles:\n  - analyst\nlanguage: ru\nmax_chars: 8000\n",
        updated_at=datetime(2026, 10, 4, 9, 0, tzinfo=timezone.utc),
    )
    client, headers, _container = _admin_env(config=stored)

    response = client.get(CONFIG_URL, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"yaml", "updated_at"}
    assert body["yaml"] == stored.yaml
    assert body["updated_at"] is not None


def test_put_then_get_round_trip_returns_saved_yaml() -> None:
    """PIPE-01/PIPE-03, D-11: PUT a valid document, then GET returns the identical yaml."""
    yaml_text = "template: lecture\nroles:\n  - employee\nlanguage: ru\nmax_chars: 4000\n"
    client, headers, container = _admin_env(config=None)

    put = client.put(CONFIG_URL, headers=headers, json={"yaml": yaml_text})

    assert put.status_code == 200
    put_body = put.json()
    assert set(put_body.keys()) == {"yaml", "updated_at"}
    assert put_body["yaml"] == yaml_text
    assert put_body["updated_at"] is not None
    # The validator port ran before the write (validate-then-persist).
    assert container.pipeline_config_validator.calls == [yaml_text]

    get = client.get(CONFIG_URL, headers=headers)

    assert get.status_code == 200
    assert get.json()["yaml"] == yaml_text


def test_get_put_require_admin_unauth_401_and_employee_403() -> None:
    """D-10 / T-16-01: both routes are admin-gated; 401 unauthenticated, 403 non-admin."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    jwk = _public_jwk(private_key)

    anon_container = build_in_memory_container()
    anon_container.pipeline_config = InMemoryPipelineConfigRepository()
    anon_container.pipeline_config_validator = InMemoryPipelineConfigValidator()
    anon_client = _client(jwk, anon_container)

    assert anon_client.get(CONFIG_URL).status_code == 401
    assert anon_client.put(CONFIG_URL, json={"yaml": "template: lecture"}).status_code == 401

    employee_container = build_in_memory_container()
    employee_container.pipeline_config = InMemoryPipelineConfigRepository()
    employee_container.pipeline_config_validator = InMemoryPipelineConfigValidator()
    _seed_profile(
        employee_container,
        user_id="user-uuid-1",
        email="alice@sberbank.ru",
        role="employee",
    )
    employee_client = _client(jwk, employee_container)
    employee_token = _mint(private_key, email="alice@sberbank.ru")
    employee_headers = {"Authorization": f"Bearer {employee_token}"}

    get = employee_client.get(CONFIG_URL, headers=employee_headers)
    assert get.status_code == 403
    assert get.json()["detail"] == "forbidden"
    assert "yaml" not in get.json()

    put = employee_client.put(
        CONFIG_URL,
        headers=employee_headers,
        json={"yaml": "template: lecture"},
    )
    assert put.status_code == 403
    assert put.json()["detail"] == "forbidden"
    assert "yaml" not in put.json()


def test_dto_exposes_only_yaml_and_updated_at_keys() -> None:
    """PIPE-03 / T-16-14: every GET/PUT success body exposes exactly {yaml, updated_at}."""
    yaml_text = "template: lecture\nroles:\n  - ds\nlanguage: ru\nmax_chars: 2000\n"
    client, headers, _container = _admin_env(config=None)

    empty_get = client.get(CONFIG_URL, headers=headers)
    assert empty_get.status_code == 200
    assert set(empty_get.json().keys()) == {"yaml", "updated_at"}

    put = client.put(CONFIG_URL, headers=headers, json={"yaml": yaml_text})
    assert put.status_code == 200
    assert set(put.json().keys()) == {"yaml", "updated_at"}

    saved_get = client.get(CONFIG_URL, headers=headers)
    assert saved_get.status_code == 200
    assert set(saved_get.json().keys()) == {"yaml", "updated_at"}


def test_missing_pipeline_config_returns_503() -> None:
    """D-11 guard: container with no pipeline_config → GET/PUT 503 not_configured."""
    client, headers, _container = _admin_env(attach_repo=False, attach_validator=False)

    get = client.get(CONFIG_URL, headers=headers)
    assert get.status_code == 503
    assert get.json()["detail"] == "pipeline_config_not_configured"

    put = client.put(CONFIG_URL, headers=headers, json={"yaml": "template: lecture"})
    assert put.status_code == 503
    assert put.json()["detail"] == "pipeline_config_not_configured"
