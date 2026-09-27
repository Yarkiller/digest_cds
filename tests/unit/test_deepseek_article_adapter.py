"""RED→GREEN: DeepSeek article adapter with an injected stub client (LLM-01, LLM-04)."""

from __future__ import annotations

import asyncio
import importlib.resources
import json
from dataclasses import dataclass
from typing import Any

import pytest

from data_collection.dto.article_draft import ArticleDraft
from data_collection.dto.template_kind import TemplateKind
from data_collection.dto.transcript import Transcript


def _stub_client(content: str) -> Any:
    @dataclass
    class _Message:
        content: str

    @dataclass
    class _Choice:
        message: _Message

    @dataclass
    class _Response:
        choices: list[_Choice]

    class _Completions:
        def __init__(self) -> None:
            self.calls: list[dict[str, Any]] = []

        async def create(self, **kwargs: Any) -> Any:
            self.calls.append(kwargs)
            return _Response(choices=[_Choice(message=_Message(content=content))])

    class _Client:
        def __init__(self) -> None:
            self.chat = type("_Chat", (), {"completions": _Completions()})()

    return _Client()


def _make_transcript(language: str = "ru") -> Transcript:
    return Transcript(text="some transcript text", language=language, video_id="vid1")


def test_process_returns_article_draft_for_lecture() -> None:
    from data_collection.adapters.deepseek_article import DeepSeekArticleGenerator
    from data_collection.templates import load_article_templates

    templates = load_article_templates(importlib.resources.files("data_collection.templates"))
    payload = {
        "title": "Title",
        "dek": "Dek",
        "body_markdown": "# Body",
        "extra_key": "ignored",
    }
    client = _stub_client(json.dumps(payload))
    generator = DeepSeekArticleGenerator(
        client=client,
        model="deepseek-flash",
        templates=templates,
        max_transcript_chars=80000,
    )

    draft = asyncio.run(generator.process(_make_transcript("ru"), TemplateKind.LECTURE))

    assert isinstance(draft, ArticleDraft)
    assert draft.title == "Title"
    assert draft.dek == "Dek"
    assert draft.body_markdown == "# Body"
    assert not hasattr(draft, "extra_key")
    assert len(client.chat.completions.calls) == 1


def test_process_returns_article_draft_for_podcast() -> None:
    from data_collection.adapters.deepseek_article import DeepSeekArticleGenerator
    from data_collection.templates import load_article_templates

    templates = load_article_templates(importlib.resources.files("data_collection.templates"))
    payload = {
        "title": "Podcast Title",
        "dek": "Podcast Dek",
        "body_markdown": "## О чём разговор\n\nBody",
    }
    client = _stub_client(json.dumps(payload))
    generator = DeepSeekArticleGenerator(
        client=client,
        model="deepseek-flash",
        templates=templates,
        max_transcript_chars=80000,
    )

    draft = asyncio.run(generator.process(_make_transcript("en"), TemplateKind.PODCAST))

    assert draft.title == "Podcast Title"
    assert draft.dek == "Podcast Dek"
    assert draft.body_markdown == "## О чём разговор\n\nBody"


def test_lecture_prompt_contains_lecture_headings_not_podcast() -> None:
    from data_collection.adapters.deepseek_article import DeepSeekArticleGenerator
    from data_collection.templates import load_article_templates

    templates = load_article_templates(importlib.resources.files("data_collection.templates"))
    client = _stub_client(json.dumps({"title": "T", "dek": "D", "body_markdown": "B"}))
    generator = DeepSeekArticleGenerator(
        client=client,
        model="deepseek-flash",
        templates=templates,
        max_transcript_chars=80000,
    )

    asyncio.run(generator.process(_make_transcript("ru"), TemplateKind.LECTURE))

    call = client.chat.completions.calls[0]
    messages = call["messages"]
    user_content = messages[-1]["content"]
    assert "## Тезис" in user_content
    assert "## Ход рассуждения" in user_content
    assert "## Вывод" in user_content
    assert "## О чём разговор" not in user_content


