"""FastAPI dependency injectors for Autofolio API."""
from __future__ import annotations

import hmac
from typing import Annotated, Any

from fastapi import Cookie, Depends, Header, HTTPException, status

from app.api.security import COOKIE_NAME, decode_session

_CSRF_HEADER = "X-CSRF-Token"
_APP_USER_ROLES = {"owner", "member"}


def get_session(
    af_session: Annotated[str | None, Cookie(alias=COOKIE_NAME)] = None,
) -> dict[str, Any] | None:
    """Return the decoded session dict, or None if the cookie is absent / invalid."""
    if af_session is None:
        return None
    return decode_session(af_session)


def require_session(
    session: Annotated[dict[str, Any] | None, Depends(get_session)],
) -> dict[str, Any]:
    """Raise 401 if there is no valid session (including guest sessions)."""
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return session


def require_app_user(
    session: Annotated[dict[str, Any], Depends(require_session)],
) -> dict[str, Any]:
    """Raise 403 if the caller is not an approved app user (guest -> 403)."""
    if session.get("role") not in _APP_USER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Approved account required",
        )
    return session


def require_owner(
    session: Annotated[dict[str, Any], Depends(require_session)],
) -> dict[str, Any]:
    """Raise 403 unless the caller is the service Owner/admin."""
    if session.get("role") != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner role required",
        )
    return session


require_admin = require_owner


def _validate_csrf(session: dict[str, Any], x_csrf_token: str | None) -> dict[str, Any]:
    expected = session.get("csrf_token")
    if not expected or not hmac.compare_digest(x_csrf_token or "", expected):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing or invalid",
        )
    return session


def require_app_user_csrf(
    session: Annotated[dict[str, Any], Depends(require_app_user)],
    x_csrf_token: Annotated[str | None, Header(alias=_CSRF_HEADER)] = None,
) -> dict[str, Any]:
    """Validate CSRF for approved-user self-service mutations."""
    return _validate_csrf(session, x_csrf_token)


def require_owner_csrf(
    session: Annotated[dict[str, Any], Depends(require_owner)],
    x_csrf_token: Annotated[str | None, Header(alias=_CSRF_HEADER)] = None,
) -> dict[str, Any]:
    """Validate CSRF for Owner/admin-only mutations."""
    return _validate_csrf(session, x_csrf_token)


require_admin_csrf = require_owner_csrf
require_csrf = require_app_user_csrf
