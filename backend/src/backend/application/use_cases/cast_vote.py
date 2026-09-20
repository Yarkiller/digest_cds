"""Cast or confirm one vote for the active open cycle (VOTE-01, D-52)."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.application.ports.vote_repository import VoteRepository
from backend.application.ports.voting_cycle_reader import VotingCycleReader
from backend.application.use_cases.get_ballot import get_ballot
from backend.application.use_cases.get_current_issue import select_active_voting_cycle
from backend.domain.errors import InvalidVoteError, VotingCycleClosedError
from backend.domain.vote import BallotSnapshot


def cast_vote(
    votes: VoteRepository,
    voting_cycles: VotingCycleReader,
    user_id: str,
    topic_id: str,
    expected_updated_at: datetime | str | None,
    *,
    now: datetime | None = None,
) -> BallotSnapshot:
    cycle = select_active_voting_cycle(voting_cycles.list_cycles())
    if cycle is None:
        raise InvalidVoteError("no active voting cycle")
    if cycle.status != "open":
        raise VotingCycleClosedError(cycle.id)

    topic_key = (topic_id or "").strip()
    if not topic_key:
        raise InvalidVoteError("topic_id is required")

    topics = votes.list_topics_with_counts(cycle.id)
    topic_ids = {t.id for t in topics}
    if topic_key not in topic_ids:
        raise InvalidVoteError(f"topic {topic_key} is not in cycle {cycle.id}")

    expected: datetime | None
    if expected_updated_at is None or expected_updated_at == "":
        expected = None
    elif isinstance(expected_updated_at, datetime):
        expected = expected_updated_at
    else:
        expected = datetime.fromisoformat(expected_updated_at.replace("Z", "+00:00"))

    votes.upsert_vote(
        cycle_id=cycle.id,
        user_id=user_id,
        topic_id=topic_key,
        expected_updated_at=expected,
    )
    return get_ballot(votes, voting_cycles, user_id, now=now or datetime.now(timezone.utc))
