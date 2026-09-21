"""Get razbor by id for reader detail (stub path for 04-06)."""

from __future__ import annotations

from backend.application.ports.razbor_repository import RazborRepository
from backend.domain.errors import RazborNotFoundError
from backend.domain.razbor import Razbor


def get_razbor(razbors: RazborRepository, razbor_id: int) -> Razbor:
    """Return razbor or raise RazborNotFoundError when missing."""
    razbor = razbors.get(razbor_id)
    if razbor is None:
        raise RazborNotFoundError(razbor_id)
    return razbor
