"""Tests for alert settings persistence (TASK-054).

TDD: This file was written BEFORE get_alert_settings/save_alert_settings existed.
Initial run confirms FAIL — then connections.py and alerts.py are updated.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Unit tests (pure function tests, no AppTest)
# ---------------------------------------------------------------------------

def test_get_alert_settings_returns_defaults_when_empty(tmp_path, monkeypatch):
    """get_alert_settings() returns defaults when vault has no alert_settings key."""
    monkeypatch.setenv("AUTOFOLIO_HOME", str(tmp_path / ".autofolio"))
    from importlib import reload
    import app.ui.vault as vault_mod
    reload(vault_mod)
    from app.services import connections as conn_mod
    reload(conn_mod)

    result = conn_mod.get_alert_settings()
    assert result["channels"] == dict(conn_mod._DEFAULT_ALERT_CHANNELS)
    assert result["rules"] == list(conn_mod._DEFAULT_ALERT_RULES)


def test_save_and_load_alert_settings(tmp_path, monkeypatch):
    """save_alert_settings round-trips: saved values can be loaded back."""
    monkeypatch.setenv("AUTOFOLIO_HOME", str(tmp_path / ".autofolio"))
    from importlib import reload
    import app.ui.vault as vault_mod
    reload(vault_mod)
    from app.services import connections as conn_mod
    reload(conn_mod)

    channels = {"Telegram": True, "Kakao": True, "Discord": False, "Notion": False, "Email": True}
    rules = ["체결", "뉴스/공시"]
    conn_mod.save_alert_settings(channels, rules)

    loaded = conn_mod.get_alert_settings()
    assert loaded["channels"] == channels
    assert loaded["rules"] == rules


def test_save_does_not_overwrite_connections(tmp_path, monkeypatch):
    """save_alert_settings preserves existing vault data (brokers/channels)."""
    monkeypatch.setenv("AUTOFOLIO_HOME", str(tmp_path / ".autofolio"))
    from importlib import reload
    import app.ui.vault as vault_mod
    reload(vault_mod)
    from app.services import connections as conn_mod
    reload(conn_mod)

    # Put some data in vault first
    conn_mod.connect_channel("Telegram", "tok123")

    # Now save alert settings
    conn_mod.save_alert_settings(
        {"Telegram": True, "Kakao": False, "Discord": False, "Notion": True, "Email": True},
        ["체결"],
    )

    # Connections data should still be intact
    conn = conn_mod.get()
    tg = next(c for c in conn["channels"] if c["채널"] == "Telegram")
    assert tg["status"] == "연결"
    assert tg["detail"] == "tok123"


def test_alert_settings_in_all(tmp_path, monkeypatch):
    """get_alert_settings and save_alert_settings must be exported in __all__."""
    monkeypatch.setenv("AUTOFOLIO_HOME", str(tmp_path / ".autofolio"))
    from importlib import reload
    import app.ui.vault as vault_mod
    reload(vault_mod)
    from app.services import connections as conn_mod
    reload(conn_mod)

    assert "get_alert_settings" in conn_mod.__all__
    assert "save_alert_settings" in conn_mod.__all__
