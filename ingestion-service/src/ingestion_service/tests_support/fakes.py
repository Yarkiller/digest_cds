"""In-memory PersistPort double with call spy and scripted failures (D-03, D-11)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from data_collection.dto.material_draft import MaterialDraft
from ingestion_service.adapters.persist_errors import DraftPersistError
from ingestion_service.application.ports.persist import PersistResult


class FakeDraftPersister:
    def __init__(
        self,
        result: PersistResult,
        failures: dict[str, DraftPersistError] | None = None,
    ) -> None:
        self._result = result
        self._failures = failures or {}
        self.calls: list[MaterialDraft] = []
        self.stored: dict[str, PersistResult] = {}

    def persist(self, material_draft: MaterialDraft) -> PersistResult:
        self.calls.append(material_draft)
        failure = self._failures.get(material_draft.youtube_video_id)
        if failure is not None:
            raise failure
        existing = self.stored.get(material_draft.youtube_video_id)
        if existing is not None:
            return existing
        self.stored[material_draft.youtube_video_id] = self._result
        return self._result


@dataclass
class FakeShortlistBatch:
    batch_id: int
    sent_at: datetime | None = None
    items: list[dict[str, object]] = field(default_factory=list)


class BatchTrackingFakePersister:
    """PersistPort double that models unsent-batch overflow and sent-batch skip."""

    def __init__(self, batch_size: int = 5) -> None:
        self.batch_size = batch_size
        self.calls: list[MaterialDraft] = []
        self.stored: dict[str, PersistResult] = {}
        self.batches: dict[int, FakeShortlistBatch] = {}
        self._next_batch_id = 1
        self._next_material_id = 1

    def seed_batch(
        self, batch_id: int, *, sent_at: datetime | None = None
    ) -> FakeShortlistBatch:
        batch = FakeShortlistBatch(batch_id=batch_id, sent_at=sent_at)
        self.batches[batch_id] = batch
        self._next_batch_id = max(self._next_batch_id, batch_id + 1)
        return batch

    def seed_item(
        self,
        batch_id: int,
        *,
        decision: str = "pending",
        video_id: str | None = None,
    ) -> None:
        batch = self.batches[batch_id]
        batch.items.append(
            {
                "video_id": video_id,
                "rank": len(batch.items) + 1,
                "decision": decision,
            }
        )

    def persist(self, material_draft: MaterialDraft) -> PersistResult:
        self.calls.append(material_draft)
        existing = self.stored.get(material_draft.youtube_video_id)
        if existing is not None:
            return existing
        batch = self._target_unsent_batch()
        rank = len(batch.items) + 1
        result = PersistResult(
            material_id=self._next_material_id,
            slug=material_draft.slug,
            batch_id=batch.batch_id,
            rank=rank,
        )
        self._next_material_id += 1
        batch.items.append(
            {
                "video_id": material_draft.youtube_video_id,
                "rank": rank,
                "decision": "pending",
                "material_id": result.material_id,
            }
        )
        self.stored[material_draft.youtube_video_id] = result
        return result

    def _target_unsent_batch(self) -> FakeShortlistBatch:
        unsent = [batch for batch in self.batches.values() if batch.sent_at is None]
        if not unsent:
            return self._create_batch()
        latest = max(unsent, key=lambda batch: batch.batch_id)
        if len(latest.items) >= self.batch_size:
            return self._create_batch()
        return latest

    def _create_batch(self) -> FakeShortlistBatch:
        batch_id = self._next_batch_id
        self._next_batch_id += 1
        batch = FakeShortlistBatch(batch_id=batch_id)
        self.batches[batch_id] = batch
        return batch
