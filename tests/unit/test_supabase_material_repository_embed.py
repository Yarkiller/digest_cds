"""Offline regression for the ambiguous `material_relations` embed (G-14-1 / G-14-4).

`materials` <-> `material_relations` has two foreign keys (`from_material_id` /
`to_material_id`), so a bare `material_relations(to_material_id)` embed is
ambiguous and PostgREST rejects it with PGRST201. Every live
`SupabaseMaterialRepository.get()` / `get_by_slug()` then raised `PersistenceError`,
which surfaced as HTTP 503 on the admin promote route.

These tests use a fake client that *simulates* the PGRST201 rejection, so the
real embed shape is exercised without a network/DB round-trip.
"""

from __future__ import annotations

import re
from typing import Any

from backend.domain.material import Material, MaterialStatus


class _PGRST201Error(Exception):
    """Mimics `postgrest.exceptions.APIError` for an ambiguous embed."""

    code = "PGRST201"


class _FakeResult:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.data = data


class _FakeQuery:
    def __init__(self, table: "_FakeTable") -> None:
        self._table = table
        self._select_cols = "*"
        self._filters: list[tuple[str, Any]] = []
        self._limit: int | None = None

    def select(self, cols: str = "*") -> "_FakeQuery":
        self._select_cols = cols
        return self

    def eq(self, column: str, value: Any) -> "_FakeQuery":
        self._filters.append((column, value))
        return self

    def limit(self, n: int) -> "_FakeQuery":
        self._limit = n
        return self

    def execute(self) -> _FakeResult:
        self._table.select_specs.append(self._select_cols)
        # PostgREST rejects the ambiguous embed before returning any rows.
        if self._table.name == "materials" and "material_relations(" in self._select_cols:
            raise _PGRST201Error(
                "Could not embed because more than one relationship was found "
                "for 'materials' and 'material_relations'"
            )
        matched = list(self._table.rows)
        for column, value in self._filters:
            matched = [r for r in matched if r.get(column) == value]
        if self._limit is not None:
            matched = matched[: self._limit]
        return _FakeResult(matched)


class _FakeTable:
    def __init__(self, name: str) -> None:
        self.name = name
        self.rows: list[dict[str, Any]] = []
        self.select_specs: list[str] = []

    def query(self) -> _FakeQuery:
        return _FakeQuery(self)


class _FakeClient:
    def __init__(self) -> None:
        self.tables = {"materials": _FakeTable("materials")}

    def table(self, name: str) -> _FakeQuery:
        return self.tables[name].query()


def _seed_ready_material(client: _FakeClient) -> None:
    client.tables["materials"].rows.append(
        {
            "id": 1,
            "slug": "rag-systems",
            "title": "Building Production RAG Systems",
            "dek": "",
            "body_markdown": "## Body\n\nText.",
            "format": "статья",
            "status": "ready",
            "reading_minutes": 5,
            "provenance_label": "внешний текстовый источник",
            "source_id": None,
            "roles": [],
            "published_at": "2026-03-20T12:00:00+00:00",
            "created_at": "2026-03-20T12:00:00+00:00",
            "updated_at": "2026-03-20T12:00:00+00:00",
            # Empty embeds: `_filter_ready_relations` short-circuits (no extra queries).
            "material_tags": [],
            "material_relations": [],
        }
    )


def test_get_returns_material_under_ambiguous_embed_rejection() -> None:
    from supabase_integration import SupabaseMaterialRepository

    client = _FakeClient()
    _seed_ready_material(client)
    repo = SupabaseMaterialRepository(client)

    material = repo.get(1)

    assert isinstance(material, Material)
    assert material.slug == "rag-systems"
    assert material.status == MaterialStatus.READY


def test_get_by_slug_returns_material_under_ambiguous_embed_rejection() -> None:
    from supabase_integration import SupabaseMaterialRepository

    client = _FakeClient()
    _seed_ready_material(client)
    repo = SupabaseMaterialRepository(client)

    material = repo.get_by_slug("rag-systems")

    assert isinstance(material, Material)
    assert material.slug == "rag-systems"


def test_fetch_one_disambiguates_relations_embed_and_keeps_tags_unhinted() -> None:
    from supabase_integration import SupabaseMaterialRepository

    client = _FakeClient()
    _seed_ready_material(client)
    repo = SupabaseMaterialRepository(client)

    repo.get(1)

    specs = client.tables["materials"].select_specs
    assert specs, "materials.select(...) was never called"
    spec = specs[-1]
    # Disambiguated by an FK hint, e.g. material_relations!<fk>(to_material_id).
    assert "material_relations!" in spec
    assert re.search(r"material_relations![^(]+\(to_material_id\)", spec)
    assert "material_relations(to_material_id)" not in spec
    # Single FK -> intentionally left unhinted.
    assert "material_tags(tag_slug,tag_label)" in spec
