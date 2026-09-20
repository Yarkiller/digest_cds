"""Composition root: wire adapters into use-cases."""

from __future__ import annotations

from dataclasses import dataclass

from backend.application.ports.issue_repository import IssueRepository
from backend.application.ports.knowledge_chunk_repository import KnowledgeChunkRepository
from backend.application.ports.material_repository import MaterialRepository
from backend.application.ports.ping_recorder import PingRecorder
from backend.application.ports.profile_repository import ProfileRepository
from backend.application.ports.vote_repository import VoteRepository
from backend.application.ports.voting_cycle_reader import VotingCycleReader
from backend.application.use_cases.index_material_chunks import index_material_chunks
from backend.application.use_cases.publish_material import publish_material
from backend.application.use_cases.search_knowledge import search_knowledge
from backend.domain.issue import Issue
from backend.domain.knowledge import KnowledgeHit
from backend.domain.material import Material
from backend.domain.voting_cycle import VotingCycle
from backend.tests_support.in_memory import (
    InMemoryIssueRepository,
    InMemoryKnowledgeChunkRepository,
    InMemoryMaterialRepository,
    InMemoryPingRecorder,
    InMemoryProfileRepository,
    InMemoryVoteRepository,
    InMemoryVotingCycleReader,
)


@dataclass
class AppContainer:
    materials: MaterialRepository
    chunks: KnowledgeChunkRepository
    profiles: ProfileRepository
    pings: PingRecorder
    issues: IssueRepository
    voting_cycles: VotingCycleReader
    votes: VoteRepository

    def publish(self, material_id: int) -> Material:
        return publish_material(self.materials, material_id)

    def index(self, material_id: int, *, embedding_model_id: str, embed) -> list:
        return index_material_chunks(
            materials=self.materials,
            chunks=self.chunks,
            material_id=material_id,
            embedding_model_id=embedding_model_id,
            embed=embed,
        )

    def search(
        self,
        *,
        query_embedding: list[float],
        query_text: str,
        role_filter: str | None = None,
        limit: int = 5,
    ) -> list[KnowledgeHit]:
        return search_knowledge(
            materials=self.materials,
            chunks=self.chunks,
            query_embedding=query_embedding,
            query_text=query_text,
            role_filter=role_filter,
            limit=limit,
        )


def build_in_memory_container(
    materials: list[Material] | None = None,
    issues: list[Issue] | None = None,
    voting_cycles: list[VotingCycle] | None = None,
) -> AppContainer:
    """Default local wiring until supabase-integration adapters are connected."""
    return AppContainer(
        materials=InMemoryMaterialRepository(materials),
        chunks=InMemoryKnowledgeChunkRepository(),
        profiles=InMemoryProfileRepository(),
        pings=InMemoryPingRecorder(),
        issues=InMemoryIssueRepository(issues),
        voting_cycles=InMemoryVotingCycleReader(voting_cycles),
        votes=InMemoryVoteRepository(),
    )
