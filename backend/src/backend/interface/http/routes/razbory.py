"""Authenticated razbor endpoints — list chronology + detail (RAZB-01 / RAZB-02 / D-66 / D-68)."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from pydantic import BaseModel, ConfigDict

from backend.application.use_cases.get_razbor import RazborDetail, get_razbor
from backend.application.use_cases.list_razbors import list_razbors
from backend.domain.auth_claims import AccessTokenClaims
from backend.domain.errors import PersistenceError, RazborNotFoundError
from backend.domain.razbor import Razbor
from backend.interface.http.deps import get_principal

router = APIRouter(prefix="/razbory", tags=["razbory"])

EDITOR_BYLINE = "Редакция Digest CDS"


class RazborListItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    title: str
    meeting_at: datetime | None
    status: str


class RazborListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[RazborListItemResponse]


class RazborDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    title: str
    meeting_at: datetime | None
    status: str
    body_markdown: str
    notebook_available: bool
    content_kind: str
    editor: str = EDITOR_BYLINE


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


def _to_detail(detail: RazborDetail) -> RazborDetailResponse:
    return RazborDetailResponse(
        id=detail.id,
        title=detail.title,
        meeting_at=detail.meeting_at,
        status=detail.status.value,
        body_markdown=detail.body_markdown,
        notebook_available=bool(detail.notebook_path),
        content_kind=detail.content_kind,
        editor=EDITOR_BYLINE,
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


@router.get(
    "/{razbor_id}",
    response_model=RazborDetailResponse,
    summary="Razbor detail",
    description=(
        "Returns published longread or announcement stub (D-68). "
        "Requires Bearer JWT. Missing → 404 razbor_not_found."
    ),
)
def read_razbor(
    request: Request,
    razbor_id: int = Path(..., ge=1),
    claims: AccessTokenClaims = Depends(get_principal),
) -> RazborDetailResponse:
    del claims
    razbors = _require_razbors(request)
    try:
        razbor = get_razbor(razbors, razbor_id)
    except RazborNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="razbor_not_found",
        ) from exc
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="razbory_unavailable",
        ) from exc
    return _to_detail(razbor)
