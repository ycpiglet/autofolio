"""Authentication router — /api/auth/*

Endpoints:
  POST /auth/login   — approved local ID/PW; guest demo only with explicit dev opt-in
  POST /auth/logout  — clear session cookie
  GET  /auth/me      — current session info (includes csrf_token for JS)
"""
from __future__ import annotations

import secrets
from typing import Annotated, Any

from fastapi import APIRouter, Cookie, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse

from app.api.schemas import LoginRequest, SessionResponse, SsoProvidersResponse
from app.api.security import (
    COOKIE_KWARGS,
    COOKIE_NAME,
    OAUTH_STATE_COOKIE,
    decode_oauth_state,
    decode_session,
    encode_oauth_state,
    encode_session,
)
from app.services import sso
from app.services.auth_service import sso_role_for_email
from app.services.flags import guest_demo_enabled

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=SessionResponse)
def login(body: LoginRequest, response: Response) -> SessionResponse:
    """Log in with approved local credentials.

    - guest=true  → disabled by default; requires AUTOFOLIO_GUEST_DEMO_ENABLED=1
    - otherwise   → call approved local login; 401 on failure

    A fresh csrf_token is generated and embedded in the session cookie at
    every login. JS reads it from GET /auth/me and sends it as X-CSRF-Token
    on every state-changing request.
    """
    if body.guest:
        if not guest_demo_enabled():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="게스트 데모는 비활성화되어 있습니다. 가입 승인 후 로그인하세요.",
            )
        csrf = secrets.token_hex(32)
        session_data: dict[str, Any] = {
            "role": "guest",
            "data_source": "demo",
            "csrf_token": csrf,
        }
        _set_cookie(response, session_data)
        return SessionResponse(role="guest", username=None, data_source="demo", csrf_token=csrf)

    # local login
    from app.services.auth_service import login_or_register, role_for_user

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

    role = role_for_user(username)
    csrf = secrets.token_hex(32)
    session_data = {
        "role": role,
        "username": username,
        "data_source": "backend",
        "csrf_token": csrf,
    }
    _set_cookie(response, session_data)
    return SessionResponse(role=role, username=username, data_source="backend", csrf_token=csrf)


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


@router.get("/sso/providers", response_model=SsoProvidersResponse)
def sso_providers() -> SsoProvidersResponse:
    """Return public SSO/SNS provider availability.

    The response intentionally excludes client secrets, OAuth tokens, and
    provider endpoint URLs.
    """
    return SsoProvidersResponse(providers=sso.public_provider_list())


@router.get("/sso/{provider_id}/login")
def sso_login(
    provider_id: str,
    next_path: Annotated[str, Query(alias="next")] = "/home",
) -> RedirectResponse:
    """Start provider OAuth login with a short-lived signed state cookie."""
    provider = sso.get_provider(provider_id)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown SSO provider")
    if not provider.enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="SSO provider is not configured")

    safe_next = next_path if next_path.startswith("/") else "/home"
    state = secrets.token_urlsafe(32)
    response = RedirectResponse(
        sso.build_authorization_url(provider, state, next_path=safe_next),
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )
    response.set_cookie(
        key=OAUTH_STATE_COOKIE,
        value=encode_oauth_state({"provider": provider.id, "state": state, "next": safe_next}),
        max_age=600,
        **COOKIE_KWARGS,
    )
    return response


@router.get("/sso/{provider_id}/callback")
async def sso_callback(
    provider_id: str,
    code: str,
    state: str,
    af_oauth_state: Annotated[str | None, Cookie(alias=OAUTH_STATE_COOKIE)] = None,
) -> RedirectResponse:
    """Complete OAuth login, issue Autofolio owner session, then return to /home."""
    provider = sso.get_provider(provider_id)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown SSO provider")
    if not provider.enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="SSO provider is not configured")
    if af_oauth_state is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing OAuth state cookie")

    state_payload = decode_oauth_state(af_oauth_state)
    if (
        state_payload is None
        or state_payload.get("provider") != provider.id
        or state_payload.get("state") != state
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")

    try:
        profile = await sso.exchange_code_for_profile(provider, code)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"OAuth exchange failed: {exc}") from exc

    if not profile.subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OAuth profile has no subject")
    if not sso.email_allowed(profile.email):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="SSO email is not allowed")

    # 3-way role assignment: owner (designated only) | member (approved account) | deny
    role = sso_role_for_email(profile.email)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SSO 이메일이 승인된 계정(owner 또는 member)과 일치하지 않습니다.",
        )

    csrf = secrets.token_hex(32)
    redirect_to = _frontend_redirect_url(str(state_payload.get("next") or "/home"))
    response = RedirectResponse(redirect_to, status_code=status.HTTP_303_SEE_OTHER)
    _set_cookie(
        response,
        {
            "role": role,
            "username": profile.username,
            "data_source": f"sso:{provider.id}",
            "csrf_token": csrf,
            "provider": provider.id,
        },
    )
    response.delete_cookie(
        OAUTH_STATE_COOKIE,
        path=COOKIE_KWARGS.get("path", "/"),
        samesite=COOKIE_KWARGS.get("samesite", "lax"),
        httponly=COOKIE_KWARGS.get("httponly", True),
        secure=COOKIE_KWARGS.get("secure", False),
    )
    return response


# ── helpers ───────────────────────────────────────────────────────────────────

def _set_cookie(response: Response, session_data: dict[str, Any]) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=encode_session(session_data),
        **COOKIE_KWARGS,
    )


def _frontend_redirect_url(next_path: str) -> str:
    safe_next = next_path if next_path.startswith("/") else "/home"
    return f"{sso.public_base_url().rstrip('/')}{safe_next}"
