"""get_ballot use-case — never-voted snapshot (VOTE-02, D-40, D-52)."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.application.use_cases.get_ballot import get_ballot
from backend.domain.vote import BallotTopic
from backend.domain.voting_cycle import VotingCycle
from backend.tests_support.in_memory import InMemoryVoteRepository, InMemoryVotingCycleReader


def _open_cycle() -> VotingCycle:
    return VotingCycle(
        id="cycle-1",
        status="open",
        opens_at=datetime(2026, 4, 3, tzinfo=timezone.utc),
        closes_at=datetime(2026, 4, 16, 23, 59, 59, tzinfo=timezone.utc),
    )


def test_get_ballot_never_voted_returns_personal_vote_null_and_topics() -> None:
    cycle = _open_cycle()
    topics = [
        BallotTopic(
            id="topic-1",
            title="RAG в корпоративной среде",
            description="Аудит применения RAG.",
            materials_count=2,
            votes=0,
        ),
        BallotTopic(
            id="topic-2",
            title="Аномалии в логах",
            description="Как искать аномалии.",
            materials_count=0,
            votes=0,
        ),
    ]
    votes = InMemoryVoteRepository(topics_by_cycle={"cycle-1": topics})
    cycles = InMemoryVotingCycleReader([cycle])

    snapshot = get_ballot(votes, cycles, user_id="user-uuid-1")

    assert snapshot.cycle is not None
    assert snapshot.cycle.id == "cycle-1"
    assert snapshot.cycle.status == "open"
    assert snapshot.personal_vote is None
    assert [t.id for t in snapshot.topics] == ["topic-1", "topic-2"]
    assert all(not hasattr(t, "leading") for t in snapshot.topics)
    assert "leading" not in BallotTopic.__dataclass_fields__
    assert snapshot.leaders == ()


def test_get_ballot_computes_leaders_when_tallies_nonzero() -> None:
    cycle = _open_cycle()
    topics = [
        BallotTopic(
            id="topic-1",
            title="RAG в корпоративной среде",
            description="dek",
            materials_count=1,
            votes=3,
        ),
        BallotTopic(
            id="topic-2",
            title="Аномалии в логах",
            description="dek",
            materials_count=0,
            votes=1,
        ),
    ]
    votes = InMemoryVoteRepository(topics_by_cycle={"cycle-1": topics})
    cycles = InMemoryVotingCycleReader([cycle])

    snapshot = get_ballot(votes, cycles, user_id="user-uuid-1")

    assert len(snapshot.leaders) == 1
    assert snapshot.leaders[0].title == "RAG в корпоративной среде"
    assert snapshot.leaders[0].votes == 3
