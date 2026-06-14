"""Tests for app/ui/state.py logout() security fix.

Verifies that logout() resets ALL session state keys, not just 'authed',
'user', and 'demo'. Pre-fix, keys like kill_switch, auto_enabled, mode,
symbol_modes, data_source, and trade ack keys leak to the next session.
"""
from __future__ import annotations

import copy
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch


def _load_state_with_mock_st():
    """Import app.ui.state with st.session_state as a real dict."""
    # Build a minimal streamlit stub that uses a plain dict for session_state
    fake_st = MagicMock()
    session: dict = {}

    # Support both attribute-style and item-style access on session_state
    ss = MagicMock()
    ss.__getitem__ = lambda self, k: session[k]
    ss.__setitem__ = lambda self, k, v: session.__setitem__(k, v)
    ss.__contains__ = lambda self, k: k in session
    ss.setdefault = session.setdefault
    ss.pop = session.pop
    # Attribute-style writes (st.session_state.foo = x) go through __setattr__
    # MagicMock records those, so we intercept via __setattr__:
    object.__setattr__(ss, "_session", session)

    fake_st.session_state = ss

    return fake_st, session


def _build_pre_logout_session(session: dict, defaults: dict) -> None:
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


class TestLogout:
    """Security tests for state.logout()."""

    def _run_logout(self):
        """Invoke logout() with a fully-populated non-default session.

        Returns (session_dict, defaults_dict) after logout() has been called.
        """
        fake_st, session = _load_state_with_mock_st()

        with patch.dict(sys.modules, {"streamlit": fake_st}):
            # Force re-import so the module picks up our fake streamlit
            if "app.ui.state" in sys.modules:
                del sys.modules["app.ui.state"]
            import app.ui.state as state_mod  # noqa: PLC0415

            defaults = copy.deepcopy(state_mod.DEFAULTS)
            _build_pre_logout_session(session, defaults)

            state_mod.logout()

        return session, defaults

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
        """Mutating session symbol_modes after logout must not corrupt DEFAULTS."""
        fake_st, session = _load_state_with_mock_st()

        with patch.dict(sys.modules, {"streamlit": fake_st}):
            if "app.ui.state" in sys.modules:
                del sys.modules["app.ui.state"]
            import app.ui.state as state_mod  # noqa: PLC0415

            _build_pre_logout_session(session, state_mod.DEFAULTS)
            state_mod.logout()

            # Mutate the post-logout session value
            session["symbol_modes"]["TEST"] = "L2"

            # DEFAULTS must remain untouched
            assert state_mod.DEFAULTS["symbol_modes"] == {}

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
        fake_st, session = _load_state_with_mock_st()

        with patch.dict(sys.modules, {"streamlit": fake_st}):
            if "app.ui.state" in sys.modules:
                del sys.modules["app.ui.state"]
            import app.ui.state as state_mod  # noqa: PLC0415

            # Only set the DEFAULTS keys (no trade-ack extras)
            session["authed"] = True
            session["user"] = {"name": "Bob", "provider": "demo"}
            session["demo"] = False
            session["mode"] = "L2"
            session["auto_enabled"] = False
            session["kill_switch"] = False
            session["pnl_kr_colors"] = True
            session["symbol_modes"] = {}
            session["data_source"] = "demo"

            # Must not raise
            state_mod.logout()

        assert session["authed"] is False
