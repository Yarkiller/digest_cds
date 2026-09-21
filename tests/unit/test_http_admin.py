"""Authenticated GET /admin/shortlist — AUTH-03 / ADMIN-01/05, D-74, D-77…D-81."""

from __future__ import annotations

import json
import time
from datetime import date
from typing import Any

import jwt
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient
from jwt.algorithms import ECAlgorithm

from backend.composition.container import AppContainer, build_in_memory_container
from backend.composition.settings import Settings
from backend.domain.current_user import CurrentUser
from backend.domain.errors import PersistenceError
from backend.domain.shortlist import ShortlistBatch, ShortlistItem
from backend.interface.http.app import create_app
from backend.tests_support.in_memory import InMemoryShortlistRepository


ISSUER = "https://auth.example/auth/v1"


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


def _seeded_shortlist() -> ShortlistBatch:
    return ShortlistBatch(
        id=42,
        week_start=date(2026, 9, 15),
        sent_at=None,
        items=(
            ShortlistItem(
                material_id=101,
                rank=1,
                title="RAG в продакшене",
                material_status="ready",
                decision="pending",
                score=0.92,
                score_factors={
                    "factors": [
                        {"label": "Релевантность"},
                        {"label": "Свежесть"},
                    ]
                },
            ),
            ShortlistItem(
                material_id=102,
                rank=2,
                title="Черновик без факторов",
                material_status="draft",
                decision="pending",
                score=0.4,
                score_factors={"only": 1},
            ),
        ),
    )


def test_admin_shortlist_without_authorization_returns_401() -> None:
    private_key = ec.generate_private_key(ec.SECP256R1())
    container = build_in_memory_container()
    client = _client(_public_jwk(private_key), container)
    response = client.get("/admin/shortlist")
    assert response.status_code == 401


def test_admin_shortlist_employee_returns_403_forbidden() -> None:
    """D-74 / D-77: non-admin profiles.role → 403, never empty shortlist body."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    jwk = _public_jwk(private_key)
    container = build_in_memory_container()
    container.shortlist = InMemoryShortlistRepository(batch=_seeded_shortlist())
    _seed_profile(
        container,
        user_id="user-uuid-1",
        email="alice@sberbank.ru",
        role="employee",
    )
    client = _client(jwk, container)
    token = _mint(private_key, email="alice@sberbank.ru")

    response = client.get(
        "/admin/shortlist",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "forbidden"
    assert "items" not in response.json()


def test_admin_shortlist_admin_returns_ranked_items_with_factor_honesty() -> None:
    """ADMIN-01 / ADMIN-05 / D-79: admin sees ≤5 items; honesty empties factor_labels."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    jwk = _public_jwk(private_key)
    container = build_in_memory_container()
    container.shortlist = InMemoryShortlistRepository(batch=_seeded_shortlist())
    _seed_profile(
        container,
        user_id="admin-uuid-1",
        email="admin@sberbank.ru",
        role="admin",
    )
    client = _client(jwk, container)
    token = _mint(private_key, email="admin@sberbank.ru", sub="admin-uuid-1")

    response = client.get(
        "/admin/shortlist",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["batch_id"] == 42
    assert len(body["items"]) == 2
    assert len(body["items"]) <= 5
    first, second = body["items"]
    assert first["rank"] == 1
    assert first["material_status"] == "ready"
    assert first["decision"] == "pending"
    assert first["score"] == 0.92
    assert first["factor_labels"] == ["Релевантность", "Свежесть"]
    assert second["material_status"] == "draft"
    assert second["factor_labels"] == []


def test_admin_shortlist_empty_batch_returns_200_empty_items() -> None:
    """D-80: empty current batch → 200 items=[] (not 404)."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    jwk = _public_jwk(private_key)
    container = build_in_memory_container()
    container.shortlist = InMemoryShortlistRepository(batch=None)
    _seed_profile(
        container,
        user_id="admin-uuid-1",
        email="admin@sberbank.ru",
        role="admin",
    )
    client = _client(jwk, container)
    token = _mint(private_key, email="admin@sberbank.ru", sub="admin-uuid-1")

    response = client.get(
        "/admin/shortlist",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"batch_id": None, "items": []}


def test_admin_shortlist_persistence_error_returns_503() -> None:
    class _FailingShortlist:
        def get_current_batch(self):
            raise PersistenceError("db down")

    private_key = ec.generate_private_key(ec.SECP256R1())
    jwk = _public_jwk(private_key)
    container = build_in_memory_container()
    container.shortlist = _FailingShortlist()  # type: ignore[assignment]
    _seed_profile(
        container,
        user_id="admin-uuid-1",
        email="admin@sberbank.ru",
        role="admin",
    )
    client = _client(jwk, container)
    token = _mint(private_key, email="admin@sberbank.ru", sub="admin-uuid-1")

    response = client.get(
        "/admin/shortlist",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "shortlist_unavailable"
