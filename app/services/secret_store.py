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
VaultSecretStore    : default (SQLite/local) — backed by the per-user Fernet
                      vault (app/ui/vault.py). Behavior-compatible with the
                      existing integrations harness. Used whenever DATABASE_URL
                      is NOT a Postgres URL, so the local path is byte-identical.
EnvelopeSecretStore : Postgres (production) — durable, envelope-encrypted secret
                      store (P2). Each user's secret is sealed under a fresh
                      per-user DEK; the DEK is wrapped under the master KEK
                      (AUTOFOLIO_VAULT_KEY, off-disk). Only {wrapped_dek,
                      ciphertext, key_version} land in Postgres, so the DB host
                      cannot read secrets without the KEK. Survives Railway's
                      ephemeral filesystem (which a local Fernet file would not).
SupabaseSecretStore : STUB — raises NotImplementedError on every call.
                      No real Supabase connection is made.

Backend selection lives in :func:`get_secret_store`.
"""
from __future__ import annotations

import contextlib
import json
import logging
import sqlite3 as _sqlite3
import uuid
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from cryptography.fernet import InvalidToken

from app.services import envelope
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

    def reveal(self, user_id: str, provider_id: str) -> str | None:
        """SERVER-ONLY: return the plaintext secret for use at call time.

        Used by the trading engine / KIS resolver to obtain a user's credential
        at the moment of use. NEVER surface this via an API response or a log.
        Returns ``None`` when no secret is configured. Mirrors
        :meth:`EnvelopeSecretStore.reveal` so the engine can call the same
        method on either backend.
        """
        user_key = _user_key(user_id)
        all_records = self._load_all()
        user_records = all_records.get(user_key, {})
        record = user_records.get(provider_id) if isinstance(user_records, dict) else None
        if not isinstance(record, dict):
            return None
        value = record.get("secret_value")
        return value if isinstance(value, str) and value else None

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


# ── Postgres-durable envelope store (P2) ─────────────────────────────────────

class EnvelopeSecretStore(AbstractSecretStore):
    """Durable, per-user **envelope-encrypted** secret store (Postgres backend).

    Why this exists
    ---------------
    Production runs on Railway, whose filesystem is ephemeral (wiped on every
    redeploy), so the local Fernet vault file used by :class:`VaultSecretStore`
    would be LOST. This store persists secrets DURABLY through the database seam
    (:func:`app.database.sqlite_db.get_connection`) — Postgres in production,
    SQLite for tests/local — so the same code is exercised on both.

    Envelope scheme (DEK-under-KEK)
    ------------------------------
    * A fresh random **DEK** (Fernet key) is generated per user/secret and seals
      the payload: ``ciphertext = encrypt(secret, DEK)``.
    * The DEK is **wrapped** under the master **KEK**
      (``AUTOFOLIO_VAULT_KEY`` via :func:`app.ui.vault.key_bytes`, off-disk):
      ``wrapped_dek = wrap(DEK, KEK)``.
    * Only ``{wrapped_dek, ciphertext, key_version}`` (plus non-secret metadata)
      are stored in ``integration_secret_blobs``. The KEK NEVER touches the DB,
      so the DB host (Supabase) cannot read secrets, and DB compromise without
      the KEK yields nothing.
    * **Per-user isolation**: each user has a distinct DEK, so one user's
      ``wrapped_dek``/``ciphertext`` is meaningless for another user.

    All PUBLIC metadata methods return METADATA ONLY (identical contract to
    :class:`VaultSecretStore`). The plaintext secret is surfaced ONLY by the
    server-side :meth:`reveal` (decrypt-at-use), never via an API response.

    Note on the blob table: the server-only ``integration_secret_blobs`` table
    is the durable source of truth and carries both the encrypted secret
    (``wrapped_dek`` + ``ciphertext`` — the ONLY secret-bearing columns) and the
    non-secret metadata (enabled, masked_hint, account_label, scopes, note,
    timestamps). It is keyed by the server's ``user_id`` text identifier and has
    RLS enabled with NO client policies (server/service-role only). Mirroring
    the client-facing ``integration_secret_metadata`` RLS view (which carries an
    ``auth.users`` uuid FK) is deferred to P3, when real auth uuids are wired.
    """

    _TABLE = "integration_secret_blobs"

    def __init__(self, db_path: Path | None = None) -> None:
        # db_path is honored only on the SQLite backend (tests/local). On the
        # Postgres backend get_connection ignores it and routes via DATABASE_URL.
        self._db_path = db_path

    @contextlib.contextmanager
    def _connect(self):
        from app.database.sqlite_db import get_connection

        conn = get_connection(self._db_path)
        try:
            with conn as c:
                yield c
        finally:
            # sqlite3.Connection.__exit__ commits/rolls back but does NOT close.
            # PgConnection.__exit__ already closes — only close here for SQLite.
            if isinstance(conn, _sqlite3.Connection):
                conn.close()

    # ── Public interface (metadata only) ─────────────────────────────────────

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
        scopes_json = json.dumps(list(scopes or []), ensure_ascii=False)
        with self._connect() as conn:
            existing = self._fetch(conn, user_key, provider_id)
            if token is not None:
                wrapped_dek, ciphertext, key_version = self._seal(token)
                masked_hint = _masked_hint(token)
            elif existing is not None:
                # token=None preserves the existing secret (no re-encryption).
                wrapped_dek = existing["wrapped_dek"]
                ciphertext = existing["ciphertext"]
                key_version = existing["key_version"]
                masked_hint = existing["masked_hint"]
            else:
                # No token and no prior secret → metadata-only row, not configured.
                wrapped_dek, ciphertext, key_version, masked_hint = "", "", envelope.CURRENT_KEY_VERSION, None
            created_at = existing["created_at"] if existing else now
            self._upsert(
                conn,
                user_key=user_key,
                provider_id=provider_id,
                wrapped_dek=wrapped_dek,
                ciphertext=ciphertext,
                key_version=key_version,
                enabled=bool(enabled),
                masked_hint=masked_hint,
                account_label=account_label,
                scopes_json=scopes_json,
                note=note,
                created_at=created_at,
                updated_at=now,
            )
            record = self._fetch(conn, user_key, provider_id)
        _log.info("secret_store.write provider=%s user=%s", provider_id, _redact_user(user_id))
        return self._to_metadata(provider_id, record)

    def rotate(self, user_id: str, provider_id: str, new_token: str) -> MetadataOnly:
        user_key = _user_key(user_id)
        now = _now()
        with self._connect() as conn:
            existing = self._fetch(conn, user_key, provider_id)
            wrapped_dek, ciphertext, key_version = self._seal(new_token)
            created_at = existing["created_at"] if existing else now
            self._upsert(
                conn,
                user_key=user_key,
                provider_id=provider_id,
                wrapped_dek=wrapped_dek,
                ciphertext=ciphertext,
                key_version=key_version,
                enabled=bool(existing["enabled"]) if existing else True,
                masked_hint=_masked_hint(new_token),
                account_label=existing["account_label"] if existing else None,
                scopes_json=existing["scopes"] if existing else "[]",
                note=existing["note"] if existing else None,
                created_at=created_at,
                updated_at=now,
            )
            record = self._fetch(conn, user_key, provider_id)
        _log.info("secret_store.rotate provider=%s user=%s", provider_id, _redact_user(user_id))
        return self._to_metadata(provider_id, record)

    def disable(self, user_id: str, provider_id: str) -> MetadataOnly:
        user_key = _user_key(user_id)
        with self._connect() as conn:
            conn.execute(
                f"UPDATE {self._TABLE} SET enabled = ?, updated_at = ? "
                "WHERE user_id = ? AND provider = ?",
                (False, _now(), user_key, provider_id),
            )
            record = self._fetch(conn, user_key, provider_id)
        _log.info("secret_store.disable provider=%s user=%s", provider_id, _redact_user(user_id))
        return self._to_metadata(provider_id, record)

    def delete(self, user_id: str, provider_id: str) -> MetadataOnly:
        user_key = _user_key(user_id)
        with self._connect() as conn:
            conn.execute(
                f"DELETE FROM {self._TABLE} WHERE user_id = ? AND provider = ?",
                (user_key, provider_id),
            )
        _log.info("secret_store.delete provider=%s user=%s", provider_id, _redact_user(user_id))
        return self._to_metadata(provider_id, None)

    def read_metadata(self, user_id: str, provider_id: str) -> MetadataOnly:
        user_key = _user_key(user_id)
        with self._connect() as conn:
            record = self._fetch(conn, user_key, provider_id)
        return self._to_metadata(provider_id, record)

    def reveal(self, user_id: str, provider_id: str) -> str | None:
        """SERVER-ONLY: unwrap the DEK with the KEK, decrypt, return plaintext.

        The trading engine / KIS resolver calls this at the moment a credential
        is used. NEVER surface the return value via an API response or a log.
        Returns ``None`` when no secret is configured or when the blob cannot
        be decrypted (e.g. wrapped under a rotated/old KEK — caller treats
        this as a missing secret rather than crashing at use-time).
        """
        user_key = _user_key(user_id)
        with self._connect() as conn:
            row = conn.execute(
                f"SELECT wrapped_dek, ciphertext, key_version FROM {self._TABLE} "
                "WHERE user_id = ? AND provider = ?",
                (user_key, provider_id),
            ).fetchone()
        if row is None:
            return None
        record = dict(row)
        wrapped_dek = record.get("wrapped_dek")
        ciphertext = record.get("ciphertext")
        if not wrapped_dek or not ciphertext:
            return None
        kek = vault.key_bytes(require_env=True)
        try:
            dek = envelope.unwrap_dek(wrapped_dek, kek)
            return envelope.decrypt(ciphertext, dek)
        except Exception:  # InvalidToken (wrong/rotated KEK), ValueError, malformed blob
            _log.warning(
                "secret_store.reveal: blob undecryptable — may be wrapped under "
                "a rotated or old KEK, or the blob is corrupt. "
                "provider=%s user=%s key_version=%s — returning None "
                "(no secret/DEK/KEK in this log)",
                provider_id,
                _redact_user(user_id),
                record.get("key_version"),
            )
            return None

    # ── Internal helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _seal(token: str) -> tuple[str, str, int]:
        """Generate a DEK, encrypt *token* under it, wrap the DEK under the KEK."""
        kek = vault.key_bytes(require_env=True)
        dek = envelope.generate_dek()
        wrapped_dek = envelope.wrap_dek(dek, kek)
        ciphertext = envelope.encrypt(token, dek)
        return wrapped_dek, ciphertext, envelope.CURRENT_KEY_VERSION

    def _fetch(self, conn, user_key: str, provider_id: str) -> dict | None:
        row = conn.execute(
            f"SELECT * FROM {self._TABLE} WHERE user_id = ? AND provider = ?",
            (user_key, provider_id),
        ).fetchone()
        return dict(row) if row is not None else None

    def _upsert(self, conn, **f: Any) -> None:
        # ON CONFLICT(user_id, provider) DO UPDATE — created_at is intentionally
        # NOT updated, so the original creation time is preserved. `excluded` is
        # supported by both SQLite (3.24+) and Postgres.
        conn.execute(
            f"""
            INSERT INTO {self._TABLE}
                (user_id, provider, wrapped_dek, ciphertext, key_version,
                 enabled, masked_hint, account_label, scopes, note,
                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, provider) DO UPDATE SET
                wrapped_dek = excluded.wrapped_dek,
                ciphertext = excluded.ciphertext,
                key_version = excluded.key_version,
                enabled = excluded.enabled,
                masked_hint = excluded.masked_hint,
                account_label = excluded.account_label,
                scopes = excluded.scopes,
                note = excluded.note,
                updated_at = excluded.updated_at
            """,
            (
                f["user_key"], f["provider_id"], f["wrapped_dek"], f["ciphertext"],
                f["key_version"], f["enabled"], f["masked_hint"], f["account_label"],
                f["scopes_json"], f["note"], f["created_at"], f["updated_at"],
            ),
        )

    @staticmethod
    def _to_metadata(provider_id: str, record: dict | None) -> MetadataOnly:
        # `configured` mirrors VaultSecretStore: a secret is present iff a masked
        # hint exists (the hint is set only when a real secret is sealed).
        configured = bool(record and record.get("masked_hint"))
        enabled = bool(record.get("enabled")) if record else False
        scopes_raw = record.get("scopes") if record else None
        try:
            scopes = json.loads(scopes_raw) if scopes_raw else []
        except (TypeError, ValueError):
            scopes = []
        return {
            "provider_id": provider_id,
            "enabled": enabled,
            "masked_hint": record.get("masked_hint") if record else None,
            "audit_id": str(uuid.uuid4()),
            "configured": configured,
            "account_label": record.get("account_label") if record else None,
            "scopes": list(scopes) if isinstance(scopes, list) else [],
            "created_at": record.get("created_at") if record else None,
            "updated_at": record.get("updated_at") if record else None,
        }


# ── Backend selection ────────────────────────────────────────────────────────

def get_secret_store() -> AbstractSecretStore:
    """Return the secret store for the active backend.

    * ``DATABASE_URL`` is a Postgres URL → :class:`EnvelopeSecretStore`
      (durable, envelope-encrypted; survives Railway's ephemeral filesystem).
    * Otherwise (unset/empty → the default SQLite/local path) →
      :class:`VaultSecretStore` (file vault), BYTE-IDENTICAL to the historical
      behaviour. The envelope store is never even instantiated on this path.
    """
    from app.config.settings import settings
    from app.database.pg_db import is_postgres_url

    if is_postgres_url(settings.database_url):
        return EnvelopeSecretStore()
    return VaultSecretStore()


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
