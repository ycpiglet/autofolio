"""TASK-087 A5: Secret-store adapter tests.

TDD RED phase: written before implementation.
"""
from __future__ import annotations

import importlib
import logging


def _get_store(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFOLIO_HOME", str(tmp_path))
    from app.ui import vault as vault_mod
    importlib.reload(vault_mod)
    import app.services.secret_store as ss_mod
    importlib.reload(ss_mod)
    return ss_mod.VaultSecretStore()


# ── Metadata-only responses ────────────────────────────────────────────────────

def test_write_returns_metadata_only(tmp_path, monkeypatch):
    store = _get_store(tmp_path, monkeypatch)
    meta = store.write("alice@example.com", "openai", "sk-secret-value-1234")
    assert "provider_id" in meta
    assert "enabled" in meta
    assert "masked_hint" in meta
    assert "audit_id" in meta
    # NEVER returns plaintext secret
    assert "secret_value" not in meta
    assert "token" not in meta
    assert "sk-secret-value-1234" not in str(meta)


def test_rotate_returns_metadata_only(tmp_path, monkeypatch):
    store = _get_store(tmp_path, monkeypatch)
    store.write("alice@example.com", "openai", "sk-old-token-abcd")
    meta = store.rotate("alice@example.com", "openai", "sk-new-token-efgh")
    assert "provider_id" in meta
    assert "masked_hint" in meta
    assert "sk-old-token-abcd" not in str(meta)
    assert "sk-new-token-efgh" not in str(meta)


def test_delete_returns_metadata_only_with_no_secret(tmp_path, monkeypatch):
    store = _get_store(tmp_path, monkeypatch)
    store.write("alice@example.com", "openai", "sk-token-to-delete")
    meta = store.delete("alice@example.com", "openai")
    assert "provider_id" in meta
    assert meta.get("configured") is False
    assert "sk-token-to-delete" not in str(meta)


def test_disable_returns_metadata_only_enabled_false(tmp_path, monkeypatch):
    store = _get_store(tmp_path, monkeypatch)
    store.write("alice@example.com", "openai", "sk-token-disable-test", enabled=True)
    meta = store.disable("alice@example.com", "openai")
    assert meta["enabled"] is False
    assert "sk-token-disable-test" not in str(meta)


def test_read_metadata_returns_no_secret(tmp_path, monkeypatch):
    store = _get_store(tmp_path, monkeypatch)
    store.write("alice@example.com", "anthropic", "sk-anthro-secret-xyz")
    meta = store.read_metadata("alice@example.com", "anthropic")
    assert "provider_id" in meta
    assert "secret_value" not in meta
    assert "sk-anthro-secret-xyz" not in str(meta)


def test_masked_hint_is_correct(tmp_path, monkeypatch):
    store = _get_store(tmp_path, monkeypatch)
    meta = store.write("alice@example.com", "openai", "sk-test-secret-value")
    assert meta["masked_hint"] == "****alue"


# ── Tenant scoping ─────────────────────────────────────────────────────────────

def test_tenant_scope_alice_cannot_see_bob_data(tmp_path, monkeypatch):
    store = _get_store(tmp_path, monkeypatch)
    store.write("alice@example.com", "openai", "alice-token-secret-1234")

    bob_meta = store.read_metadata("bob@example.com", "openai")
    assert bob_meta["configured"] is False
    assert "alice-token-secret-1234" not in str(bob_meta)
    assert "alice" not in str(bob_meta)


def test_tenant_scope_bob_cannot_delete_alice_record(tmp_path, monkeypatch):
    store = _get_store(tmp_path, monkeypatch)
    store.write("alice@example.com", "openai", "alice-token-for-delete-test")

    # Bob deletes his own (non-existent) openai record — does not affect alice
    store.delete("bob@example.com", "openai")

    alice_meta = store.read_metadata("alice@example.com", "openai")
    assert alice_meta["configured"] is True


def test_tenant_scope_write_isolation(tmp_path, monkeypatch):
    store = _get_store(tmp_path, monkeypatch)
    store.write("alice@example.com", "telegram", "alice-telegram-bot-token")
    store.write("bob@example.com", "telegram", "bob-telegram-bot-token")

    alice_meta = store.read_metadata("alice@example.com", "telegram")
    bob_meta = store.read_metadata("bob@example.com", "telegram")

    assert alice_meta["configured"] is True
    assert bob_meta["configured"] is True
    assert "bob-telegram-bot-token" not in str(alice_meta)
    assert "alice-telegram-bot-token" not in str(bob_meta)


# ── Log redaction ──────────────────────────────────────────────────────────────

def test_logs_do_not_contain_token(tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("AUTOFOLIO_HOME", str(tmp_path))
    from app.ui import vault as vault_mod
    importlib.reload(vault_mod)
    import app.services.secret_store as ss_mod
    importlib.reload(ss_mod)
    store = ss_mod.VaultSecretStore()

    with caplog.at_level(logging.DEBUG, logger="app.services.secret_store"):
        store.write("alice@example.com", "openai", "sk-super-secret-do-not-log")

    assert "sk-super-secret-do-not-log" not in caplog.text


def test_rotate_logs_do_not_contain_tokens(tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("AUTOFOLIO_HOME", str(tmp_path))
    from app.ui import vault as vault_mod
    importlib.reload(vault_mod)
    import app.services.secret_store as ss_mod
    importlib.reload(ss_mod)
    store = ss_mod.VaultSecretStore()
    store.write("alice@example.com", "openai", "sk-old-do-not-log")

    with caplog.at_level(logging.DEBUG, logger="app.services.secret_store"):
        store.rotate("alice@example.com", "openai", "sk-new-do-not-log")

    assert "sk-old-do-not-log" not in caplog.text
    assert "sk-new-do-not-log" not in caplog.text


# ── Supabase stub ──────────────────────────────────────────────────────────────

def test_supabase_store_raises_not_implemented(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFOLIO_HOME", str(tmp_path))
    import app.services.secret_store as ss_mod
    importlib.reload(ss_mod)
    store = ss_mod.SupabaseSecretStore()
    import pytest
    with pytest.raises(NotImplementedError):
        store.write("alice@example.com", "openai", "some-token")
    with pytest.raises(NotImplementedError):
        store.rotate("alice@example.com", "openai", "some-token")
    with pytest.raises(NotImplementedError):
        store.disable("alice@example.com", "openai")
    with pytest.raises(NotImplementedError):
        store.delete("alice@example.com", "openai")
    with pytest.raises(NotImplementedError):
        store.read_metadata("alice@example.com", "openai")
