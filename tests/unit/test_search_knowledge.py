"""RED→GREEN: hybrid knowledge search returns material-facing hits."""

from datetime import datetime, timezone

from backend.domain.knowledge import KnowledgeChunk
from backend.domain.material import Material, MaterialStatus
from backend.application.use_cases.search_knowledge import search_knowledge
from backend.tests_support.in_memory import (
    InMemoryKnowledgeChunkRepository,
    InMemoryMaterialRepository,
)


def test_search_knowledge_returns_material_id_and_snippet() -> None:
    material = Material(
        id=7,
        slug="pgvector",
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
        published_at=datetime(2026, 3, 17, tzinfo=timezone.utc),
        created_at=datetime(2026, 3, 17, tzinfo=timezone.utc),
        updated_at=datetime(2026, 3, 17, tzinfo=timezone.utc),
    )
    materials = InMemoryMaterialRepository([material])
    chunks = InMemoryKnowledgeChunkRepository()
    chunks.replace_for_material(
        7,
        [
            KnowledgeChunk(
                id=1,
                material_id=7,
                chunk_index=0,
                heading="Setup",
                content_md="Use HNSW indexes for semantic search.",
                embedding=[0.9] + [0.0] * 1023,
                embedding_model_id="foundry-embed-v1",
                content_sha256="sha",
                created_at=datetime(2026, 3, 17, tzinfo=timezone.utc),
            )
        ],
    )

    hits = search_knowledge(
        materials=materials,
        chunks=chunks,
        query_embedding=[0.9] + [0.0] * 1023,
        query_text="HNSW",
        role_filter=None,
        limit=5,
    )

    assert len(hits) == 1
    assert hits[0].material_id == 7
    assert hits[0].material_slug == "pgvector"
    assert hits[0].chunk_index == 0
    assert "HNSW" in hits[0].snippet
