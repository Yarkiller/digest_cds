"""HTTP GET /razbory — JWT gate + chronology list DTO (RAZB-01 / D-66)."""

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
from backend.domain.errors import PersistenceError
from backend.domain.razbor import Razbor, RazborStatus
from backend.interface.http.app import create_app
from backend.tests_support.in_memory import InMemoryRazborRepository

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


def _razbor(
    *,
    razbor_id: int,
    title: str,
    status: RazborStatus,
    meeting_at: datetime | None,
    created_at: datetime,
) -> Razbor:
    return Razbor(
        id=razbor_id,
        title=title,
        body_markdown="",
        meeting_at=meeting_at,
        status=status,
        notebook_path=None,
        created_at=created_at,
    )


def _client(signing_jwk: dict[str, Any], container: AppContainer | None = None) -> TestClient:
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
        container=container or build_in_memory_container(),
        signing_key_resolver=lambda _token: signing_jwk,
    )
    return TestClient(app)


def test_razbory_list_without_authorization_returns_401() -> None:
    """RAZB-01 / D-66: GET /razbory requires Bearer JWT."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    client = _client(_public_jwk(private_key))
    response = client.get("/razbory")
    assert response.status_code == 401


def test_razbory_list_returns_chronology_items_including_announcement() -> None:
    """RAZB-01 / D-68: list DTO has id, title, meeting_at, status; announcement included."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    jwk = _public_jwk(private_key)
    earlier = datetime(2026, 3, 10, tzinfo=timezone.utc)
    later = datetime(2026, 4, 14, tzinfo=timezone.utc)
    created = datetime(2026, 3, 1, tzinfo=timezone.utc)
    container = build_in_memory_container()
    container.razbors = InMemoryRazborRepository(
        [
            _razbor(
                razbor_id=1,
                title="Older published",
                status=RazborStatus.PUBLISHED,
                meeting_at=earlier,
                created_at=created,
            ),
            _razbor(
                razbor_id=2,
                title="RAG в корпоративной среде",
                status=RazborStatus.ANNOUNCEMENT,
                meeting_at=later,
                created_at=created,
            ),
        ]
    )
    client = _client(jwk, container)
    token = _mint(private_key, email="alice@sberbank.ru")
    response = client.get("/razbory", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    items = body["items"]
    assert len(items) == 2
    assert items[0]["id"] == 2
    assert items[0]["title"] == "RAG в корпоративной среде"
    assert items[0]["status"] == "announcement"
    assert items[0]["meeting_at"] is not None
    assert set(items[0].keys()) >= {"id", "title", "meeting_at", "status"}
    assert items[1]["id"] == 1
    assert items[1]["status"] == "published"


def test_razbory_list_orders_null_meeting_at_last() -> None:
    """RAZB-01 ordering: meeting_at DESC NULLS LAST, then created_at DESC."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    jwk = _public_jwk(private_key)
    meeting = datetime(2026, 4, 1, tzinfo=timezone.utc)
    older_created = datetime(2026, 1, 1, tzinfo=timezone.utc)
    newer_created = datetime(2026, 2, 1, tzinfo=timezone.utc)
    container = build_in_memory_container()
    container.razbors = InMemoryRazborRepository(
        [
            _razbor(
                razbor_id=10,
                title="No meeting",
                status=RazborStatus.ANNOUNCEMENT,
                meeting_at=None,
                created_at=newer_created,
            ),
            _razbor(
                razbor_id=11,
                title="Has meeting",
                status=RazborStatus.PUBLISHED,
                meeting_at=meeting,
                created_at=older_created,
            ),
            _razbor(
                razbor_id=12,
                title="Also no meeting older",
                status=RazborStatus.ANNOUNCEMENT,
                meeting_at=None,
                created_at=older_created,
            ),
        ]
    )
    client = _client(jwk, container)
    token = _mint(private_key, email="alice@sberbank.ru")
    response = client.get("/razbory", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    ids = [item["id"] for item in response.json()["items"]]
    assert ids == [11, 10, 12]
