"""ADUX-05: mark_material_ready — RED stub (status flip not implemented yet)."""

from __future__ import annotations

from datetime import datetime

from backend.application.ports.material_repository import MaterialRepository
from backend.domain.errors import MaterialNotFoundError
from backend.domain.material import Material


def mark_material_ready(
    repo: MaterialRepository,
    material_id: int,
    *,
    now: datetime | None = None,
) -> Material:
    del now
    material = repo.get(material_id)
    if material is None:
        raise MaterialNotFoundError(material_id)
    # Intentionally no status flip — RED until GREEN implements with_ready_status.
    return material
