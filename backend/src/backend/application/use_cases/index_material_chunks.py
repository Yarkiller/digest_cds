from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from datetime import datetime, timezone

from backend.application.ports.knowledge_chunk_repository import KnowledgeChunkRepository
from backend.application.ports.material_repository import MaterialRepository
from backend.domain.errors import MaterialNotFoundError, MaterialNotReadyError
from backend.domain.knowledge import KnowledgeChunk
from backend.domain.material import MaterialStatus

_HEADING = re.compile(r"(?m)^(#{1,6})\s+(.+)$")


def split_article_into_atoms(body_markdown: str) -> list[tuple[str | None, str]]:
    """Split published article markdown into atomic (heading, content) chunks."""
    text = body_markdown.strip()
    if not text:
        return []

    parts = _HEADING.split(text)
    # parts: [preamble, level, title, body, level, title, body, ...]
    atoms: list[tuple[str | None, str]] = []
    if parts[0].strip():
        atoms.append((None, parts[0].strip()))

    i = 1
    while i + 2 < len(parts):
        heading = parts[i + 1].strip()
        body = parts[i + 2].strip()
        if body:
            atoms.append((heading, body))
        elif heading:
            atoms.append((heading, heading))
        i += 3

    if not atoms:
        atoms.append((None, text))
    return atoms


def index_material_chunks(
    *,
    materials: MaterialRepository,
    chunks: KnowledgeChunkRepository,
    material_id: int,
    embedding_model_id: str,
    embed: Callable[[str], list[float]],
    now: datetime | None = None,
) -> list[KnowledgeChunk]:
    material = materials.get(material_id)
    if material is None:
        raise MaterialNotFoundError(material_id)
    if material.status != MaterialStatus.READY:
        raise MaterialNotReadyError(material_id)

    created_at = now or datetime.now(timezone.utc)
    built: list[KnowledgeChunk] = []
    for index, (heading, content) in enumerate(split_article_into_atoms(material.body_markdown)):
        payload = f"{heading or ''}\n{content}".strip()
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        built.append(
            KnowledgeChunk(
                id=0,
                material_id=material_id,
                chunk_index=index,
                heading=heading,
                content_md=content,
                embedding=embed(payload),
                embedding_model_id=embedding_model_id,
                content_sha256=digest,
                created_at=created_at,
            )
        )
    return chunks.replace_for_material(material_id, built)
