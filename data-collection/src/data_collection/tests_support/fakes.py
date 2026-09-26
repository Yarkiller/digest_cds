"""Scripted success + call-spy fakes for ingestion ports (D-15, D-16, D-17)."""

from __future__ import annotations

from data_collection.dto.article_draft import ArticleDraft
from data_collection.dto.template_kind import TemplateKind
from data_collection.dto.transcript import Transcript


class FakeTranscriptProvider:
    def __init__(self, result: Transcript) -> None:
        self._result = result
        self.calls: list[str] = []

    async def get(self, video_id: str) -> Transcript:
        self.calls.append(video_id)
        return self._result


class FakeArticleGenerator:
    def __init__(self, result: ArticleDraft) -> None:
        self._result = result
        self.calls: list[dict] = []

    async def process(
        self, transcript: Transcript, template: TemplateKind
    ) -> ArticleDraft:
        self.calls.append({"transcript": transcript, "template": template})
        return self._result
