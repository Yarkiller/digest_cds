"""Authenticated razbor endpoints — list chronology (RAZB-01 / D-66)."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict

from backend.application.use_cases.list_razbors import list_razbors
from backend.domain.auth_claims import AccessTokenClaims
from backend.domain.errors import PersistenceError
from backend.domain.razbor import Razbor
from backend.interface.http.deps import get_principal

router = APIRouter(prefix="/razbory", tags=["razbory"])


class RazborListItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    title: str
    meeting_at: datetime | None
    status: str


class RazborListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[RazborListItemResponse]


def _require_razbors(request: Request):
    container = request.app.state.container
    if container is None or getattr(container, "razbors", None) is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="razbory_not_configured",
        )
    return container.razbors


def _to_item(razbor: Razbor) -> RazborListItemResponse:
    return RazborListItemResponse(
        id=razbor.id,
        title=razbor.title,
        meeting_at=razbor.meeting_at,
        status=razbor.status.value,
    )


@router.get(
    "",
    response_model=RazborListResponse,
    summary="Razbor chronology list",
    description=(
        "Returns razbors ordered by meeting_at DESC NULLS LAST, then created_at DESC "
        "(RAZB-01 / D-66). Requires Bearer JWT. Empty list → 200 with items=[]."
    ),
)
def read_razbory(
    request: Request,
    claims: AccessTokenClaims = Depends(get_principal),
) -> RazborListResponse:
    del claims
    razbors = _require_razbors(request)
    try:
        rows = list_razbors(razbors)
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="razbory_unavailable",
        ) from exc
    return RazborListResponse(items=[_to_item(row) for row in rows])
