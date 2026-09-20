"""cast_vote use-case — confirm one vote, idempotent same-topic (VOTE-01, D-52)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.application.use_cases.cast_vote import cast_vote
from backend.domain.errors import InvalidVoteError
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


def _seeded() -> tuple[InMemoryVoteRepository, InMemoryVotingCycleReader]:
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
    cycles = InMemoryVotingCycleReader([_open_cycle()])
    return votes, cycles


def test_cast_vote_stores_exactly_one_vote_and_returns_snapshot() -> None:
    votes, cycles = _seeded()

    snapshot = cast_vote(
        votes,
        cycles,
        user_id="user-uuid-1",
        topic_id="topic-1",
        expected_updated_at=None,
    )

    assert snapshot.personal_vote is not None
    assert snapshot.personal_vote.topic_id == "topic-1"
    assert snapshot.topics[0].votes == 1
    assert votes.get_vote("cycle-1", "user-uuid-1") is not None
    assert votes.vote_count_for("cycle-1") == 1


def test_cast_vote_same_topic_repeat_is_idempotent() -> None:
    votes, cycles = _seeded()

    first = cast_vote(
        votes,
        cycles,
        user_id="user-uuid-1",
        topic_id="topic-1",
        expected_updated_at=None,
    )
    second = cast_vote(
        votes,
        cycles,
        user_id="user-uuid-1",
        topic_id="topic-1",
        expected_updated_at=first.personal_vote.updated_at.isoformat(),
    )

    assert second.personal_vote is not None
    assert second.personal_vote.topic_id == "topic-1"
    assert votes.vote_count_for("cycle-1") == 1
    assert second.topics[0].votes == 1


def test_cast_vote_unknown_topic_raises_invalid_vote() -> None:
    votes, cycles = _seeded()

    with pytest.raises(InvalidVoteError):
        cast_vote(
            votes,
            cycles,
            user_id="user-uuid-1",
            topic_id="topic-missing",
            expected_updated_at=None,
        )
