"""Admin shortlist endpoints — GET/decision/preview/send behind require_admin (ADMIN-01…08)."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field

from backend.application.use_cases.get_admin_shortlist import get_admin_shortlist
from backend.application.use_cases.mark_material_ready import (
    mark_material_ready,
    mark_materials_ready,
)
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
    MaterialNotFoundError,
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
    dek: str | None = None
    body_markdown: str | None = None
    provenance_label: str | None = None
    slug: str | None = None
    reading_minutes: int | None = None
    char_count: int = 0
    word_count: int = 0


class AdminShortlistResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batch_id: int | None = None
    items: list[AdminShortlistItemResponse] = []
    digest_rest: bool = False
    days_until_next_batch: int | None = None
    week_label: str | None = None
    sent_at: datetime | None = None


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
    html: str
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
    intro: str = ""
    blocks: list[DigestPreviewMaterialBlockRequest | DigestPreviewTextBlockRequest] | None = None


class SendDigestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batch_id: int
    issue_number: int
    issue_url: str
    delivery_status: str
    recipient_count: int = 0
    message: str


class MarkReadyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    material_id: int
    status: str


class MarkReadyBatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    material_ids: list[int]


class MarkReadyBatchItemResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    material_id: int
    ok: bool
    status: str | None = None
    error: str | None = None


class MarkReadyBatchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    results: list[MarkReadyBatchItemResult]


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


def _require_materials(request: Request):
    container = request.app.state.container
    if container is None or getattr(container, "materials", None) is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="materials_not_configured",
        )
    return container.materials


def _to_preview_blocks(
    blocks: list[DigestPreviewMaterialBlockRequest | DigestPreviewTextBlockRequest] | None,
) -> list[PreviewMaterialBlock | PreviewTextBlock] | None:
    if blocks is None:
        return None
    uc_blocks: list[PreviewMaterialBlock | PreviewTextBlock] = []
    for block in blocks:
        if isinstance(block, DigestPreviewMaterialBlockRequest):
            uc_blocks.append(PreviewMaterialBlock(material_id=block.material_id))
        else:
            uc_blocks.append(PreviewTextBlock(text=block.text))
    return uc_blocks


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
                dek=item.dek,
                body_markdown=item.body_markdown,
                provenance_label=item.provenance_label,
                slug=item.slug,
                reading_minutes=item.reading_minutes,
                char_count=item.char_count,
                word_count=item.word_count,
            )
            for item in dto.items
        ],
        digest_rest=dto.digest_rest,
        days_until_next_batch=dto.days_until_next_batch,
        week_label=dto.week_label,
        sent_at=dto.sent_at,
    )


@router.post(
    "/materials/ready",
    response_model=MarkReadyBatchResponse,
    summary="Batch promote materials draft→ready (partial success)",
    description=(
        "One-call batch ready with per-id results (ADUX-05; D-08). "
        "HTTP 200 even when some ids are missing — never 207; never abort the batch. "
        "Requires admin. Unknown JSON fields → 422 (extra=forbid)."
    ),
)
def post_materials_ready_batch(
    body: MarkReadyBatchRequest,
    request: Request,
    _admin: CurrentUser = Depends(require_admin),
) -> MarkReadyBatchResponse:
    materials = _require_materials(request)
    try:
        items = mark_materials_ready(materials, body.material_ids)
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="materials_unavailable",
        ) from exc
    return MarkReadyBatchResponse(
        results=[
            MarkReadyBatchItemResult(
                material_id=item.material_id,
                ok=item.ok,
                status=item.status,
                error=item.error,
            )
            for item in items
        ]
    )


@router.post(
    "/materials/{material_id}/ready",
    response_model=MarkReadyResponse,
    summary="Promote one material draft→ready (status-only)",
    description=(
        "Triage ready without publish gate or published_at (ADUX-05; D-06, D-07, D-09, D-10). "
        "Missing material → 404 material_not_found. Already-ready → 200 no-op. Requires admin."
    ),
)
def post_material_ready(
    material_id: int,
    request: Request,
    _admin: CurrentUser = Depends(require_admin),
) -> MarkReadyResponse:
    materials = _require_materials(request)
    try:
        material = mark_material_ready(materials, material_id)
    except MaterialNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="material_not_found",
        ) from exc
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="materials_unavailable",
        ) from exc
    return MarkReadyResponse(material_id=material.id, status=material.status.value)


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
    uc_blocks = _to_preview_blocks(payload.blocks)
    settings = getattr(request.app.state, "settings", None)
    site_url = getattr(settings, "site_url", None) or "http://127.0.0.1:5173"
    try:
        preview = preview_digest_email(
            shortlist,
            intro=payload.intro,
            blocks=uc_blocks,
            site_url=site_url,
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
        html=preview.html,
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
    settings = getattr(request.app.state, "settings", None)
    site_url = getattr(settings, "site_url", None) or "http://127.0.0.1:5173"
    try:
        result = send_digest(
            shortlist,
            container.publisher,
            container.mailer,
            container.pings,
            actor_user_id=admin.id,
            material_ids=payload.material_ids,
            intro=payload.intro,
            blocks=_to_preview_blocks(payload.blocks),
            site_url=site_url,
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
