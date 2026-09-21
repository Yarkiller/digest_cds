"""Admin shortlist endpoints — GET /admin/shortlist behind require_admin (ADMIN-01/05, D-74)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict

from backend.application.use_cases.get_admin_shortlist import get_admin_shortlist
from backend.domain.current_user import CurrentUser
from backend.domain.errors import PersistenceError
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


def _require_shortlist(request: Request):
    container = request.app.state.container
    if container is None or getattr(container, "shortlist", None) is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="shortlist_not_configured",
        )
    return container.shortlist


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
