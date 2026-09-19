"""HTTP dependencies: Bearer JWT verify + corporate email gate."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWK

from backend.domain.auth_claims import AccessTokenClaims
from backend.domain.auth_email import DEFAULT_ALLOWED_EMAIL_DOMAINS, is_allowed_corporate_email
from backend.infrastructure.auth_jwt import TokenVerificationError, verify_access_token

_bearer = HTTPBearer(auto_error=True)


def get_principal(
    request: Request,
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
) -> AccessTokenClaims:
    settings = request.app.state.settings
    resolver: Callable[[str], Mapping[str, Any] | PyJWK] | None = getattr(
        request.app.state,
        "signing_key_resolver",
        None,
    )
    try:
        claims = verify_access_token(
            creds.credentials,
            issuer=settings.supabase_jwt_issuer,
            jwks_url=settings.supabase_jwks_url or None,
            signing_key_resolver=resolver,
        )
    except TokenVerificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from exc

    domains = settings.email_domains or DEFAULT_ALLOWED_EMAIL_DOMAINS
    if not is_allowed_corporate_email(claims.email, allowed_domains=domains):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="domain_not_allowed",
        )
    return claims
