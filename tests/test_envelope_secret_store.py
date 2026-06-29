"""P2 EnvelopeSecretStore + backend-selection tests (security-critical).

Exercises the durable, envelope-encrypted store against a TEMP SQLite DB (with
the integration_secret_blobs table) using a TEST-generated KEK, plus:
  * set -> read_metadata (metadata only) -> reveal (plaintext) round-trip,
  * cross-user isolation (each user reveals only their own secret; user A's
    stored ciphertext cannot be decrypted with user B's unwrapped DEK),
  * no-plaintext leak (the raw secret is ABSENT from the stored row and from
    every metadata response),
  * the byte-identical backend selection: factory returns VaultSecretStore when
    DATABASE_URL is unset, EnvelopeSecretStore for a Postgres URL.
  * the 0006 Postgres migration parses (sqlglot, read='postgres').
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest
from cryptography.fernet import Fernet, InvalidToken


def _fresh_kek(monkeypatch) -> bytes:
    """Set a throwaway AUTOFOLIO_VAULT_KEY (the test KEK) and return its bytes."""
    kek = Fernet.generate_key()
    monkeypatch.setenv("AUTOFOLIO_VAULT_KEY", kek.decode("ascii"))
    return kek


@pytest.fixture
def store(tmp_path, monkeypatch):
    """An EnvelopeSecretStore over a temp SQLite DB with a test KEK."""
    _fresh_kek(monkeypatch)
    # Reload vault so its key sourcing reflects the test env, then import store.
    from app.ui import vault as vault_mod
    importlib.reload(vault_mod)
    import app.services.envelope as env_mod
    importlib.reload(env_mod)
    import app.services.secret_store as ss_mod
    importlib.reload(ss_mod)

    from app.database.sqlite_db import initialize_database

    db = tmp_path / "secrets.db"
    initialize_database(db)
    return ss_mod.EnvelopeSecretStore(db_path=db), db, ss_mod


# ── set -> metadata -> reveal round-trip ─────────────────────────────────────

def test_write_returns_metadata_only(store):
    st, _db, _ = store
    meta = st.write("alice@example.com", "openai", "sk-secret-value-1234")
    assert meta["provider_id"] == "openai"
    assert meta["configured"] is True
    assert meta["enabled"] is True
    assert meta["masked_hint"] == "****1234"
    assert "audit_id" in meta
    # NEVER returns plaintext.
    assert "secret_value" not in meta
    assert "token" not in meta
    assert "sk-secret-value-1234" not in json.dumps(meta)


def test_reveal_round_trip(store):
    st, _db, _ = store
    st.write("alice@example.com", "openai", "sk-reveal-me-9999")
    assert st.reveal("alice@example.com", "openai") == "sk-reveal-me-9999"


def test_reveal_none_when_absent(store):
    st, _db, _ = store
    assert st.reveal("nobody@example.com", "openai") is None


def test_read_metadata_no_secret(store):
    st, _db, _ = store
    st.write("alice@example.com", "anthropic", "sk-anthro-secret-xyz", account_label="acct", scopes=["a", "b"])
    meta = st.read_metadata("alice@example.com", "anthropic")
    assert meta["configured"] is True
    assert meta["account_label"] == "acct"
    assert meta["scopes"] == ["a", "b"]
    assert "sk-anthro-secret-xyz" not in json.dumps(meta)


def test_rotate_changes_secret_and_hint(store):
    st, _db, _ = store
    st.write("alice@example.com", "openai", "sk-old-token-abcd")
    meta = st.rotate("alice@example.com", "openai", "sk-new-token-efgh")
    assert meta["masked_hint"] == "****efgh"
    assert st.reveal("alice@example.com", "openai") == "sk-new-token-efgh"
    assert "sk-old-token-abcd" not in json.dumps(meta)
    assert "sk-new-token-efgh" not in json.dumps(meta)


def test_disable_keeps_secret_but_flags_off(store):
    st, _db, _ = store
    st.write("alice@example.com", "openai", "sk-disable-test-1234", enabled=True)
    meta = st.disable("alice@example.com", "openai")
    assert meta["enabled"] is False
    assert meta["configured"] is True
    # Secret is preserved (disable != delete).
    assert st.reveal("alice@example.com", "openai") == "sk-disable-test-1234"


def test_delete_removes_secret(store):
    st, _db, _ = store
    st.write("alice@example.com", "openai", "sk-delete-me-1234")
    meta = st.delete("alice@example.com", "openai")
    assert meta["configured"] is False
    assert st.reveal("alice@example.com", "openai") is None
    assert "sk-delete-me-1234" not in json.dumps(meta)


def test_write_token_none_preserves_secret(store):
    st, _db, _ = store
    st.write("alice@example.com", "openai", "sk-keep-me-1234", account_label="first")
    # Re-write with token=None should preserve the secret but update metadata.
    st.write("alice@example.com", "openai", None, account_label="updated")
    assert st.reveal("alice@example.com", "openai") == "sk-keep-me-1234"
    assert st.read_metadata("alice@example.com", "openai")["account_label"] == "updated"


# ── Cross-user isolation ─────────────────────────────────────────────────────

def test_cross_user_reveal_isolation(store):
    st, _db, _ = store
    st.write("alice@example.com", "openai", "alice-secret-token-1111")
    st.write("bob@example.com", "openai", "bob-secret-token-2222")
    assert st.reveal("alice@example.com", "openai") == "alice-secret-token-1111"
    assert st.reveal("bob@example.com", "openai") == "bob-secret-token-2222"


def test_cross_user_ciphertext_not_readable_with_other_dek(store, monkeypatch):
    """User A's stored ciphertext cannot be decrypted with user B's unwrapped DEK,
    even though the same KEK wraps both DEKs."""
    st, db, _ = store
    import app.services.envelope as env_mod
    from app.ui import vault as vault_mod

    st.write("alice@example.com", "openai", "alice-only-secret-aaaa")
    st.write("bob@example.com", "openai", "bob-only-secret-bbbb")

    rows = _dump_rows(db)
    by_user = {r["user_id"]: r for r in rows}
    kek = vault_mod.key_bytes()
    dek_a = env_mod.unwrap_dek(by_user["alice@example.com"]["wrapped_dek"], kek)
    dek_b = env_mod.unwrap_dek(by_user["bob@example.com"]["wrapped_dek"], kek)
    assert dek_a != dek_b

    # B's DEK cannot read A's ciphertext, and vice-versa.
    with pytest.raises(InvalidToken):
        env_mod.decrypt(by_user["alice@example.com"]["ciphertext"], dek_b)
    with pytest.raises(InvalidToken):
        env_mod.decrypt(by_user["bob@example.com"]["ciphertext"], dek_a)


def test_tenant_scope_other_user_sees_nothing(store):
    st, _db, _ = store
    st.write("alice@example.com", "openai", "alice-token-secret-1234")
    bob_meta = st.read_metadata("bob@example.com", "openai")
    assert bob_meta["configured"] is False
    assert "alice" not in json.dumps(bob_meta)


# ── No-plaintext leak (the stored row) ───────────────────────────────────────

def test_stored_row_contains_no_plaintext_secret(store):
    st, db, _ = store
    secret = "sk-DO-NOT-PERSIST-IN-CLEAR-7777"
    st.write("alice@example.com", "openai", secret, account_label="lbl", scopes=["s1"], note="n")
    rows = _dump_rows(db)
    assert len(rows) == 1
    row = rows[0]
    # Secret-bearing columns hold ENCRYPTED material only.
    assert row["wrapped_dek"] and row["wrapped_dek"] != secret
    assert row["ciphertext"] and row["ciphertext"] != secret
    # The raw secret string must be absent from EVERY column value.
    for col, val in row.items():
        assert secret not in str(val), f"plaintext secret leaked into column {col!r}"


def test_db_compromise_without_kek_yields_nothing(store, monkeypatch):
    """A DB dump + wrong KEK cannot recover the secret."""
    st, db, _ = store
    import app.services.envelope as env_mod

    st.write("alice@example.com", "openai", "sk-needs-the-real-kek-5555")
    row = _dump_rows(db)[0]

    wrong_kek = Fernet.generate_key()
    with pytest.raises(InvalidToken):
        env_mod.unwrap_dek(row["wrapped_dek"], wrong_kek)


# ── Backend selection (byte-identical guardrail) ─────────────────────────────

def test_factory_returns_vault_store_when_no_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")
    import app.config.settings as settings_mod
    importlib.reload(settings_mod)
    import app.services.secret_store as ss_mod
    importlib.reload(ss_mod)
    store_obj = ss_mod.get_secret_store()
    assert type(store_obj).__name__ == "VaultSecretStore"


def test_factory_returns_envelope_store_for_postgres_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pw@host:5432/db")
    import app.config.settings as settings_mod
    importlib.reload(settings_mod)
    import app.services.secret_store as ss_mod
    importlib.reload(ss_mod)
    store_obj = ss_mod.get_secret_store()
    assert type(store_obj).__name__ == "EnvelopeSecretStore"
    # Restore SQLite selection for the rest of the session.
    monkeypatch.setenv("DATABASE_URL", "")
    importlib.reload(settings_mod)
    importlib.reload(ss_mod)


# ── 0006 migration parses as Postgres ────────────────────────────────────────

def test_migration_0006_parses_as_postgres():
    import sqlglot

    path = Path(__file__).resolve().parents[1] / "supabase" / "migrations" / "0006_integration_secret_blobs.sql"
    sql = path.read_text(encoding="utf-8")
    statements = sqlglot.parse(sql, read="postgres")
    # CREATE TABLE + CREATE INDEX + ALTER ... ENABLE RLS (comments are not statements).
    assert sum(1 for s in statements if s is not None) >= 3
    assert "integration_secret_blobs" in sql
    # The migration file must never contain a plaintext secret/key.
    assert "AUTOFOLIO_VAULT_KEY" not in sql or "lives ONLY" in sql  # only mentioned in the explanatory comment


# ── helpers ──────────────────────────────────────────────────────────────────

def _dump_rows(db) -> list[dict]:
    import sqlite3

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT * FROM integration_secret_blobs").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
