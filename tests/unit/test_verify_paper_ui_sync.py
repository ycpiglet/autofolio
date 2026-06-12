from __future__ import annotations

from scripts.verify_paper_ui_sync import DEFAULT_TIMEOUT_SEC, build_view_script


def test_build_view_script_forces_paper_backend():
    script = build_view_script("home.render()")

    assert "KIS_ENV" in script
    assert "'paper'" in script
    assert "data_source'] = 'backend'" in script
    assert "home.render()" in script


def test_default_timeout_allows_larger_live_holdings():
    assert DEFAULT_TIMEOUT_SEC >= 300
