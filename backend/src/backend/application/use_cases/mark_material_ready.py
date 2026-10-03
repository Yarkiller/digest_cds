"""mark_material_ready — status-only triage promote (ADUX-05; D-06 / D-09 / D-10)."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.application.ports.material_repository import MaterialRepository
from backend.domain.errors import MaterialNotFoundError
from backend.domain.material import Material


def mark_material_ready(
    repo: MaterialRepository,
    material_id: int,
    *,
    now: datetime | None = None,
) -> Material:
    material = repo.get(material_id)
    if material is None:
        raise MaterialNotFoundError(material_id)
    clock = now or datetime.now(timezone.utc)
    updated = material.with_ready_status(now=clock)
    if updated is material:
        return material
    return repo.save(updated)
