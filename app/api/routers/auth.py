"""Authentication router — /api/auth/*

Endpoints:
  POST /auth/login   — local ID/PW or guest
  POST /auth/logout  — clear session cookie
  GET  /auth/me      — current session info (includes csrf_token for JS)
"""
from __future__ import annotations

import secrets
from typing import Annotated, Any

from fastapi import APIRouter, Cookie, HTTPException, Response, status

from app.api.schemas import LoginRequest, SessionResponse
from app.api.security import COOKIE_KWARGS, COOKIE_NAME, decode_session, encode_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=SessionResponse)
def login(body: LoginRequest, response: Response) -> SessionResponse:
    """Log in as guest or with local ID/PW credentials.

    - guest=true  → session {role:"guest", data_source:"demo"}
    - otherwise   → call login_or_register; 401 on failure

    A fresh csrf_token is generated and embedded in the session cookie at
    every login. JS reads it from GET /auth/me and sends it as X-CSRF-Token
    on every state-changing request.
    """
    if body.guest:
        csrf = secrets.token_hex(32)
        session_data: dict[str, Any] = {
            "role": "guest",
            "data_source": "demo",
            "csrf_token": csrf,
        }
        _set_cookie(response, session_data)
        return SessionResponse(role="guest", username=None, data_source="demo", csrf_token=csrf)

    # local login
    from app.services.auth_service import login_or_register

    username = (body.username or "").strip()
    password = body.password or ""

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="username and password are required",
        )

    ok, msg = login_or_register(username, password)
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

    csrf = secrets.token_hex(32)
    session_data = {
        "role": "owner",
        "username": username,
        "data_source": "backend",
        "csrf_token": csrf,
    }
    _set_cookie(response, session_data)
    return SessionResponse(role="owner", username=username, data_source="backend", csrf_token=csrf)


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    """Clear the session cookie."""
    response.delete_cookie(
        COOKIE_NAME,
        path=COOKIE_KWARGS.get("path", "/"),
        samesite=COOKIE_KWARGS.get("samesite", "lax"),
        httponly=COOKIE_KWARGS.get("httponly", True),
        secure=COOKIE_KWARGS.get("secure", False),
    )
    return {"status": "logged_out"}


@router.get("/me", response_model=SessionResponse)
def me(
    af_session: Annotated[str | None, Cookie(alias=COOKIE_NAME)] = None,
) -> SessionResponse:
    """Return the current session info, or 401 if not authenticated.

    Exposes csrf_token in JSON so the JS frontend can read it and send it
    back as X-CSRF-Token on state-changing requests.
    """
    if af_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    session = decode_session(af_session)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session"
        )
    return SessionResponse(
        role=session.get("role", "guest"),
        username=session.get("username"),
        data_source=session.get("data_source", "demo"),
        csrf_token=session.get("csrf_token"),
    )


# ── helpers ───────────────────────────────────────────────────────────────────

def _set_cookie(response: Response, session_data: dict[str, Any]) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=encode_session(session_data),
        **COOKIE_KWARGS,
    )
