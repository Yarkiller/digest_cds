"""DeepSeek ArticleGenerator adapter via the official OpenAI SDK (D-11, D-12)."""

from __future__ import annotations

import json
from typing import Any

from data_collection.dto.article_draft import ArticleDraft
from data_collection.dto.template_kind import TemplateKind
from data_collection.dto.transcript import Transcript


ARTICLE_SYSTEM_PROMPT = (
    "You are an editorial assistant preparing articles for СВА (Служба внутреннего аудита).\n"
    "Use only the transcript below. Do not invent facts, names, or numbers.\n"
    "Output is always Russian.\n"
    "If the transcript language is ru: format only; do not translate.\n"
    "If the transcript language is en: translate into Russian.\n"
    "Preserve technical terms, proper names, library names, numbers, and units as written.\n"
    "Return one json object with keys title, dek, body_markdown."
)


def build_article_messages(
    transcript: Transcript,
    template: TemplateKind,
    templates: dict[TemplateKind, str],
) -> list[dict[str, str]]:
    """System prompt + user message carrying template, language, and transcript."""
    user_parts = [
        templates[template],
        "",
        f"Transcript language: {transcript.language}",
        "",
        transcript.text,
    ]
    return [
        {"role": "system", "content": ARTICLE_SYSTEM_PROMPT},
        {"role": "user", "content": "\n".join(user_parts)},
    ]


class DeepSeekArticleGenerator:
    """ArticleGenerator implementation over an injected async OpenAI client."""

    def __init__(
        self,
        client: Any,
        model: str,
        templates: dict[TemplateKind, str],
        max_transcript_chars: int,
    ) -> None:
        self._client = client
        self._model = model
        self._templates = templates
        self._max_transcript_chars = max_transcript_chars

    async def process(
        self, transcript: Transcript, template: TemplateKind
    ) -> ArticleDraft:
        messages = build_article_messages(transcript, template, self._templates)
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            response_format={"type": "json_object"},
            extra_body={"thinking": {"type": "disabled"}},
        )
        content = response.choices[0].message.content
        payload = json.loads(content)
        if not isinstance(payload, dict):
            raise ValueError("response JSON is not an object")
        return ArticleDraft.model_validate(payload)
