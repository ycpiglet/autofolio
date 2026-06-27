"""Unit tests for app.services.flags — TASK-087 A1.

TDD order: write RED tests first, then implement GREEN.

Covers:
- Every flag defaults False when the env var is unset.
- Truthy env values ("1", "true", "yes", "on", mixed-case, with whitespace)
  flip the flag on.
- Falsy env values ("0", "false", "no", "off", "") keep the flag off.
- guest_demo_enabled() and local_auto_register_enabled() match the EXACT
  pre-existing semantics from auth.py and auth_service.py:
      (os.getenv(VAR) or "").strip().lower() in {"1", "true", "yes", "on"}
- Characterization: the flags module parser is byte-identical to the old
  inline parsers for the two env vars they replace.
"""
from __future__ import annotations

import importlib
import os

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reload_flags():
    """Re-import flags so env patches take effect (module has no caching)."""
    import app.services.flags as flags_mod
    importlib.reload(flags_mod)
    return flags_mod


# ---------------------------------------------------------------------------
# 1. All flags default OFF when the env var is absent
# ---------------------------------------------------------------------------

class TestDefaultOff:
    VARS = [
        "AUTOFOLIO_MULTI_TENANT_ENABLED",
        "AUTOFOLIO_AUTO_EXEC_ENABLED",
        "AUTOFOLIO_RECOMMENDATION_ENABLED",
        "AUTOFOLIO_ADVICE_ENABLED",
        "AUTOFOLIO_GUEST_DEMO_ENABLED",
        "AUTOFOLIO_LOCAL_AUTO_REGISTER",
    ]

    @pytest.mark.parametrize("var", VARS)
    def test_flag_defaults_false_when_unset(self, monkeypatch, var):
        monkeypatch.delenv(var, raising=False)
        from app.services import flags
        importlib.reload(flags)
        fn_map = {
            "AUTOFOLIO_MULTI_TENANT_ENABLED": flags.multi_tenant_enabled,
            "AUTOFOLIO_AUTO_EXEC_ENABLED": flags.auto_exec_enabled,
            "AUTOFOLIO_RECOMMENDATION_ENABLED": flags.recommendation_enabled,
            "AUTOFOLIO_ADVICE_ENABLED": flags.advice_enabled,
            "AUTOFOLIO_GUEST_DEMO_ENABLED": flags.guest_demo_enabled,
            "AUTOFOLIO_LOCAL_AUTO_REGISTER": flags.local_auto_register_enabled,
        }
        assert fn_map[var]() is False


# ---------------------------------------------------------------------------
# 2. Truthy values enable the flag
# ---------------------------------------------------------------------------

TRUTHY_VALUES = ["1", "true", "True", "TRUE", "yes", "Yes", "YES", "on", "On", "ON",
                 " 1 ", " true ", "  on  "]
FALSY_VALUES = ["0", "false", "no", "off", "", "2", "enabled", "yes1"]


class TestTruthyValues:
    @pytest.mark.parametrize("val", TRUTHY_VALUES)
    def test_multi_tenant_enabled_truthy(self, monkeypatch, val):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", val)
        from app.services import flags
        importlib.reload(flags)
        assert flags.multi_tenant_enabled() is True

    @pytest.mark.parametrize("val", TRUTHY_VALUES)
    def test_auto_exec_enabled_truthy(self, monkeypatch, val):
        monkeypatch.setenv("AUTOFOLIO_AUTO_EXEC_ENABLED", val)
        from app.services import flags
        importlib.reload(flags)
        assert flags.auto_exec_enabled() is True

    @pytest.mark.parametrize("val", TRUTHY_VALUES)
    def test_recommendation_enabled_truthy(self, monkeypatch, val):
        monkeypatch.setenv("AUTOFOLIO_RECOMMENDATION_ENABLED", val)
        from app.services import flags
        importlib.reload(flags)
        assert flags.recommendation_enabled() is True

    @pytest.mark.parametrize("val", TRUTHY_VALUES)
    def test_advice_enabled_truthy(self, monkeypatch, val):
        monkeypatch.setenv("AUTOFOLIO_ADVICE_ENABLED", val)
        from app.services import flags
        importlib.reload(flags)
        assert flags.advice_enabled() is True

    @pytest.mark.parametrize("val", TRUTHY_VALUES)
    def test_guest_demo_enabled_truthy(self, monkeypatch, val):
        monkeypatch.setenv("AUTOFOLIO_GUEST_DEMO_ENABLED", val)
        from app.services import flags
        importlib.reload(flags)
        assert flags.guest_demo_enabled() is True

    @pytest.mark.parametrize("val", TRUTHY_VALUES)
    def test_local_auto_register_enabled_truthy(self, monkeypatch, val):
        monkeypatch.setenv("AUTOFOLIO_LOCAL_AUTO_REGISTER", val)
        from app.services import flags
        importlib.reload(flags)
        assert flags.local_auto_register_enabled() is True