def test_podcast_prompt_contains_podcast_headings_not_lecture() -> None:
    from data_collection.adapters.deepseek_article import DeepSeekArticleGenerator
    from data_collection.templates import load_article_templates

    templates = load_article_templates(importlib.resources.files("data_collection.templates"))
    client = _stub_client(json.dumps({"title": "T", "dek": "D", "body_markdown": "B"}))
    generator = DeepSeekArticleGenerator(
        client=client,
        model="deepseek-flash",
        templates=templates,
        max_transcript_chars=80000,
    )

    asyncio.run(generator.process(_make_transcript("en"), TemplateKind.PODCAST))

    call = client.chat.completions.calls[0]
    messages = call["messages"]
    user_content = messages[-1]["content"]
    assert "## О чём разговор" in user_content
    assert "## Позиции" in user_content
    assert "## Что запомнить" in user_content
    assert "## Тезис" not in user_content


def test_system_prompt_contains_honesty_and_language_rules() -> None:
    from data_collection.adapters.deepseek_article import DeepSeekArticleGenerator
    from data_collection.templates import load_article_templates

    templates = load_article_templates(importlib.resources.files("data_collection.templates"))
    client = _stub_client(json.dumps({"title": "T", "dek": "D", "body_markdown": "B"}))
    generator = DeepSeekArticleGenerator(
        client=client,
        model="deepseek-flash",
        templates=templates,
        max_transcript_chars=80000,
    )

    asyncio.run(generator.process(_make_transcript("ru"), TemplateKind.LECTURE))

    call = client.chat.completions.calls[0]
    messages = call["messages"]
    system_content = messages[0]["content"]
    assert "Use only the transcript" in system_content
    assert "Do not invent facts, names, or numbers" in system_content
    assert "Output is always Russian" in system_content
    assert "If the transcript language is ru: format only; do not translate" in system_content
    assert "If the transcript language is en: translate into Russian" in system_content
    assert "Preserve technical terms, proper names, library names, numbers, and units as written" in system_content
    assert "json" in system_content
    assert "title" in system_content
    assert "dek" in system_content
    assert "body_markdown" in system_content


def test_create_kwargs_include_json_object_and_disabled_thinking() -> None:
    from data_collection.adapters.deepseek_article import DeepSeekArticleGenerator
    from data_collection.templates import load_article_templates

    templates = load_article_templates(importlib.resources.files("data_collection.templates"))
    client = _stub_client(json.dumps({"title": "T", "dek": "D", "body_markdown": "B"}))
    generator = DeepSeekArticleGenerator(
        client=client,
        model="deepseek-flash",
        templates=templates,
        max_transcript_chars=80000,
    )

    asyncio.run(generator.process(_make_transcript("ru"), TemplateKind.LECTURE))

    call = client.chat.completions.calls[0]
    assert call["response_format"] == {"type": "json_object"}
    assert call["extra_body"] == {"thinking": {"type": "disabled"}}


def test_preserved_technical_terms_round_trip_unchanged() -> None:
    from data_collection.adapters.deepseek_article import DeepSeekArticleGenerator
    from data_collection.templates import load_article_templates

    templates = load_article_templates(importlib.resources.files("data_collection.templates"))
    body = "pgvector, RAG, embedding"
    payload = {"title": "T", "dek": "D", "body_markdown": body}
    client = _stub_client(json.dumps(payload))
    generator = DeepSeekArticleGenerator(
        client=client,
        model="deepseek-flash",
        templates=templates,
        max_transcript_chars=80000,
    )

    for language in ("ru", "en"):
        draft = asyncio.run(generator.process(_make_transcript(language), TemplateKind.LECTURE))
        assert draft.body_markdown == body


def test_body_without_headings_is_valid_when_strings_non_blank() -> None:
    from data_collection.adapters.deepseek_article import DeepSeekArticleGenerator
    from data_collection.templates import load_article_templates

    templates = load_article_templates(importlib.resources.files("data_collection.templates"))
    payload = {"title": "T", "dek": "D", "body_markdown": "plain body"}
    client = _stub_client(json.dumps(payload))
    generator = DeepSeekArticleGenerator(
        client=client,
        model="deepseek-flash",
        templates=templates,
        max_transcript_chars=80000,
    )

    draft = asyncio.run(generator.process(_make_transcript("ru"), TemplateKind.LECTURE))
    assert draft.body_markdown == "plain body"
