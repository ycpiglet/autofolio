"""Tests for alert settings persistence (TASK-054).

TDD: This file was written BEFORE get_alert_settings/save_alert_settings existed.
Initial run confirms FAIL — then connections.py and alerts.py are updated.
"""
from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest


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


# ---------------------------------------------------------------------------
# AppTest integration tests
# ---------------------------------------------------------------------------

def test_alerts_view_loads_persisted_channels(tmp_path):
    """Alert view initializes channel toggles from persisted vault data."""
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "alerts_persist_app.py"
    script.write_text(
        f"""
import streamlit as st
from unittest.mock import patch

SAVED = {{"channels": {{"Telegram": False, "Kakao": True, "Discord": True, "Notion": False, "Email": False}}, "rules": ["뉴스/공시", "일일요약"]}}

from app.ui.views import alerts as alerts_mod

with patch.object(alerts_mod, "get_alert_settings", return_value=SAVED):
    with patch.object(alerts_mod, "save_alert_settings"):
        alerts_mod.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)
    assert not at.exception

    # Telegram should be OFF (persisted False)
    tg = next(t for t in at.toggle if t.label == "Telegram")
    assert tg.value is False

    # Kakao should be ON (persisted True)
    kakao = next(t for t in at.toggle if t.label == "Kakao")
    assert kakao.value is True


def test_alerts_view_saves_on_toggle_change(tmp_path):
    """Changing a channel toggle triggers save_alert_settings (no exception)."""
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "alerts_save_app.py"
    script.write_text(
        f"""
import streamlit as st
from unittest.mock import patch, MagicMock

SAVED = {{"channels": {{"Telegram": True, "Kakao": False, "Discord": False, "Notion": True, "Email": True}}, "rules": ["체결", "가격도달", "리스크한도", "서킷브레이커"]}}

from app.ui.views import alerts as alerts_mod

with patch.object(alerts_mod, "get_alert_settings", return_value=SAVED):
    with patch.object(alerts_mod, "save_alert_settings", MagicMock()):
        alerts_mod.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)
    assert not at.exception

    # Toggle Telegram (currently True → False) — on_change fires, save is called
    tg = next(t for t in at.toggle if t.label == "Telegram")
    at2 = tg.set_value(False).run(timeout=15)
    assert not at2.exception

    # Confirm the callback completed: value reflects the new state
    tg2 = next(t for t in at2.toggle if t.label == "Telegram")
    assert tg2.value is False


def test_alerts_view_saves_on_rules_change(tmp_path):
    """Changing the rules multiselect triggers save_alert_settings (no exception)."""
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "alerts_rules_app.py"
    script.write_text(
        f"""
import streamlit as st
from unittest.mock import patch, MagicMock

SAVED = {{"channels": {{"Telegram": True, "Kakao": False, "Discord": False, "Notion": True, "Email": True}}, "rules": ["체결", "가격도달", "리스크한도", "서킷브레이커"]}}

from app.ui.views import alerts as alerts_mod

with patch.object(alerts_mod, "get_alert_settings", return_value=SAVED):
    with patch.object(alerts_mod, "save_alert_settings", MagicMock()):
        alerts_mod.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)
    assert not at.exception

    # Change rules multiselect (key updated from _alert_rules_widget → alert_rules_widget)
    ms = next(m for m in at.multiselect if m.key == "alert_rules_widget")
    at2 = ms.set_value(["체결", "뉴스/공시"]).run(timeout=15)
    assert not at2.exception

    # Confirm the new value is reflected after callback completed
    ms2 = next(m for m in at2.multiselect if m.key == "alert_rules_widget")
    assert "체결" in ms2.value
    assert "뉴스/공시" in ms2.value
