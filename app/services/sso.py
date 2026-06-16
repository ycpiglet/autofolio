"""SSO/SNS OAuth helpers for the FastAPI auth router.

Secrets are read only from environment variables. Public API responses expose
provider availability, never client secrets or tokens.
"""
from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx


@dataclass(frozen=True)
class SsoProvider:
    id: str
    label: str
    kind: str
    auth_url: str
    token_url: str
    userinfo_url: str
    scope: str
    client_id: str
    client_secret: str
    requires_secret: bool = True

    @property
    def enabled(self) -> bool:
        if self.requires_secret:
            return bool(self.client_id and self.client_secret)
        return bool(self.client_id)


@dataclass(frozen=True)
class SsoProfile:
    provider: str
    subject: str
    email: str | None
    name: str | None

    @property
    def username(self) -> str:
        return self.email or self.name or f"{self.provider}:{self.subject}"


def _env(*names: str) -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value.strip()
    return ""


def public_base_url() -> str:
    return _env("AUTOFOLIO_PUBLIC_BASE_URL", "NEXT_PUBLIC_BASE_URL") or "http://127.0.0.1:3000"


def frontend_home_url() -> str:
    return _env("AUTOFOLIO_FRONTEND_HOME_URL") or f"{public_base_url().rstrip('/')}/home"


def frontend_login_url() -> str:
    return _env("AUTOFOLIO_FRONTEND_LOGIN_URL") or f"{public_base_url().rstrip('/')}/login"


def providers() -> dict[str, SsoProvider]:
    return {
        "google": SsoProvider(
            id="google",
            label="Google",
            kind="oidc",
            auth_url=_env("AUTOFOLIO_GOOGLE_AUTH_URL") or "https://accounts.google.com/o/oauth2/v2/auth",
            token_url=_env("AUTOFOLIO_GOOGLE_TOKEN_URL") or "https://oauth2.googleapis.com/token",
            userinfo_url=_env("AUTOFOLIO_GOOGLE_USERINFO_URL") or "https://openidconnect.googleapis.com/v1/userinfo",
            scope=_env("AUTOFOLIO_GOOGLE_SCOPE") or "openid email profile",
            client_id=_env("AUTOFOLIO_GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_ID"),
            client_secret=_env("AUTOFOLIO_GOOGLE_CLIENT_SECRET", "GOOGLE_CLIENT_SECRET"),
        ),
        "kakao": SsoProvider(
            id="kakao",
            label="Kakao",
            kind="sns",
            auth_url=_env("AUTOFOLIO_KAKAO_AUTH_URL") or "https://kauth.kakao.com/oauth/authorize",
            token_url=_env("AUTOFOLIO_KAKAO_TOKEN_URL") or "https://kauth.kakao.com/oauth/token",
            userinfo_url=_env("AUTOFOLIO_KAKAO_USERINFO_URL") or "https://kapi.kakao.com/v2/user/me",
            scope=_env("AUTOFOLIO_KAKAO_SCOPE") or "profile_nickname account_email",
            client_id=_env("AUTOFOLIO_KAKAO_REST_API_KEY", "AUTOFOLIO_KAKAO_CLIENT_ID", "KAKAO_REST_API_KEY"),
            client_secret=_env("AUTOFOLIO_KAKAO_CLIENT_SECRET", "KAKAO_CLIENT_SECRET"),
            requires_secret=False,
        ),
        "naver": SsoProvider(
            id="naver",
            label="Naver",
            kind="sns",
            auth_url=_env("AUTOFOLIO_NAVER_AUTH_URL") or "https://nid.naver.com/oauth2.0/authorize",
            token_url=_env("AUTOFOLIO_NAVER_TOKEN_URL") or "https://nid.naver.com/oauth2.0/token",
            userinfo_url=_env("AUTOFOLIO_NAVER_USERINFO_URL") or "https://openapi.naver.com/v1/nid/me",
            scope=_env("AUTOFOLIO_NAVER_SCOPE") or "name email",
            client_id=_env("AUTOFOLIO_NAVER_CLIENT_ID", "NAVER_CLIENT_ID"),
            client_secret=_env("AUTOFOLIO_NAVER_CLIENT_SECRET", "NAVER_CLIENT_SECRET"),
        ),
    }


def get_provider(provider_id: str) -> SsoProvider | None:
    return providers().get(provider_id)


def public_provider_list() -> list[dict[str, Any]]:
    return [
        {
            "id": provider.id,
            "label": provider.label,
            "kind": provider.kind,
            "enabled": provider.enabled,
        }
        for provider in providers().values()
    ]


def redirect_uri(provider_id: str) -> str:
    return f"{public_base_url().rstrip('/')}/api/auth/sso/{provider_id}/callback"


def build_authorization_url(provider: SsoProvider, state: str, *, next_path: str = "/home") -> str:
    query: dict[str, str] = {
        "response_type": "code",
        "client_id": provider.client_id,
        "redirect_uri": redirect_uri(provider.id),
        "state": state,
    }
    if provider.scope:
        query["scope"] = provider.scope
    if provider.id == "google":
        query["nonce"] = secrets.token_urlsafe(24)
        query["prompt"] = "select_account"
    if provider.id == "naver":
        # Naver uses state for CSRF and does not need scope for basic profile,
        # but keeping configured scope is harmless for providers that accept it.
        query.pop("scope", None)
    if next_path and next_path != "/home":
        query["next"] = next_path
    return f"{provider.auth_url}?{urlencode(query)}"


def email_allowed(email: str | None) -> bool:
    raw = _env("AUTOFOLIO_SSO_ALLOWED_EMAILS")
    if not raw:
        return True
    allowed = {item.strip().lower() for item in raw.split(",") if item.strip()}
    return bool(email and email.lower() in allowed)


async def exchange_code_for_profile(provider: SsoProvider, code: str) -> SsoProfile:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri(provider.id),
        "client_id": provider.client_id,
    }
    if provider.client_secret:
        data["client_secret"] = provider.client_secret

    async with httpx.AsyncClient(timeout=10.0) as client:
        token_resp = await client.post(
            provider.token_url,
            data=data,
            headers={"Accept": "application/json"},
        )
        token_resp.raise_for_status()
        token_payload = token_resp.json()
        access_token = token_payload.get("access_token")
        if not access_token:
            raise ValueError("OAuth token response did not include access_token")

        user_resp = await client.get(
            provider.userinfo_url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
        )
        user_resp.raise_for_status()
        return normalize_profile(provider.id, user_resp.json())


def normalize_profile(provider_id: str, payload: dict[str, Any]) -> SsoProfile:
    if provider_id == "google":
        return SsoProfile(
            provider=provider_id,
            subject=str(payload.get("sub") or payload.get("id") or ""),
            email=payload.get("email"),
            name=payload.get("name"),
        )
    if provider_id == "kakao":
        account = payload.get("kakao_account") or {}
        profile = account.get("profile") or {}
        return SsoProfile(
            provider=provider_id,
            subject=str(payload.get("id") or ""),
            email=account.get("email"),
            name=profile.get("nickname") or payload.get("properties", {}).get("nickname"),
        )
    if provider_id == "naver":
        response = payload.get("response") or {}
        return SsoProfile(
            provider=provider_id,
            subject=str(response.get("id") or payload.get("id") or ""),
            email=response.get("email"),
            name=response.get("name") or response.get("nickname"),
        )
    return SsoProfile(
        provider=provider_id,
        subject=str(payload.get("sub") or payload.get("id") or ""),
        email=payload.get("email"),
        name=payload.get("name"),
    )
