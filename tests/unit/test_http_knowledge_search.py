"""HTTP GET /knowledge/search — JWT gate, no score in JSON (KNOW-01 / D-59 / D-61)."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient
from jwt.algorithms import ECAlgorithm

from backend.application.ports.query_embedder import StubQueryEmbedder
from backend.composition.container import AppContainer, build_in_memory_container
from backend.composition.settings import Settings
from backend.domain.knowledge import KnowledgeChunk
from backend.domain.material import Material, MaterialStatus
from backend.interface.http.app import create_app
from backend.tests_support.in_memory import (
    InMemoryIssueRepository,
    InMemoryKnowledgeChunkRepository,
    InMemoryMaterialRepository,
    InMemoryPingRecorder,
    InMemoryProfileRepository,
    InMemoryVoteRepository,
    InMemoryVotingCycleReader,
)

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


def _ready_material(*, material_id: int = 7, slug: str = "pgvector") -> Material:
    now = datetime(2026, 3, 17, tzinfo=timezone.utc)
    return Material(
        id=material_id,
        slug=slug,
        title="pgvector for Enterprise Search",
        dek="PostgreSQL + pgvector",
        body_markdown="## Setup\n\nUse HNSW indexes for semantic search.",
        format="статья",
        status=MaterialStatus.READY,
        reading_minutes=6,
        provenance_label="внешний текстовый источник",
        source_id=None,
        roles=("ds", "sva"),
        tags=(("pgvector", "pgvector"),),
        related_material_ids=(),
        published_at=now,
        created_at=now,
        updated_at=now,
    )


def _seeded_container(materials: list[Material], chunks_by_material: dict[int, list[KnowledgeChunk]]) -> AppContainer:
    materials_repo = InMemoryMaterialRepository(materials)
    chunks = InMemoryKnowledgeChunkRepository(materials=materials_repo)
    for material_id, chunk_list in chunks_by_material.items():
        chunks.replace_for_material(material_id, chunk_list)
    return AppContainer(
        materials=materials_repo,
        chunks=chunks,
        profiles=InMemoryProfileRepository(),
        pings=InMemoryPingRecorder(),
        issues=InMemoryIssueRepository(),
        voting_cycles=InMemoryVotingCycleReader(),
        votes=InMemoryVoteRepository(),
        embedder=StubQueryEmbedder(),
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


def test_knowledge_search_without_authorization_returns_401() -> None:
    private_key = ec.generate_private_key(ec.SECP256R1())
    client = _client(_public_jwk(private_key))
    response = client.get("/knowledge/search", params={"q": "HNSW"})
    assert response.status_code == 401


def test_knowledge_search_returns_200_without_score_field() -> None:
    """KNOW-01 / D-59: hits expose slug/snippet/title; never score."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    jwk = _public_jwk(private_key)
    material = _ready_material()
    now = datetime(2026, 3, 17, tzinfo=timezone.utc)
    embedder = StubQueryEmbedder()
    query = "HNSW"
    embedding = embedder.embed(query)
    container = _seeded_container(
        [material],
        {
            7: [
                KnowledgeChunk(
                    id=1,
                    material_id=7,
                    chunk_index=0,
                    heading="Setup",
                    content_md="Use HNSW indexes for semantic search.",
                    embedding=embedding,
                    embedding_model_id="foundry-embed-v1",
                    content_sha256="sha",
                    created_at=now,
                )
            ]
        },
    )
    client = _client(jwk, container)
    token = _mint(private_key, email="alice@sberbank.ru")
    response = client.get(
        "/knowledge/search",
        params={"q": query},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "has_more" in body
    assert body["limit"] == 10
    assert body["offset"] == 0
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["slug"] == "pgvector"
    assert "HNSW" in item["snippet"]
    assert item["title"] == "pgvector for Enterprise Search"
    assert item.get("cover_url") is None
    assert "score" not in item
    assert "score" not in body
