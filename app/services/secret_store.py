"""Secret-store adapter (TASK-087 A5).

Interface contract
------------------
ALL public methods return METADATA ONLY:

    {
        "provider_id": str,       # provider identifier
        "enabled": bool,          # whether the integration is active
        "masked_hint": str|None,  # e.g. "****abcd" — last 4 chars only
        "audit_id": str,          # UUID for audit trail
        "configured": bool,       # True when a secret is stored
        "account_label": str|None,
        "scopes": list[str],
        "created_at": str|None,
        "updated_at": str|None,
    }

No plaintext token/secret is ever returned or logged.
Logs must redact token/secret fields (never emit them).

Implementations
---------------
VaultSecretStore   : default — backed by the per-user Fernet vault
                     (app/ui/vault.py).  Behavior-compatible with the
                     existing integrations harness.
SupabaseSecretStore: STUB — raises NotImplementedError on every call.
                     No real Supabase connection is made.
                     See TASK-087 for the implementation roadmap.
"""
from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

from app.ui import vault

_log = logging.getLogger(__name__)

_VAULT_KEY = "user_integrations"
_KST = timezone(timedelta(hours=9))

MetadataOnly = dict[str, Any]


# ── Abstract interface ─────────────────────────────────────────────────────────

class AbstractSecretStore(ABC):
    """Metadata-only interface for user-owned integration secrets."""

    @abstractmethod
    def write(
        self,
        user_id: str,
        provider_id: str,
        token: str | None,
        *,
        account_label: str | None = None,
        scopes: list[str] | None = None,
        enabled: bool = True,
        note: str | None = None,
    ) -> MetadataOnly:
        """Store or replace a secret. token=None preserves existing. Metadata only."""

    @abstractmethod
    def rotate(
        self,
        user_id: str,
        provider_id: str,
        new_token: str,
    ) -> MetadataOnly:
        """Replace secret with new_token, tombstone old reference. Metadata only."""

    @abstractmethod
    def disable(self, user_id: str, provider_id: str) -> MetadataOnly:
        """Disable the integration without deleting the secret. Metadata only."""

    @abstractmethod
    def delete(self, user_id: str, provider_id: str) -> MetadataOnly:
        """Remove the secret payload. Returns tombstone metadata only."""

    @abstractmethod
    def read_metadata(self, user_id: str, provider_id: str) -> MetadataOnly:
        """Read metadata for user_id's provider record. Tenant-scoped. No secret."""


# ── Default implementation: per-user Fernet vault ─────────────────────────────

