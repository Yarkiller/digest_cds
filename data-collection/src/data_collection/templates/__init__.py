"""Repository markdown templates for lecture and podcast prompts (D-16)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable

from data_collection.dto.template_kind import TemplateKind


def load_article_templates(root: Traversable) -> dict[TemplateKind, str]:
    """Load template markdown for every TemplateKind from *root*.

    Production root is ``importlib.resources.files("data_collection.templates")``.
    """
    loaded: dict[TemplateKind, str] = {}
    for kind in TemplateKind:
        path = root.joinpath(f"{kind.value}.md")
        loaded[kind] = path.read_text(encoding="utf-8")
    return loaded
