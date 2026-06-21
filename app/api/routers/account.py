"""Account router — /api/account/*

Local account management (no external OAuth/SSO). Endpoints:
  GET  /account           — current account profile (require_app_user)
  POST /account/password  — change the SESSION's own password (require_app_user + CSRF)

SAFETY invariants:
  - Responses NEVER contain a password, hash, salt, or any secret.
  - The password-change target is derived from the SESSION, never the request
    body — you can only change your own account.
  - Fail-closed: guest → 403, no session → 401, bad input → 4xx.
"""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_app_user, require_app_user_csrf
from app.api.schemas import (
    AccountResponse,
    PasswordChangeRequest,
    PasswordChangeResponse,
)

router = APIRouter(prefix="/account", tags=["account"])


@router.get("", response_model=AccountResponse)
def get_account(
    session: Annotated[dict[str, Any], Depends(require_app_user)],
) -> AccountResponse:
    """Return the current account profile. No secrets are ever included."""
    role = session.get("role", "guest")
    return AccountResponse(
        username=session.get("username"),
        role=role,
        data_source=session.get("data_source", "demo"),
        is_owner=role == "owner",
    )


@router.post("/password", response_model=PasswordChangeResponse)
def change_account_password(
    body: PasswordChangeRequest,
    session: Annotated[dict[str, Any], Depends(require_app_user_csrf)],
) -> PasswordChangeResponse:
    """Change the password of the SESSION's own account.

    The username is taken from the verified session — NOT the request body —
    so a caller can never change another account. Guests are rejected by
    require_app_user_csrf (403) before this body runs.
    """
    from app.services.auth_service import change_password

    # Username comes from the session, never the body.
    username = (session.get("username") or "").strip()
    if not username:
        # Owner session without a username should not happen; fail closed.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="계정을 확인할 수 없습니다.",
        )

    ok, msg = change_password(username, body.old_password, body.new_password)
    if not ok:
        # Wrong current password → 401; everything else (weak/empty/same) → 400.
        if "현재 비밀번호" in msg:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    return PasswordChangeResponse(status="changed", message=msg)
