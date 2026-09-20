from __future__ import annotations

from dataclasses import dataclass, field

from backend.domain.current_user import CurrentUser
from backend.domain.issue import Issue
from backend.domain.knowledge import KnowledgeChunk
from backend.domain.material import Material


@dataclass(frozen=True)
class InMemoryPingEntry:
    id: str
    user_id: str | None
    kind: str
    payload: dict = field(default_factory=dict)


class InMemoryPingRecorder:
    def __init__(self) -> None:
        self._entries: list[InMemoryPingEntry] = []
        self._next_id = 1

    def record(
        self,
        *,
        user_id: str | None,
        kind: str,
        payload: dict,
    ) -> str:
        entry_id = str(self._next_id)
        self._next_id += 1
        self._entries.append(
            InMemoryPingEntry(
                id=entry_id,
                user_id=user_id,
                kind=kind,
                payload=dict(payload),
            )
        )
        return entry_id

    def entries_for(self, user_id: str | None) -> list[InMemoryPingEntry]:
        return [e for e in self._entries if e.user_id == user_id]

    @property
    def entries(self) -> list[InMemoryPingEntry]:
        return list(self._entries)


class InMemoryProfileRepository:
    def __init__(self) -> None:
        self._by_id: dict[str, CurrentUser] = {}

    def get_or_upsert(self, user_id: str, email: str) -> CurrentUser:
        existing = self._by_id.get(user_id)
        if existing is not None and existing.email == email:
            return existing
        display_name = existing.display_name if existing is not None else None
        user = CurrentUser(
            id=user_id,
            email=email,
            role="authenticated",
            display_name=display_name,
        )
        self._by_id[user_id] = user
        return user

    def set_display_name(self, user_id: str, display_name: str) -> CurrentUser:
        existing = self._by_id.get(user_id)
        if existing is None:
            raise KeyError(f"profile not found: {user_id}")
        user = CurrentUser(
            id=existing.id,
            email=existing.email,
            role=existing.role,
            display_name=display_name,
        )
        self._by_id[user_id] = user
        return user


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


class InMemoryIssueRepository:
    """In-memory IssueRepository — selects latest published_at (D-24)."""

    def __init__(self, issues: list[Issue] | None = None) -> None:
        self._issues: list[Issue] = list(issues or [])

    def seed(self, issues: list[Issue]) -> None:
        self._issues = list(issues)

    def get_latest_published(self) -> Issue | None:
        published = [i for i in self._issues if i.published_at is not None]
        if not published:
            return None
        return max(published, key=lambda i: i.published_at)
