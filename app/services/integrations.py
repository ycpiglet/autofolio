"""User-owned integration credential registry.

Local prototype only: stores each approved user's LLM/SNS integration metadata
and optional token in the encrypted local vault. No provider API is called here,
and secret values are write-only at the API boundary.

Token writes and reads are routed through VaultSecretStore (TASK-087 A5) so
the metadata-only interface is enforced at the service layer.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.secret_store import get_secret_store

# Backend-selected at import: VaultSecretStore on the default SQLite/local path
# (byte-identical), EnvelopeSecretStore when DATABASE_URL is a Postgres URL.
_STORE = get_secret_store()

_MAX_SCOPES = 12

_PROVIDERS: dict[str, dict[str, Any]] = {
    "openai": {
        "id": "openai",
        "label": "OpenAI",
        "kind": "llm",
        "auth_type": "api_key",
        "secret_label": "API key",
        "account_label_hint": "email or project",
        "description": "User-owned LLM API key for agent analysis.",
    },
    "anthropic": {
        "id": "anthropic",
        "label": "Anthropic",
        "kind": "llm",
        "auth_type": "api_key",
        "secret_label": "API key",
        "account_label_hint": "email or workspace",
        "description": "User-owned Claude API key for agent analysis.",
    },
    "telegram": {
        "id": "telegram",
        "label": "Telegram",
        "kind": "sns",
        "auth_type": "bot_token",
        "secret_label": "Bot token",
        "account_label_hint": "chat id or handle",
        "description": "User-owned Telegram destination for notifications.",
    },
    "google": {
        "id": "google",
        "label": "Google",
        "kind": "sns",
        "auth_type": "oauth_token",
        "secret_label": "OAuth token",
        "account_label_hint": "Google account",
        "description": "User-owned Google integration placeholder.",
    },
    "naver": {
        "id": "naver",
        "label": "Naver",
        "kind": "sns",
        "auth_type": "oauth_token",
        "secret_label": "OAuth token",
        "account_label_hint": "Naver account",
        "description": "User-owned Naver integration placeholder.",
    },
    "kakao": {
        "id": "kakao",
        "label": "Kakao",
        "kind": "sns",
        "auth_type": "oauth_token",
        "secret_label": "OAuth token",
        "account_label_hint": "Kakao account",
        "description": "User-owned Kakao integration placeholder.",
    },
    "x": {
        "id": "x",
        "label": "X",
        "kind": "sns",
        "auth_type": "oauth_token",
        "secret_label": "OAuth token",
        "account_label_hint": "X account",
        "description": "User-owned X integration placeholder.",
    },
}


def provider_catalog() -> list[dict[str, Any]]:
    """Return safe public metadata for supported integration providers."""
    return [deepcopy(provider) for provider in _PROVIDERS.values()]


def list_user_integrations(username: str) -> dict[str, Any]:
    """Return one user's configured integration status without secrets."""
    _require_username(username)
    items = []
    for provider in provider_catalog():
        meta = _STORE.read_metadata(username, provider["id"])
        items.append(_response_from_meta(provider["id"], meta))
    return {"providers": provider_catalog(), "integrations": items}


def upsert_user_integration(
    username: str,
    provider_id: str,
    *,
    secret_value: str | None = None,
    account_label: str | None = None,
    scopes: list[str] | None = None,
    enabled: bool = True,
    note: str | None = None,
) -> dict[str, Any]:
    """Create or update one provider record for a user."""
    _provider(provider_id)  # raises ValueError for unknown providers

    clean_secret = _clean_optional(secret_value, max_len=4000)
    clean_label = _clean_optional(account_label, max_len=160)
    clean_note = _clean_optional(note, max_len=500)
    clean_scopes = _clean_scopes(scopes or [])

    meta = _STORE.write(
        username,
        provider_id,
        clean_secret,
        account_label=clean_label,
        scopes=clean_scopes,
        enabled=bool(enabled),
        note=clean_note,
    )
    return _response_from_meta(provider_id, meta)


def delete_user_integration(username: str, provider_id: str) -> dict[str, Any]:
    """Remove one provider record for a user."""
    _provider(provider_id)  # raises ValueError for unknown providers
    meta = _STORE.delete(username, provider_id)
    return _response_from_meta(provider_id, meta)


def _response_from_meta(provider_id: str, meta: dict[str, Any] | None) -> dict[str, Any]:
    provider = _provider(provider_id)
    configured = bool(meta and meta.get("configured"))
    enabled = bool(meta.get("enabled")) if meta else False
    status = "not_configured"
    if configured and enabled:
        status = "configured"
    elif configured:
        status = "disabled"
    return {
        "provider_id": provider["id"],
        "label": provider["label"],
        "kind": provider["kind"],
        "auth_type": provider["auth_type"],
        "configured": configured,
        "enabled": enabled,
        "account_label": meta.get("account_label") if meta else None,
        "scopes": list(meta.get("scopes") or []) if meta else [],
        "secret_set": configured,
        "secret_hint": meta.get("masked_hint") if meta else None,
        "created_at": meta.get("created_at") if meta else None,
        "updated_at": meta.get("updated_at") if meta else None,
        "last_checked_at": None,
        "status": status,
        "message": _message(status),
    }


def _message(status: str) -> str:
    if status == "configured":
        return "연동 정보가 저장되었습니다."
    if status == "disabled":
        return "연동 정보는 저장되어 있지만 비활성 상태입니다."
    return "연동 정보가 없습니다."


def _require_username(username: str) -> str:
    cleaned = " ".join((username or "").strip().split())
    if not cleaned:
        raise ValueError("approved account username is required")
    return cleaned.lower()


def _provider(provider_id: str) -> dict[str, Any]:
    key = (provider_id or "").strip().lower()
    provider = _PROVIDERS.get(key)
    if provider is None:
        raise ValueError("unknown integration provider")
    return provider


def _clean_optional(value: str | None, *, max_len: int) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(str(value).strip().split())
    if not cleaned:
        return None
    if len(cleaned) > max_len:
        raise ValueError("value is too long")
    return cleaned


def _clean_scopes(scopes: list[str]) -> list[str]:
    cleaned: list[str] = []
    for raw in scopes[:_MAX_SCOPES]:
        value = _clean_optional(raw, max_len=60)
        if value and value not in cleaned:
            cleaned.append(value)
    return cleaned
