"""User-owned integration credential registry.

Local prototype only: stores each approved user's LLM/SNS integration metadata
and optional token in the encrypted local vault. No provider API is called here,
and secret values are write-only at the API boundary.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

from app.ui import vault

_VAULT_KEY = "user_integrations"
_KST = timezone(timedelta(hours=9))
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
    owner_key = _user_key(username)
    records = _load_all().get(owner_key, {})
    items = []
    for provider in provider_catalog():
        record = records.get(provider["id"], {})
        items.append(_response(provider["id"], record if isinstance(record, dict) else None))
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
    provider = _provider(provider_id)
    owner_key = _user_key(username)
    now = _now()
    all_records = _load_all()
    user_records = all_records.setdefault(owner_key, {})
    current = user_records.get(provider["id"], {})
    if not isinstance(current, dict):
        current = {}

    clean_secret = _clean_optional(secret_value, max_len=4000)
    existing_secret = current.get("secret_value") if isinstance(current.get("secret_value"), str) else None
    next_secret = clean_secret if clean_secret is not None else existing_secret

    record = {
        "provider_id": provider["id"],
        "enabled": bool(enabled),
        "account_label": _clean_optional(account_label, max_len=160),
        "scopes": _clean_scopes(scopes or []),
        "note": _clean_optional(note, max_len=500),
        "secret_value": next_secret,
        "secret_hint": _secret_hint(next_secret),
        "created_at": current.get("created_at") or now,
        "updated_at": now,
    }
    user_records[provider["id"]] = record
    all_records[owner_key] = user_records
    _save_all(all_records)
    return _response(provider["id"], record)


def delete_user_integration(username: str, provider_id: str) -> dict[str, Any]:
    """Remove one provider record for a user."""
    provider = _provider(provider_id)
    owner_key = _user_key(username)
    all_records = _load_all()
    user_records = all_records.get(owner_key, {})
    if isinstance(user_records, dict):
        user_records.pop(provider["id"], None)
        all_records[owner_key] = user_records
        _save_all(all_records)
    return _response(provider["id"], None)


def _load_all() -> dict[str, dict[str, dict[str, Any]]]:
    data = vault.load()
    records = data.get(_VAULT_KEY, {})
    if not isinstance(records, dict):
        return {}
    return deepcopy(records)


def _save_all(records: dict[str, dict[str, dict[str, Any]]]) -> None:
    data = vault.load()
    data[_VAULT_KEY] = records
    vault.save(data)


def _provider(provider_id: str) -> dict[str, Any]:
    key = (provider_id or "").strip().lower()
    provider = _PROVIDERS.get(key)
    if provider is None:
        raise ValueError("unknown integration provider")
    return provider


def _response(provider_id: str, record: dict[str, Any] | None) -> dict[str, Any]:
    provider = _provider(provider_id)
    configured = bool(record and record.get("secret_value"))
    enabled = bool(record.get("enabled")) if record else False
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
        "account_label": record.get("account_label") if record else None,
        "scopes": record.get("scopes") if record else [],
        "secret_set": configured,
        "secret_hint": record.get("secret_hint") if record else None,
        "created_at": record.get("created_at") if record else None,
        "updated_at": record.get("updated_at") if record else None,
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


def _user_key(username: str) -> str:
    cleaned = " ".join((username or "").strip().split())
    if not cleaned:
        raise ValueError("approved account username is required")
    return cleaned.lower()


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


def _secret_hint(secret_value: str | None) -> str | None:
    if not secret_value:
        return None
    suffix = secret_value[-4:] if len(secret_value) > 4 else ""
    return f"****{suffix}" if suffix else "****"


def _now() -> str:
    return datetime.now(_KST).isoformat()
