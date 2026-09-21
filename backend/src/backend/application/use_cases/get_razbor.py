"""Get razbor by id for reader detail (RAZB-02 / D-68)."""

from __future__ import annotations

from backend.application.ports.razbor_repository import RazborRepository
from backend.domain.errors import RazborNotFoundError
from backend.domain.razbor import Razbor, RazborStatus


def get_razbor(razbors: RazborRepository, razbor_id: int) -> Razbor:
    """Return razbor or raise RazborNotFoundError when missing.

    Announcement stubs never expose draft prose (D-68 / T-04-10).
    """
    razbor = razbors.get(razbor_id)
    if razbor is None:
        raise RazborNotFoundError(razbor_id)
    if razbor.status == RazborStatus.ANNOUNCEMENT:
        return Razbor(
            id=razbor.id,
            title=razbor.title,
            body_markdown="",
            meeting_at=razbor.meeting_at,
            status=razbor.status,
            notebook_path=razbor.notebook_path,
            created_at=razbor.created_at,
        )
    return razbor
