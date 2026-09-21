from __future__ import annotations

import math
import re
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any

from backend.domain.current_user import CurrentUser
from backend.domain.errors import VoteConflictError
from backend.domain.issue import Issue
from backend.domain.knowledge import KnowledgeChunk, KnowledgeHit
from backend.domain.material import Material, MaterialStatus
from backend.domain.razbor import Razbor
from backend.domain.shortlist import ShortlistBatch
from backend.domain.vote import BallotTopic, PersonalVote
from backend.domain.voting_cycle import VotingCycle


def _cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


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


class InMemoryShortlistRepository:
    """In-memory ShortlistRepository — empty by default (D-80)."""

    def __init__(self, batch: ShortlistBatch | None = None) -> None:
        self._batch = batch

    def get_current_batch(self) -> ShortlistBatch | None:
        return self._batch

    def seed(self, batch: ShortlistBatch | None) -> None:
        self._batch = batch


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
        self._by_slug: dict[str, Material] = {m.slug: m for m in (materials or [])}

    def get(self, material_id: int) -> Material | None:
        return self._by_id.get(material_id)

    def get_by_slug(self, slug: str) -> Material | None:
        return self._by_slug.get(slug)

    def save(self, material: Material) -> Material:
        self._by_id[material.id] = material
        self._by_slug[material.slug] = material
        return material


class InMemoryKnowledgeChunkRepository:
    """In-memory chunks with hybrid search (cosine 0.7 + FTS 0.3) for unit tests."""

    def __init__(self, materials: Any | None = None) -> None:
        self._chunks: list[KnowledgeChunk] = []
        self._next_id = 1
        self._materials = materials

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

    def search(
        self,
        *,
        query_embedding: list[float],
        query_text: str,
        role_filter: str | None,
        limit: int,
        offset: int,
    ) -> list[KnowledgeHit]:
        tokens = {t.lower() for t in re.findall(r"\w+", query_text, flags=re.UNICODE) if t}
        scored: list[KnowledgeHit] = []

        for chunk in self._chunks:
            material = self._materials.get(chunk.material_id) if self._materials is not None else None
            if material is None:
                continue
            if material.status != MaterialStatus.READY:
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
            scored.append(
                KnowledgeHit(
                    material_id=material.id,
                    material_slug=material.slug,
                    chunk_index=chunk.chunk_index,
                    snippet=snippet,
                    score=score,
                )
            )

        # Dedupe by material_id — best score wins (D-61 / Pitfall 2).
        best: dict[int, KnowledgeHit] = {}
        for hit in scored:
            existing = best.get(hit.material_id)
            if existing is None or hit.score > existing.score:
                best[hit.material_id] = hit

        ranked = sorted(best.values(), key=lambda h: h.score, reverse=True)
        if offset < 0:
            offset = 0
        if limit < 1:
            return []
        return ranked[offset : offset + limit]


class InMemoryVotingCycleReader:
    """In-memory VotingCycleReader — returns seeded cycles as-is (selection in use-case)."""

    def __init__(self, cycles: list[VotingCycle] | None = None) -> None:
        self._cycles: list[VotingCycle] = list(cycles or [])

    def seed(self, cycles: list[VotingCycle]) -> None:
        self._cycles = list(cycles)

    def list_cycles(self) -> list[VotingCycle]:
        return list(self._cycles)


class InMemoryVoteRepository:
    """In-memory VoteRepository keyed by (cycle_id, user_id) — PK one-row guarantee."""

    def __init__(
        self,
        topics_by_cycle: dict[str, list[BallotTopic]] | None = None,
    ) -> None:
        self._topics: dict[str, list[BallotTopic]] = {
            cycle_id: list(topics) for cycle_id, topics in (topics_by_cycle or {}).items()
        }
        self._votes: dict[tuple[str, str], PersonalVote] = {}

    def seed_topics(self, cycle_id: str, topics: list[BallotTopic]) -> None:
        self._topics[cycle_id] = list(topics)

    def list_topics_with_counts(self, cycle_id: str) -> list[BallotTopic]:
        return list(self._topics.get(cycle_id, []))

    def get_vote(self, cycle_id: str, user_id: str) -> PersonalVote | None:
        return self._votes.get((cycle_id, user_id))

    def vote_count_for(self, cycle_id: str) -> int:
        return sum(1 for key in self._votes if key[0] == cycle_id)

    def upsert_vote(
        self,
        *,
        cycle_id: str,
        user_id: str,
        topic_id: str,
        expected_updated_at: datetime | None,
    ) -> PersonalVote:
        key = (cycle_id, user_id)
        existing = self._votes.get(key)

        if existing is None:
            if expected_updated_at is not None:
                raise VoteConflictError(cycle_id, user_id)
        elif existing.topic_id != topic_id:
            # A→B change requires matching expected_updated_at (strict CAS in 03-04)
            if expected_updated_at is None or existing.updated_at != expected_updated_at:
                raise VoteConflictError(cycle_id, user_id)
        # same-topic repeat: idempotent success regardless of expected drift (VOTE-01 assumption)

        previous_topic = existing.topic_id if existing is not None else None
        now = datetime.now(timezone.utc)
        personal = PersonalVote(topic_id=topic_id, updated_at=now)
        self._votes[key] = personal

        topics = self._topics.get(cycle_id, [])
        updated: list[BallotTopic] = []
        for topic in topics:
            votes = topic.votes
            if previous_topic == topic.id and previous_topic != topic_id:
                votes = max(0, votes - 1)
            if topic.id == topic_id and previous_topic != topic_id:
                votes = votes + 1
            updated.append(replace(topic, votes=votes) if votes != topic.votes else topic)
        self._topics[cycle_id] = updated
        return personal


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

    def get_by_number(self, number: int) -> Issue | None:
        for issue in self._issues:
            if issue.number == number and issue.published_at is not None:
                return issue
        return None

    def list_past_published(self) -> list[Issue]:
        current = self.get_latest_published()
        published = [i for i in self._issues if i.published_at is not None]
        if current is None:
            return sorted(published, key=lambda i: i.published_at, reverse=True)
        return sorted(
            [i for i in published if i.id != current.id],
            key=lambda i: i.published_at,
            reverse=True,
        )


class InMemoryRazborRepository:
    """In-memory RazborRepository — meeting_at DESC NULLS LAST, created_at DESC (RAZB-01)."""

    def __init__(self, razbors: list[Razbor] | None = None) -> None:
        self._razbors: list[Razbor] = list(razbors or [])

    def seed(self, razbors: list[Razbor]) -> None:
        self._razbors = list(razbors)

    def list_for_reader(self) -> list[Razbor]:
        return sorted(
            self._razbors,
            key=lambda r: (
                r.meeting_at is None,
                -(r.meeting_at.timestamp()) if r.meeting_at is not None else 0.0,
                -r.created_at.timestamp(),
            ),
        )

    def get(self, razbor_id: int) -> Razbor | None:
        for razbor in self._razbors:
            if razbor.id == razbor_id:
                return razbor
        return None
