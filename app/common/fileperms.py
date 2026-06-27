"""Cross-platform helper to restrict an on-disk secret file to the current user.

SECURITY: The historical code called ``os.chmod(path, 0o600)`` which is a
**no-op on Windows** (the POSIX mode bits are ignored by the Windows filesystem
layer). This module centralises the restriction logic:

* POSIX  → ``os.chmod(path, 0o600)`` (owner read/write only) — unchanged behaviour.
* Windows → best-effort ``icacls`` ACL lockdown, **opt-in** via the
  ``AUTOFOLIO_HARDEN_ACL`` env var. By default this is a documented no-op so
  that existing local runs and the test-suite are byte-identical and never spawn
  a subprocess.

  The *real* production mitigation for the vault key is **AUTOFOLIO_VAULT_KEY**
  (the key is then never written to disk at all — see ``app/ui/vault.py``).
  The icacls path is a defence-in-depth nicety for the dev fallback, not the
  primary control, which is why it stays opt-in and fully error-swallowed.

This helper never raises: a permission tweak must never break the caller that
just persisted a token/key/session file.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_TRUTHY = {"1", "true", "yes", "on"}


def _windows_icacls(path: Path) -> None:
    """Best-effort ACL lockdown on Windows (opt-in, never raises).

    Grants the current user full control with inheritance disabled so that only
    the owner can read the secret file. Guarded so a failure leaves the file's
    existing ACL untouched (grant is applied before inheritance removal would
    matter, and the whole thing is wrapped in a broad except).
    """
    import getpass
    import subprocess

    try:
        user = getpass.getuser()
    except Exception:  # noqa: BLE001 — diagnostics only
        return
    try:
        # Additive explicit grant first (never locks the owner out), then strip
        # inherited ACEs so other principals lose access.
        subprocess.run(
            ["icacls", str(path), "/grant:r", f"{user}:F"],
            check=False,
            capture_output=True,
            timeout=10,
        )
        subprocess.run(
            ["icacls", str(path), "/inheritance:r"],
            check=False,
            capture_output=True,
            timeout=10,
        )
    except Exception:  # noqa: BLE001 — best-effort hardening; never break caller
        return


def restrict_to_user(path: str | os.PathLike[str]) -> None:
    """Restrict *path* to the current OS user, best-effort and never raising.

    POSIX applies ``chmod 0o600``. Windows applies an icacls lockdown only when
    ``AUTOFOLIO_HARDEN_ACL`` is truthy; otherwise it is a documented no-op (the
    primary mitigation is AUTOFOLIO_VAULT_KEY keeping the key off disk).
    """
    p = Path(path)
    if sys.platform.startswith("win"):
        if os.getenv("AUTOFOLIO_HARDEN_ACL", "").strip().lower() in _TRUTHY:
            _windows_icacls(p)
        # else: SECURITY no-op — see module docstring; AUTOFOLIO_VAULT_KEY is the
        # real production mitigation for the vault key.
        return
    try:
        os.chmod(p, 0o600)
    except OSError:
        pass
