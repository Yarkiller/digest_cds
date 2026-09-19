"""Authenticated identity endpoints.

Admin-route 403 (AUTH-03 full admin API gate) is deferred to Phase 5.
This module exposes GET /me and POST /me/ping for Phase 1 JWT + ping proof.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict

from backend.application.use_cases.get_current_user import get_current_user
from backend.application.use_cases.record_platform_ping import record_platform_ping
from backend.domain.auth_claims import AccessTokenClaims
from backend.interface.http.deps import get_principal

router = APIRouter(tags=["me"])


class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    email: str
    role: str


class PingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    id: str


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    summary="Current authenticated user",
    description=(
        "Returns the CurrentUser DTO for a valid ES256 Bearer token with an allowed "
        "corporate email. Admin-route 403 enforcement is Phase 5 (AUTH-03 partial)."
    ),
)
def read_me(
    request: Request,
    claims: AccessTokenClaims = Depends(get_principal),
) -> CurrentUserResponse:
    container = request.app.state.container
    if container is None or getattr(container, "profiles", None) is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="profiles_not_configured",
        )
    user = get_current_user(container.profiles, claims)
    return CurrentUserResponse(id=user.id, email=user.email, role=user.role)


@router.post(
    "/me/ping",
    response_model=PingResponse,
    summary="Record platform ping",
    description=(
        "Records a platform_ping via PingRecorder for the authenticated principal. "
        "Live activity_events persistence is Plan 04; in-memory proves D-10 offline."
    ),
)
def post_me_ping(
    request: Request,
    claims: AccessTokenClaims = Depends(get_principal),
) -> PingResponse:
    container = request.app.state.container
    if container is None or getattr(container, "pings", None) is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="pings_not_configured",
        )
    recorded_id = record_platform_ping(container.pings, claims.sub)
    return PingResponse(ok=True, id=recorded_id)
