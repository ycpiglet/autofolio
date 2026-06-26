"""TASK-087 A6: Runtime config / env-flag loader tests.

TDD RED phase: written before implementation.
"""
from __future__ import annotations

import importlib


def _mod(monkeypatch):
    import app.services.runtime_config as rc_mod
    importlib.reload(rc_mod)
    return rc_mod


# ── Fail-closed (missing → present=False) ────────────────────────────────────

def test_missing_var_returns_false(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    rc = _mod(monkeypatch)
    result = rc.check_presence("SUPABASE_URL")
    assert result == {"name": "SUPABASE_URL", "present": False}


def test_missing_var_no_value_key(monkeypatch):
    monkeypatch.delenv("SUPABASE_SECRET_KEY", raising=False)
    rc = _mod(monkeypatch)
    result = rc.check_presence("SUPABASE_SECRET_KEY")
    assert "value" not in result


def test_missing_service_role_key_fail_closed(monkeypatch):
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    rc = _mod(monkeypatch)
    result = rc.check_presence("SUPABASE_SERVICE_ROLE_KEY")
    assert result["present"] is False


# ── Presence-only (present → present=True, value never returned) ──────────────

def test_present_var_returns_true(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://secret-project.supabase.co")
    rc = _mod(monkeypatch)
    result = rc.check_presence("SUPABASE_URL")
    assert result["present"] is True


def test_present_var_has_no_value_key(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://secret-project.supabase.co")
    rc = _mod(monkeypatch)
    result = rc.check_presence("SUPABASE_URL")
    assert "value" not in result


def test_present_var_value_not_in_result_string(monkeypatch):
    secret_url = "https://super-secret-supabase-url.co"
    monkeypatch.setenv("SUPABASE_URL", secret_url)
    rc = _mod(monkeypatch)
    result = rc.check_presence("SUPABASE_URL")
    assert secret_url not in str(result)


def test_kis_env_present(monkeypatch):
    monkeypatch.setenv("KIS_ENV", "paper")
    rc = _mod(monkeypatch)
    result = rc.check_presence("KIS_ENV")
    assert result["present"] is True
    assert "paper" not in str(result)


# ── check_all: all vars, no value leak ────────────────────────────────────────

def test_check_all_returns_list(monkeypatch):
    rc = _mod(monkeypatch)
    results = rc.check_all()
    assert isinstance(results, list)
    assert len(results) > 0


def test_check_all_no_value_key_in_any_entry(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://secret-url.supabase.co")
    monkeypatch.setenv("KIS_ENV", "mock")
    rc = _mod(monkeypatch)
    results = rc.check_all()
    for entry in results:
        assert "value" not in entry


def test_check_all_no_secret_value_in_any_entry(monkeypatch):
    secret = "super-secret-value-xyz-12345"
    monkeypatch.setenv("SUPABASE_URL", secret)
    rc = _mod(monkeypatch)
    results = rc.check_all()
    combined = str(results)
    assert secret not in combined


def test_check_all_entries_have_name_and_present(monkeypatch):
    rc = _mod(monkeypatch)
    results = rc.check_all()
    for entry in results:
        assert "name" in entry
        assert "present" in entry
        assert isinstance(entry["present"], bool)


def test_supabase_url_in_tracked_vars(monkeypatch):
    rc = _mod(monkeypatch)
    names = [e["name"] for e in rc.check_all()]
    assert "SUPABASE_URL" in names


def test_service_role_key_in_tracked_vars(monkeypatch):
    rc = _mod(monkeypatch)
    names = [e["name"] for e in rc.check_all()]
    assert "SUPABASE_SERVICE_ROLE_KEY" in names


def test_kis_env_in_tracked_vars(monkeypatch):
    rc = _mod(monkeypatch)
    names = [e["name"] for e in rc.check_all()]
    assert "KIS_ENV" in names


# ── Internal get_config_flag (server-side only, not for API responses) ─────────

def test_get_config_flag_returns_actual_value(monkeypatch):
    monkeypatch.setenv("KIS_ENV", "mock")
    rc = _mod(monkeypatch)
    val = rc.get_config_flag("KIS_ENV")
    assert val == "mock"


def test_get_config_flag_missing_returns_default(monkeypatch):
    monkeypatch.delenv("MISSING_VAR_XYZ", raising=False)
    rc = _mod(monkeypatch)
    assert rc.get_config_flag("MISSING_VAR_XYZ") is None
    assert rc.get_config_flag("MISSING_VAR_XYZ", "fallback") == "fallback"
