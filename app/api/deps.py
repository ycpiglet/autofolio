"""FastAPI dependency injectors for Autofolio API."""
from __future__ import annotations

import hmac
from typing import Annotated, Any

from fastapi import Cookie, Depends, Header, HTTPException, status

from app.api.security import COOKIE_NAME, decode_session

_CSRF_HEADER = "X-CSRF-Token"


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


def require_owner(
    session: Annotated[dict[str, Any], Depends(require_session)],
) -> dict[str, Any]:
    """Raise 403 if the caller is not an owner (guest → 403).

    This is the safety seam for Phase 3 state-changing endpoints.
    """
    if session.get("role") != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner role required",
        )
    return session


def require_csrf(
    session: Annotated[dict[str, Any], Depends(require_owner)],
    x_csrf_token: Annotated[str | None, Header(alias=_CSRF_HEADER)] = None,
) -> dict[str, Any]:
    """Validate X-CSRF-Token header against the session's csrf_token.

    Raises 403 if header is missing, empty, or does not match.
    Must be composed after require_owner so guests are already rejected
    before we bother checking CSRF.
    """
    expected = session.get("csrf_token")
    if not expected or not hmac.compare_digest(x_csrf_token or "", expected):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing or invalid",
        )
    return session


# Convenience alias — apply both owner gate and CSRF gate together
require_owner_csrf = require_csrf
