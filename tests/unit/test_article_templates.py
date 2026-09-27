"""RED→GREEN: article templates are package markdown with D-16 headings (LLM-02)."""

from __future__ import annotations

import importlib.resources
from pathlib import Path

from data_collection.dto.template_kind import TemplateKind


def test_lecture_md_contains_russian_headings() -> None:
    root = importlib.resources.files("data_collection.templates")
    text = root.joinpath("lecture.md").read_text(encoding="utf-8")
    assert "## Тезис" in text
    assert "## Ход рассуждения" in text
    assert "## Вывод" in text


def test_podcast_md_contains_russian_headings() -> None:
    root = importlib.resources.files("data_collection.templates")
    text = root.joinpath("podcast.md").read_text(encoding="utf-8")
    assert "## О чём разговор" in text
    assert "## Позиции" in text
    assert "## Что запомнить" in text


def test_load_article_templates_returns_both_kinds() -> None:
    from data_collection.templates import load_article_templates

    root = importlib.resources.files("data_collection.templates")
    templates = load_article_templates(root)
    assert set(templates.keys()) == set(TemplateKind)
    assert "## Тезис" in templates[TemplateKind.LECTURE]
    assert "## О чём разговор" in templates[TemplateKind.PODCAST]
