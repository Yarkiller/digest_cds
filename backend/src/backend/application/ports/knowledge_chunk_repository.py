from __future__ import annotations

from typing import Protocol

from backend.domain.knowledge import KnowledgeChunk


class KnowledgeChunkRepository(Protocol):
    def replace_for_material(self, material_id: int, chunks: list[KnowledgeChunk]) -> list[KnowledgeChunk]: ...

    def list_all(self) -> list[KnowledgeChunk]: ...
