"""Runtime config / env-flag reader (TASK-087 A6).

Fail-closed: missing env var → {"name": name, "present": False}
Presence-only: present env var → {"name": name, "present": True}

NEVER returns the actual env var value in any public-facing output.

Tracked vars align with .env.example.  Add names here as new config
vars are introduced; never add values.
"""
from __future__ import annotations

import os

TRACKED_VARS: list[str] = [
    # Supabase platform keys
    "SUPABASE_URL",
    "SUPABASE_PUBLISHABLE_KEY",
    "SUPABASE_SECRET_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    # KIS broker environment
    "KIS_ENV",
    # Membership deposit config
    "AUTOFOLIO_MEMBERSHIP_BANK_NAME",
    "AUTOFOLIO_MEMBERSHIP_ACCOUNT_HOLDER",
    "AUTOFOLIO_MEMBERSHIP_BANK_ACCOUNT",
    "AUTOFOLIO_MEMBERSHIP_PRICE_KRW",
    # Runtime / environment
    "AUTOFOLIO_ENV",
    "AUTOFOLIO_HOME",
    # SSO owner designation (presence-only; value never returned)
    "AUTOFOLIO_OWNER_EMAIL",
    # Production capability locks (TASK-087 A — all default OFF / fail-closed)
    "AUTOFOLIO_AUTO_EXEC_ENABLED",
    "AUTOFOLIO_RECOMMENDATION_ENABLED",
    "AUTOFOLIO_ADVICE_ENABLED",
    "AUTOFOLIO_MULTI_TENANT_ENABLED",
]


def check_presence(name: str) -> dict:
    """Return presence info for one env var. Value is never included.

    Returns {"name": name, "present": bool}.
    """
    return {"name": name, "present": name in os.environ}


def check_all() -> list[dict]:
    """Return presence info for all tracked vars. Values are never included."""
    return [check_presence(name) for name in TRACKED_VARS]


def _get_config_flag(name: str, default=None):
    """INTERNAL USE ONLY — returns the actual env var value for server-side use.

    WARNING: Never expose the return value in any API response, log message,
    or user-facing output. This function exists solely for internal server-side
    configuration reads (e.g., selecting KIS_ENV at startup).
    """
    return os.environ.get(name, default)