class VaultSecretStore(AbstractSecretStore):
    """Secret store backed by the local per-user Fernet vault.

    Tenant scoping: every method operates only on the requesting user_id's
    records.  Cross-tenant access is not possible — records are keyed by
    user_id and only that user's records are loaded or mutated.

    The vault continues to store the encrypted secret payload so that existing
    integrations behaviour is preserved.  All PUBLIC methods return metadata
    only; the secret value is never surfaced.
    """

    # ── Public interface ───────────────────────────────────────────────────────

    def write(
        self,
        user_id: str,
        provider_id: str,
        token: str | None,
        *,
        account_label: str | None = None,
        scopes: list[str] | None = None,
        enabled: bool = True,
        note: str | None = None,
    ) -> MetadataOnly:
        user_key = _user_key(user_id)
        now = _now()
        all_records = self._load_all()
        user_records = all_records.setdefault(user_key, {})
        current = user_records.get(provider_id, {})
        if not isinstance(current, dict):
            current = {}

        existing_secret = current.get("secret_value") if isinstance(current.get("secret_value"), str) else None
        next_secret = token if token is not None else existing_secret

        record = {
            "provider_id": provider_id,
            "enabled": bool(enabled),
            "account_label": account_label,
            "scopes": list(scopes or []),
            "note": note,
            "secret_value": next_secret,
            "secret_hint": _masked_hint(next_secret),
            "created_at": current.get("created_at") or now,
            "updated_at": now,
        }
        user_records[provider_id] = record
        all_records[user_key] = user_records
        self._save_all(all_records)
        _log.info("secret_store.write provider=%s user=%s", provider_id, _redact_user(user_id))
        return self._to_metadata(provider_id, record)

    def rotate(
        self,
        user_id: str,
        provider_id: str,
        new_token: str,
    ) -> MetadataOnly:
        user_key = _user_key(user_id)
        all_records = self._load_all()
        user_records = all_records.get(user_key, {})
        current = user_records.get(provider_id, {}) if isinstance(user_records, dict) else {}
        if not isinstance(current, dict):
            current = {}

        now = _now()
        record = {
            **current,
            "secret_value": new_token,
            "secret_hint": _masked_hint(new_token),
            "updated_at": now,
        }
        user_records[provider_id] = record
        all_records[user_key] = user_records
        self._save_all(all_records)
        _log.info("secret_store.rotate provider=%s user=%s", provider_id, _redact_user(user_id))
        return self._to_metadata(provider_id, record)

    def disable(self, user_id: str, provider_id: str) -> MetadataOnly:
        user_key = _user_key(user_id)
        all_records = self._load_all()
        user_records = all_records.get(user_key, {})
        current = user_records.get(provider_id, {}) if isinstance(user_records, dict) else {}
        if not isinstance(current, dict):
            current = {}

        record = {**current, "enabled": False, "updated_at": _now()}
        user_records[provider_id] = record
        all_records[user_key] = user_records
        self._save_all(all_records)
        _log.info("secret_store.disable provider=%s user=%s", provider_id, _redact_user(user_id))
        return self._to_metadata(provider_id, record)

    def delete(self, user_id: str, provider_id: str) -> MetadataOnly:
        user_key = _user_key(user_id)
        all_records = self._load_all()
        user_records = all_records.get(user_key, {})
        if isinstance(user_records, dict):
            user_records.pop(provider_id, None)
            all_records[user_key] = user_records
            self._save_all(all_records)
        _log.info("secret_store.delete provider=%s user=%s", provider_id, _redact_user(user_id))
        return self._to_metadata(provider_id, None)

    def read_metadata(self, user_id: str, provider_id: str) -> MetadataOnly:
        user_key = _user_key(user_id)
        all_records = self._load_all()
        user_records = all_records.get(user_key, {})
        record = user_records.get(provider_id) if isinstance(user_records, dict) else None
        return self._to_metadata(provider_id, record)

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _load_all(self) -> dict:
        data = vault.load()
        records = data.get(_VAULT_KEY, {})
        return deepcopy(records) if isinstance(records, dict) else {}

    def _save_all(self, records: dict) -> None:
        data = vault.load()
        data[_VAULT_KEY] = records
        vault.save(data)

    @staticmethod
    def _to_metadata(provider_id: str, record: dict | None) -> MetadataOnly:
        configured = bool(record and record.get("secret_value"))
        enabled = bool(record.get("enabled")) if record else False
        return {
            "provider_id": provider_id,
            "enabled": enabled,
            "masked_hint": record.get("secret_hint") if record else None,
            "audit_id": str(uuid.uuid4()),
            "configured": configured,
            "account_label": record.get("account_label") if record else None,
            "scopes": list(record.get("scopes") or []) if record else [],
            "created_at": record.get("created_at") if record else None,
            "updated_at": record.get("updated_at") if record else None,
        }


# ── Supabase Vault/KMS stub (NOT YET IMPLEMENTED) ────────────────────────────

class SupabaseSecretStore(AbstractSecretStore):
    """STUB — Supabase Vault / KMS integration.

    NOT IMPLEMENTED. Raises NotImplementedError on every call.
    No Supabase connection is made. No secrets are stored or read.
    See TASK-087 for the implementation roadmap and required R3 gates.
    """

    _MSG = (
        "Supabase Vault/KMS integration is not yet implemented. "
        "See TASK-087 for required R3 gates before this store can be activated."
    )

    def write(self, user_id, provider_id, token, **kwargs) -> MetadataOnly:
        raise NotImplementedError(self._MSG)

    def rotate(self, user_id, provider_id, new_token) -> MetadataOnly:
        raise NotImplementedError(self._MSG)

    def disable(self, user_id, provider_id) -> MetadataOnly:
        raise NotImplementedError(self._MSG)

    def delete(self, user_id, provider_id) -> MetadataOnly:
        raise NotImplementedError(self._MSG)

    def read_metadata(self, user_id, provider_id) -> MetadataOnly:
        raise NotImplementedError(self._MSG)


# ── Private helpers ────────────────────────────────────────────────────────────

def _user_key(user_id: str) -> str:
    cleaned = " ".join((user_id or "").strip().split())
    if not cleaned:
        raise ValueError("user_id is required")
    return cleaned.lower()


def _masked_hint(token: str | None) -> str | None:
    if not token:
        return None
    suffix = token[-4:] if len(token) > 4 else ""
    return f"****{suffix}" if suffix else "****"


def _redact_user(user_id: str) -> str:
    if not user_id or "@" not in user_id:
        return "***"
    local, domain = user_id.split("@", 1)
    return f"{local[:2]}***@{domain}" if len(local) > 2 else f"***@{domain}"


def _now() -> str:
    return datetime.now(_KST).isoformat()
