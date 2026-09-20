"""Authenticated current-issue endpoint — GET /issues/current (ISSUE-01 / D-24 / D-26)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict

from backend.application.use_cases.get_current_issue import get_current_issue
from backend.domain.auth_claims import AccessTokenClaims
from backend.domain.errors import PersistenceError
from backend.domain.issue import Issue
from backend.interface.http.deps import get_principal

router = APIRouter(prefix="/issues", tags=["issues"])


class IssueItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    title: str
    position: int
    format: str
    reading_minutes: int
    dek: str | None = None


class CurrentIssueResponse(BaseModel):
    """Honest empty: number/title null and items=[] when no published issue (D-24/D-30)."""

    model_config = ConfigDict(extra="forbid")

    number: int | None = None
    period_label: str | None = None
    title: str | None = None
    editor: str | None = None
    items: list[IssueItemResponse] = []


def _to_response(issue: Issue | None) -> CurrentIssueResponse:
    if issue is None:
        return CurrentIssueResponse()
    return CurrentIssueResponse(
        number=issue.number,
        period_label=issue.period_label,
        title=issue.title,
        editor=issue.editor,
        items=[
            IssueItemResponse(
                slug=item.slug,
                title=item.title,
                position=item.position,
                format=item.format,
                reading_minutes=item.reading_minutes,
                dek=item.dek,
            )
            for item in issue.items
        ],
    )


@router.get(
    "/current",
    response_model=CurrentIssueResponse,
    summary="Current published issue",
    description=(
        "Returns the latest published digest issue by published_at (D-24). "
        "Requires Bearer JWT. Empty published set → 200 with null fields and empty items."
    ),
)
def read_current_issue(
    request: Request,
    claims: AccessTokenClaims = Depends(get_principal),
) -> CurrentIssueResponse:
    del claims  # auth gate only; content is reader-shared
    container = request.app.state.container
    if container is None or getattr(container, "issues", None) is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="issues_not_configured",
        )
    try:
        issue = get_current_issue(container.issues)
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="issues_unavailable",
        ) from exc
    return _to_response(issue)
