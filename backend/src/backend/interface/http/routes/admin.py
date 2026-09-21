"""Admin shortlist endpoints — GET + decision mutation behind require_admin (ADMIN-01…03/05)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field

from backend.application.use_cases.get_admin_shortlist import get_admin_shortlist
from backend.application.use_cases.set_shortlist_decision import set_shortlist_decision
from backend.domain.current_user import CurrentUser
from backend.domain.errors import (
    InvalidShortlistDecisionError,
    PersistenceError,
    ShortlistNotFoundError,
)
from backend.domain.shortlist import AdminShortlist
from backend.interface.http.deps import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminShortlistItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    material_id: int
    rank: int
    title: str
    material_status: str
    decision: str
    score: float | None = None
    factor_labels: list[str] = []


class AdminShortlistResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batch_id: int | None = None
    items: list[AdminShortlistItemResponse] = []


class SetShortlistDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: str = Field(
        ...,
        min_length=1,
        description="shortlist_decision: pending|approved|rejected (D-82; allowlist in use-case)",
    )


def _require_shortlist(request: Request):
    container = request.app.state.container
    if container is None or getattr(container, "shortlist", None) is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="shortlist_not_configured",
        )
    return container.shortlist


def _to_response(dto: AdminShortlist) -> AdminShortlistResponse:
    return AdminShortlistResponse(
        batch_id=dto.batch_id,
        items=[
            AdminShortlistItemResponse(
                material_id=item.material_id,
                rank=item.rank,
                title=item.title,
                material_status=item.material_status,
                decision=item.decision,
                score=item.score,
                factor_labels=list(item.factor_labels),
            )
            for item in dto.items
        ],
    )


@router.get(
    "/shortlist",
    response_model=AdminShortlistResponse,
    summary="Current admin shortlist batch",
    description=(
        "Returns ≤5 ranked shortlist candidates for the current unsent batch "
        "(ADMIN-01, D-81). Requires profiles.role=admin (D-74). "
        "Empty batch → items=[] (D-80). PersistenceError → 503 shortlist_unavailable."
    ),
)
def read_admin_shortlist(
    request: Request,
    _admin: CurrentUser = Depends(require_admin),
) -> AdminShortlistResponse:
    shortlist = _require_shortlist(request)
    try:
        dto = get_admin_shortlist(shortlist)
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="shortlist_unavailable",
        ) from exc
    return _to_response(dto)


@router.post(
    "/shortlist/items/{material_id}/decision",
    response_model=AdminShortlistResponse,
    summary="Set shortlist decision for one material",
    description=(
        "Persists shortlist_decision pending|approved|rejected (ADMIN-02, D-82). "
        "Approve allowed on draft (D-85). Actor is authenticated admin id (T-05-07). "
        "Unknown material → 404; invalid body → 400; PersistenceError → 503."
    ),
)
def post_shortlist_decision(
    material_id: int,
    body: SetShortlistDecisionRequest,
    request: Request,
    admin: CurrentUser = Depends(require_admin),
) -> AdminShortlistResponse:
    shortlist = _require_shortlist(request)
    try:
        dto = set_shortlist_decision(
            shortlist,
            material_id=material_id,
            decision=body.decision,
            actor_user_id=admin.id,
        )
    except InvalidShortlistDecisionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_decision",
        ) from exc
    except ShortlistNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="shortlist_item_not_found",
        ) from exc
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="shortlist_unavailable",
        ) from exc
    return _to_response(dto)
