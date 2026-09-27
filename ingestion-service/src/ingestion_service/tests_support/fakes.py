"""In-memory PersistPort double with call spy and scripted failures (D-03, D-11)."""

from __future__ import annotations

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
