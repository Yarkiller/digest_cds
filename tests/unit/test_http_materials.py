"""Wave 0 scaffold — HTTP materials 401/404 shapes.

Becomes active RED→GREEN when 02-04 lands materials router.
"""

from __future__ import annotations

import json
import time
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from jwt.algorithms import ECAlgorithm

materials_routes = pytest.importorskip(
    "backend.interface.http.routes.materials",
    reason="02-04 will add materials router",
)
del materials_routes  # import proves module exists; HTTP tests below need create_app wiring

from fastapi.testclient import TestClient

from backend.composition.container import build_in_memory_container
from backend.composition.settings import Settings
from backend.interface.http.app import create_app

ISSUER = "https://auth.example/auth/v1"


def _public_jwk(private_key: ec.EllipticCurvePrivateKey) -> dict[str, Any]:
    data = json.loads(ECAlgorithm.to_jwk(private_key.public_key()))
    data["kid"] = "test-kid-1"
    data["alg"] = "ES256"
    data["use"] = "sig"
    return data


def _mint(private_key: ec.EllipticCurvePrivateKey, *, email: str) -> str:
    now = int(time.time())
    return jwt.encode(
        {
            "sub": "user-uuid-1",
            "email": email,
            "role": "authenticated",
            "aud": "authenticated",
            "iss": ISSUER,
            "exp": now + 3600,
            "iat": now,
        },
        private_key,
        algorithm="ES256",
        headers={"kid": "test-kid-1"},
    )


def _client(signing_jwk: dict[str, Any]) -> TestClient:
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
        container=build_in_memory_container(),
        signing_key_resolver=lambda _token: signing_jwk,
    )
    return TestClient(app)


def test_materials_by_slug_without_authorization_returns_401() -> None:
    private_key = ec.generate_private_key(ec.SECP256R1())
    client = _client(_public_jwk(private_key))
    response = client.get("/materials/rag-systems")
    assert response.status_code == 401


def test_materials_unknown_slug_returns_404() -> None:
    private_key = ec.generate_private_key(ec.SECP256R1())
    jwk = _public_jwk(private_key)
    client = _client(jwk)
    token = _mint(private_key, email="alice@sberbank.ru")
    response = client.get(
        "/materials/does-not-exist",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
