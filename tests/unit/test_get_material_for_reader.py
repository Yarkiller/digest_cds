"""Wave 0 scaffold — get_material_for_reader draft→not found; ready by slug.

Becomes active RED→GREEN when 02-04 lands get_material_for_reader.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

get_material_mod = pytest.importorskip(
    "backend.application.use_cases.get_material_for_reader",
    reason="02-04 will add get_material_for_reader",
)
get_material_for_reader = get_material_mod.get_material_for_reader
MaterialNotFoundError = pytest.importorskip(
    "backend.domain.errors",
    reason="domain errors required",
).MaterialNotFoundError
Material = pytest.importorskip("backend.domain.material", reason="Material required").Material
MaterialStatus = pytest.importorskip(
    "backend.domain.material",
    reason="MaterialStatus required",
).MaterialStatus
InMemoryMaterialRepository = pytest.importorskip(
    "backend.tests_support.in_memory",
    reason="InMemoryMaterialRepository required",
).InMemoryMaterialRepository


def _material(*, slug: str, status: MaterialStatus) -> Material:
    now = datetime(2026, 3, 20, tzinfo=timezone.utc)
    return Material(
        id=1,
        slug=slug,
        title="Ready article",
        dek="",
        body_markdown="## Intro\n\nBody.",
        format="статья",
        status=status,
        reading_minutes=5,
        provenance_label="внутренний разбор",
        source_id=None,
        roles=("ds",),
        tags=(("RAG", "rag"),),
        related_material_ids=(),
        published_at=now if status == MaterialStatus.READY else None,
        created_at=now,
        updated_at=now,
    )


def test_get_material_for_reader_returns_ready_by_slug() -> None:
    ready = _material(slug="rag-systems", status=MaterialStatus.READY)
    repo = InMemoryMaterialRepository([ready])
    # 02-04 may extend InMemory with get_by_slug; until then this asserts use-case contract.
    material = get_material_for_reader(repo, "rag-systems")
    assert material.slug == "rag-systems"
    assert material.status == MaterialStatus.READY


def test_get_material_for_reader_draft_raises_not_found() -> None:
    draft = _material(slug="secret-draft", status=MaterialStatus.DRAFT)
    repo = InMemoryMaterialRepository([draft])
    with pytest.raises(MaterialNotFoundError):
        get_material_for_reader(repo, "secret-draft")
