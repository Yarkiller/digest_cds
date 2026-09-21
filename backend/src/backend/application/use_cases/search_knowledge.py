from __future__ import annotations

from backend.application.ports.knowledge_chunk_repository import KnowledgeChunkRepository
from backend.domain.errors import KnowledgeQueryValidationError
from backend.domain.knowledge import KnowledgeHit

MAX_QUERY_CODE_POINTS = 500  # Unicode code points; HTTP 400 query_too_long when exceeded
DEFAULT_SEARCH_LIMIT = 10


def search_knowledge(
    *,
    chunks: KnowledgeChunkRepository,
    query_embedding: list[float],
    query_text: str,
    role_filter: str | None,
    limit: int = DEFAULT_SEARCH_LIMIT,
    offset: int = 0,
) -> list[KnowledgeHit]:
    """Hybrid knowledge search via chunk repository (KNOW-01 / D-59 / D-61).

    Blank/whitespace queries raise KnowledgeQueryValidationError before search.
    Ranking scores stay on KnowledgeHit for server-side ordering only.
    """
    q = (query_text or "").strip()
    if not q:
        raise KnowledgeQueryValidationError("empty_query")
    if len(q) > MAX_QUERY_CODE_POINTS:
        raise KnowledgeQueryValidationError("query_too_long")

    if limit < 1:
        limit = DEFAULT_SEARCH_LIMIT
    if offset < 0:
        offset = 0

    return chunks.search(
        query_embedding=query_embedding,
        query_text=q,
        role_filter=role_filter,
        limit=limit,
        offset=offset,
    )
