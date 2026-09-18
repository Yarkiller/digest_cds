from __future__ import annotations

from backend.domain.knowledge import KnowledgeChunk
from backend.domain.material import Material


class InMemoryMaterialRepository:
    def __init__(self, materials: list[Material] | None = None) -> None:
        self._by_id: dict[int, Material] = {m.id: m for m in (materials or [])}

    def get(self, material_id: int) -> Material | None:
        return self._by_id.get(material_id)

    def save(self, material: Material) -> Material:
        self._by_id[material.id] = material
        return material


class InMemoryKnowledgeChunkRepository:
    def __init__(self) -> None:
        self._chunks: list[KnowledgeChunk] = []
        self._next_id = 1

    def replace_for_material(self, material_id: int, chunks: list[KnowledgeChunk]) -> list[KnowledgeChunk]:
        self._chunks = [c for c in self._chunks if c.material_id != material_id]
        stored: list[KnowledgeChunk] = []
        for chunk in chunks:
            stored_chunk = KnowledgeChunk(
                id=self._next_id,
                material_id=chunk.material_id,
                chunk_index=chunk.chunk_index,
                heading=chunk.heading,
                content_md=chunk.content_md,
                embedding=list(chunk.embedding),
                embedding_model_id=chunk.embedding_model_id,
                content_sha256=chunk.content_sha256,
                created_at=chunk.created_at,
            )
            self._next_id += 1
            stored.append(stored_chunk)
            self._chunks.append(stored_chunk)
        return stored

    def list_all(self) -> list[KnowledgeChunk]:
        return list(self._chunks)
