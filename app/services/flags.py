"""Central feature-flag module — TASK-087 A1.

All flags are backed by environment variables and default to OFF (fail-closed).

Rules:
- Pure functions: only read env vars via os.getenv, no I/O, no caching.
- Never log the env value itself.
- New flags (multi_tenant, auto_exec, recommendation, advice) are defined here
  but not read by any other module yet. A1 is a definition-only step.

Truthy parser matches the EXACT semantics used by the pre-existing inline
parsers in app/api/routers/auth.py and app/services/auth_service.py:

    (os.getenv(VAR) or "").strip().lower() in {"1", "true", "yes", "on"}
"""
from __future__ import annotations

import os

_TRUTHY: frozenset[str] = frozenset({"1", "true", "yes", "on"})


def _is_truthy(var: str) -> bool:
    """Return True iff the env var resolves to a recognised truthy string.

    Semantics are byte-identical to the inline parsers that existed before
    this module was introduced (auth.py::guest_demo_enabled and
    auth_service.py::_auto_register_enabled).
    """
    return (os.getenv(var) or "").strip().lower() in _TRUTHY


# ---------------------------------------------------------------------------
# Flags gating pre-existing guest/local-dev features
# (semantics preserved from the original inline parsers)
# ---------------------------------------------------------------------------

def guest_demo_enabled() -> bool:
    """True iff AUTOFOLIO_GUEST_DEMO_ENABLED is set to a truthy value.

    Replaces the local ``guest_demo_enabled()`` helper in
    ``app/api/routers/auth.py``.  Semantics are preserved verbatim.
    """
    return _is_truthy("AUTOFOLIO_GUEST_DEMO_ENABLED")


def local_auto_register_enabled() -> bool:
    """True iff AUTOFOLIO_LOCAL_AUTO_REGISTER is set to a truthy value.

    Replaces the local ``_auto_register_enabled()`` helper in
    ``app/services/auth_service.py``.  Semantics are preserved verbatim.
    """
    return _is_truthy("AUTOFOLIO_LOCAL_AUTO_REGISTER")


# ---------------------------------------------------------------------------
# New production-gate flags — defined here; NOT consumed by any other module
# in A1.  All default OFF.
# ---------------------------------------------------------------------------

def multi_tenant_enabled() -> bool:
    """True iff AUTOFOLIO_MULTI_TENANT_ENABLED is set to a truthy value."""
    return _is_truthy("AUTOFOLIO_MULTI_TENANT_ENABLED")


def auto_exec_enabled() -> bool:
    """True iff AUTOFOLIO_AUTO_EXEC_ENABLED is set to a truthy value."""
    return _is_truthy("AUTOFOLIO_AUTO_EXEC_ENABLED")


def recommendation_enabled() -> bool:
    """True iff AUTOFOLIO_RECOMMENDATION_ENABLED is set to a truthy value."""
    return _is_truthy("AUTOFOLIO_RECOMMENDATION_ENABLED")


def advice_enabled() -> bool:
    """True iff AUTOFOLIO_ADVICE_ENABLED is set to a truthy value."""
    return _is_truthy("AUTOFOLIO_ADVICE_ENABLED")