class TestFalsyValues:
    @pytest.mark.parametrize("val", FALSY_VALUES)
    def test_multi_tenant_disabled_on_falsy(self, monkeypatch, val):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", val)
        from app.services import flags
        importlib.reload(flags)
        assert flags.multi_tenant_enabled() is False

    @pytest.mark.parametrize("val", FALSY_VALUES)
    def test_guest_demo_disabled_on_falsy(self, monkeypatch, val):
        monkeypatch.setenv("AUTOFOLIO_GUEST_DEMO_ENABLED", val)
        from app.services import flags
        importlib.reload(flags)
        assert flags.guest_demo_enabled() is False

    @pytest.mark.parametrize("val", FALSY_VALUES)
    def test_local_auto_register_disabled_on_falsy(self, monkeypatch, val):
        monkeypatch.setenv("AUTOFOLIO_LOCAL_AUTO_REGISTER", val)
        from app.services import flags
        importlib.reload(flags)
        assert flags.local_auto_register_enabled() is False


# ---------------------------------------------------------------------------
# 3. Characterization tests: flags module matches old inline parsers exactly
#
#    Old inline parsers (auth.py and auth_service.py) both use:
#        (os.getenv(VAR) or "").strip().lower() in {"1", "true", "yes", "on"}
#    This test asserts the flags module result equals that reference expression
#    for every test value.
# ---------------------------------------------------------------------------

_PROBE_VALUES = [
    "1", "0", "true", "false", "True", "False", "yes", "no", "on", "off",
    "YES", "NO", "ON", "OFF", " 1 ", " true ", "  on  ", "", "2", "enabled",
    None,
]


def _old_inline_parser(env_value) -> bool:
    """Replicate the EXACT parser used in auth.py and auth_service.py."""
    return (env_value or "").strip().lower() in {"1", "true", "yes", "on"}


class TestCharacterizationGuestDemo:
    @pytest.mark.parametrize("raw", _PROBE_VALUES)
    def test_flags_matches_old_inline_parser_guest_demo(self, monkeypatch, raw):
        """flags.guest_demo_enabled() must be byte-identical to old auth.py logic."""
        if raw is None:
            monkeypatch.delenv("AUTOFOLIO_GUEST_DEMO_ENABLED", raising=False)
            env_value = None
        else:
            monkeypatch.setenv("AUTOFOLIO_GUEST_DEMO_ENABLED", raw)
            env_value = raw

        from app.services import flags
        importlib.reload(flags)

        expected = _old_inline_parser(env_value)
        assert flags.guest_demo_enabled() == expected, (
            f"guest_demo_enabled() mismatch for raw={raw!r}: "
            f"flags={flags.guest_demo_enabled()!r}, old={expected!r}"
        )


class TestCharacterizationLocalAutoRegister:
    @pytest.mark.parametrize("raw", _PROBE_VALUES)
    def test_flags_matches_old_inline_parser_local_auto_register(self, monkeypatch, raw):
        """flags.local_auto_register_enabled() must match old auth_service.py logic."""
        if raw is None:
            monkeypatch.delenv("AUTOFOLIO_LOCAL_AUTO_REGISTER", raising=False)
            env_value = None
        else:
            monkeypatch.setenv("AUTOFOLIO_LOCAL_AUTO_REGISTER", raw)
            env_value = raw

        from app.services import flags
        importlib.reload(flags)

        expected = _old_inline_parser(env_value)
        assert flags.local_auto_register_enabled() == expected, (
            f"local_auto_register_enabled() mismatch for raw={raw!r}: "
            f"flags={flags.local_auto_register_enabled()!r}, old={expected!r}"
        )
