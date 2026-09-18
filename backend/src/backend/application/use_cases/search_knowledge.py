from __future__ import annotations

import math
import re

from backend.application.ports.knowledge_chunk_repository import KnowledgeChunkRepository
from backend.application.ports.material_repository import MaterialRepository
from backend.domain.knowledge import KnowledgeHit


def _cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def search_knowledge(
    *,
    materials: MaterialRepository,
    chunks: KnowledgeChunkRepository,
    query_embedding: list[float],
    query_text: str,
    role_filter: str | None,
    limit: int = 5,
) -> list[KnowledgeHit]:
    tokens = {t.lower() for t in re.findall(r"\w+", query_text, flags=re.UNICODE) if t}
    hits: list[KnowledgeHit] = []

    for chunk in chunks.list_all():
        material = materials.get(chunk.material_id)
        if material is None:
            continue
        if role_filter and role_filter not in material.roles:
            continue

        vector_score = _cosine(query_embedding, chunk.embedding)
        text_l = chunk.content_md.lower()
        fts_score = 0.0
        if tokens:
            fts_score = sum(1.0 for t in tokens if t in text_l) / len(tokens)
        score = 0.7 * vector_score + 0.3 * fts_score
        if score <= 0:
            continue

        snippet = chunk.content_md.strip()
        if len(snippet) > 180:
            snippet = snippet[:177] + "..."
        hits.append(
            KnowledgeHit(
                material_id=material.id,
                material_slug=material.slug,
                chunk_index=chunk.chunk_index,
                snippet=snippet,
                score=score,
            )
        )

    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[:limit]
