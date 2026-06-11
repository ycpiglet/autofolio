"""Tests for shared UI component contracts."""
from __future__ import annotations

from app.ui.components import ui
from app.ui import theme


def test_status_tone_maps_known_states():
    assert ui.status_tone("연결") == "success"
    assert ui.status_tone("주의") == "warning"
    assert ui.status_tone("위험") == "danger"
    assert ui.status_tone("OFF") == "neutral"


def test_status_tone_maps_control_desk_guard_states():
    assert ui.status_tone("ACTIVE") == "danger"
    assert ui.status_tone("TRIGGERED") == "danger"
    assert ui.status_tone("CLEAR") == "success"


def test_status_badge_contains_text_not_color_only():
    rendered = ui.status_badge("위험")
    assert "위험" in rendered
    assert "[BLOCK]" in rendered or "BLOCK" in rendered


def test_safety_summary_preserves_explicit_environment():
    summary = ui.build_safety_summary(
        env="paper",
        mode="L1",
        auto=False,
        kill=True,
        circuit_breaker=False,
    )
    assert summary["env"] == theme.env_label("paper")
    assert summary["mode"] == "L1"
    assert summary["auto"] == "OFF"
    assert summary["kill"] == "ACTIVE"


def test_safety_summary_maps_session_datasource_aliases():
    demo_summary = ui.build_safety_summary(
        env="demo",
        mode="L2",
        auto=True,
        kill=False,
        circuit_breaker=True,
    )
    backend_summary = ui.build_safety_summary(
        env="backend",
        mode="L2",
        auto=True,
        kill=False,
        circuit_breaker=True,
    )
    assert demo_summary["env"] == theme.env_label("mock")
    assert backend_summary["env"] == theme.env_label("paper")
    assert demo_summary["circuit_breaker"] == "TRIGGERED"
    assert backend_summary["circuit_breaker"] == "TRIGGERED"


def test_console_row_requires_timestamp_source_and_message():
    row = ui.console_row("12:01", "guard", "BLOCK unknown source")
    assert "12:01" in row
    assert "guard" in row
    assert "BLOCK unknown source" in row
