"""Admin shortlist endpoints — GET/decision/preview/send behind require_admin (ADMIN-01…08)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field

from backend.application.use_cases.get_admin_shortlist import get_admin_shortlist
from backend.application.use_cases.preview_digest_email import (
    PreviewMaterialBlock,
    PreviewTextBlock,
    preview_digest_email,
)
from backend.application.use_cases.send_digest import send_digest
from backend.application.use_cases.set_shortlist_decision import set_shortlist_decision
from backend.domain.current_user import CurrentUser
from backend.domain.errors import (
    AlreadySentError,
    DraftInSendPoolError,
    EmptySendPoolError,
    InvalidPreviewCompositionError,
    InvalidSendOrderError,
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
    digest_rest: bool = False
    days_until_next_batch: int | None = None


class SetShortlistDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: str = Field(
        ...,
        min_length=1,
        description="shortlist_decision: pending|approved|rejected (D-82; allowlist in use-case)",
    )


class DigestPreviewItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    material_id: int
    rank: int
    title: str


class DigestPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batch_id: int
    subject: str
    body: str
    items: list[DigestPreviewItemResponse] = []


class DigestPreviewMaterialBlockRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str = Field(..., pattern="^material$")
    material_id: int


class DigestPreviewTextBlockRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str = Field(..., pattern="^text$")
    text: str


class DigestPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intro: str = ""
    blocks: list[DigestPreviewMaterialBlockRequest | DigestPreviewTextBlockRequest] | None = None


class SendDigestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    material_ids: list[int] | None = None


class SendDigestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batch_id: int
    issue_number: int
    issue_url: str
    delivery_status: str
    recipient_count: int = 0
    message: str


def _require_shortlist(request: Request):
    container = request.app.state.container
    if container is None or getattr(container, "shortlist", None) is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="shortlist_not_configured",
        )
    return container.shortlist


def _require_container(request: Request):
    container = request.app.state.container
    if container is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="container_not_configured",
        )
    return container


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
        digest_rest=dto.digest_rest,
        days_until_next_batch=dto.days_until_next_batch,
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


@router.post(
    "/shortlist/preview",
    response_model=DigestPreviewResponse,
    summary="Preview digest email for approved∩ready pool",
    description=(
        "Returns subject/body/items for approved ready materials only (ADMIN-04, D-86, G-05-1). "
        "Optional intro + ordered blocks compose the body. Never marks batch sent. "
        "Empty pool → 400; invalid composition → 400. Requires admin."
    ),
)
def post_shortlist_preview(
    request: Request,
    body: DigestPreviewRequest | None = None,
    _admin: CurrentUser = Depends(require_admin),
) -> DigestPreviewResponse:
    shortlist = _require_shortlist(request)
    payload = body or DigestPreviewRequest()
    uc_blocks: list[PreviewMaterialBlock | PreviewTextBlock] | None = None
    if payload.blocks is not None:
        uc_blocks = []
        for block in payload.blocks:
            if isinstance(block, DigestPreviewMaterialBlockRequest):
                uc_blocks.append(PreviewMaterialBlock(material_id=block.material_id))
            else:
                uc_blocks.append(PreviewTextBlock(text=block.text))
    try:
        preview = preview_digest_email(
            shortlist,
            intro=payload.intro,
            blocks=uc_blocks,
        )
    except EmptySendPoolError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="empty_send_pool",
        ) from exc
    except InvalidPreviewCompositionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_preview_composition",
        ) from exc
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="shortlist_unavailable",
        ) from exc
    return DigestPreviewResponse(
        batch_id=preview.batch_id,
        subject=preview.subject,
        body=preview.body,
        items=[
            DigestPreviewItemResponse(
                material_id=item.material_id,
                rank=item.rank,
                title=item.title,
            )
            for item in preview.items
        ],
    )


@router.post(
    "/shortlist/send",
    response_model=SendDigestResponse,
    summary="Send digest: claim, publish issue, stub mail",
    description=(
        "Publish-on-send (D-88): claim batch, publish digest_issues, StubMailer. "
        "Draft in pool → 400; empty → 400; already sent → 409. Success: «Отправка записана»."
    ),
)
def post_shortlist_send(
    request: Request,
    body: SendDigestRequest | None = None,
    admin: CurrentUser = Depends(require_admin),
) -> SendDigestResponse:
    container = _require_container(request)
    shortlist = _require_shortlist(request)
    payload = body or SendDigestRequest()
    try:
        result = send_digest(
            shortlist,
            container.publisher,
            container.mailer,
            container.pings,
            actor_user_id=admin.id,
            material_ids=payload.material_ids,
        )
    except DraftInSendPoolError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "draft_in_send_pool",
                "draft_material_ids": exc.draft_material_ids,
            },
        ) from exc
    except InvalidSendOrderError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_send_order",
        ) from exc
    except EmptySendPoolError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="empty_send_pool",
        ) from exc
    except AlreadySentError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="already_sent",
        ) from exc
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="shortlist_unavailable",
        ) from exc
    return SendDigestResponse(
        batch_id=result.batch_id,
        issue_number=result.issue_number,
        issue_url=result.issue_url,
        delivery_status=result.delivery_status,
        recipient_count=result.recipient_count,
        message=result.message,
    )
