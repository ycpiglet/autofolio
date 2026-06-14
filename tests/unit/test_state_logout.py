"""Tests for app/ui/state.py logout() security fix.

Verifies that logout() resets ALL session state keys, not just 'authed',
'user', and 'demo'. Pre-fix, keys like kill_switch, auto_enabled, mode,
symbol_modes, data_source, and trade ack keys leak to the next session.

Isolation note: these tests patch ONLY ``app.ui.state.st`` (the module-level
streamlit reference) with a SimpleNamespace whose ``session_state`` is a plain
dict. They do NOT touch ``sys.modules`` or the real streamlit module, so they
cannot pollute later AppTest-based tests (an earlier sys.modules-swapping
approach corrupted streamlit's globals and broke test_top_bar_data_source).
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import app.ui.state as state_mod


def _build_pre_logout_session(session: dict) -> None:
    """Populate session with non-default 'logged-in' values for every key."""
    session["authed"] = True
    session["user"] = {"name": "Alice", "provider": "google"}
    session["demo"] = True
    session["mode"] = "L4"               # non-default (default: "L1")
    session["auto_enabled"] = True       # non-default (default: False)
    session["kill_switch"] = True        # non-default (default: False)
    session["pnl_kr_colors"] = False     # non-default (default: True)
    session["symbol_modes"] = {"005930": "L3"}  # non-default (default: {})
    session["data_source"] = "backend"   # non-default (default: "demo")
    # Extra trade-ack session keys not in DEFAULTS
    session["trade_ack_checked"] = True
    session["_trade_ack_pending_message"] = "sell 100 shares"
    session["_trade_ack_context"] = {"order_id": 42}


def _logout_with(session: dict) -> None:
    """Run the real logout() against a dict-backed fake session_state."""
    fake_st = SimpleNamespace(session_state=session)
    with patch.object(state_mod, "st", fake_st):
        state_mod.logout()


class TestLogout:
    """Security tests for state.logout()."""

    def _run_logout(self):
        """Invoke logout() with a fully-populated non-default session.

        Returns (session_dict, defaults_dict) after logout() has been called.
        """
        session: dict = {}
        _build_pre_logout_session(session)
        _logout_with(session)
        return session, state_mod.DEFAULTS

    # ------------------------------------------------------------------
    # Core DEFAULTS keys must be reset
    # ------------------------------------------------------------------

    def test_logout_resets_authed(self):
        session, defaults = self._run_logout()
        assert session["authed"] == defaults["authed"]

    def test_logout_resets_user(self):
        session, defaults = self._run_logout()
        assert session["user"] == defaults["user"]

    def test_logout_resets_demo(self):
        session, defaults = self._run_logout()
        assert session["demo"] == defaults["demo"]

    def test_logout_resets_mode(self):
        """Bug: pre-fix logout() did NOT reset 'mode'."""
        session, defaults = self._run_logout()
        assert session["mode"] == defaults["mode"], (
            f"mode leaked: got {session['mode']!r}, expected {defaults['mode']!r}"
        )

    def test_logout_resets_auto_enabled(self):
        """Bug: pre-fix logout() did NOT reset 'auto_enabled'."""
        session, defaults = self._run_logout()
        assert session["auto_enabled"] == defaults["auto_enabled"], (
            f"auto_enabled leaked: {session['auto_enabled']!r}"
        )

    def test_logout_resets_kill_switch(self):
        """Bug: pre-fix logout() did NOT reset 'kill_switch'."""
        session, defaults = self._run_logout()
        assert session["kill_switch"] == defaults["kill_switch"], (
            f"kill_switch leaked: {session['kill_switch']!r}"
        )

    def test_logout_resets_pnl_kr_colors(self):
        session, defaults = self._run_logout()
        assert session["pnl_kr_colors"] == defaults["pnl_kr_colors"]

    def test_logout_resets_symbol_modes(self):
        """Bug: pre-fix logout() did NOT reset 'symbol_modes'."""
        session, defaults = self._run_logout()
        assert session["symbol_modes"] == defaults["symbol_modes"], (
            f"symbol_modes leaked: {session['symbol_modes']!r}"
        )

    def test_logout_resets_data_source(self):
        """Bug: pre-fix logout() did NOT reset 'data_source'."""
        session, defaults = self._run_logout()
        assert session["data_source"] == defaults["data_source"], (
            f"data_source leaked: {session['data_source']!r}"
        )

    # ------------------------------------------------------------------
    # symbol_modes must be a new copy, not the shared DEFAULTS dict
    # ------------------------------------------------------------------

    def test_logout_symbol_modes_is_independent_copy(self):
        """logout() must store a copy of symbol_modes, not the shared DEFAULTS dict.

        Asserted via object identity + targeted-key propagation so the test is
        robust to other suites mutating the shared DEFAULTS global (init_state
        aliases DEFAULTS mutables via setdefault — a separate latent issue).
        """
        session: dict = {}
        _build_pre_logout_session(session)
        _logout_with(session)

        # logout used copy.copy → the post-logout value must be a DISTINCT object
        assert session["symbol_modes"] is not state_mod.DEFAULTS["symbol_modes"]

        # Mutating the post-logout session value must not propagate to DEFAULTS
        session["symbol_modes"]["TEST"] = "L2"
        assert "TEST" not in state_mod.DEFAULTS["symbol_modes"]

    # ------------------------------------------------------------------
    # Extra trade-ack keys must be removed
    # ------------------------------------------------------------------

    def test_logout_removes_trade_ack_checked(self):
        session, _ = self._run_logout()
        assert "trade_ack_checked" not in session

    def test_logout_removes_trade_ack_pending_message(self):
        session, _ = self._run_logout()
        assert "_trade_ack_pending_message" not in session

    def test_logout_removes_trade_ack_context(self):
        session, _ = self._run_logout()
        assert "_trade_ack_context" not in session

    def test_logout_no_error_when_extra_keys_absent(self):
        """logout() must not raise even if trade-ack keys were never set."""
        session = {
            "authed": True,
            "user": {"name": "Bob", "provider": "demo"},
            "demo": False,
            "mode": "L2",
            "auto_enabled": False,
            "kill_switch": False,
            "pnl_kr_colors": True,
            "symbol_modes": {},
            "data_source": "demo",
        }
        # Must not raise
        _logout_with(session)

        assert session["authed"] is False
