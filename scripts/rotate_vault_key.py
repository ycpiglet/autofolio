#!/usr/bin/env python3
"""Rotate the Autofolio vault Fernet key. [Autofolio 호스트 스크립트]

Decrypts ``.autofolio/vault.enc`` with the OLD key and re-encrypts it with the
NEW key, in place (atomic write via a temp file + replace). This is the
documented rotation procedure that backs the AUTOFOLIO_VAULT_KEY env-key path
(P1.4 secret-handling hardening).

Keys are urlsafe-base64 Fernet keys (``cryptography.fernet.Fernet.generate_key``).
They are read from the environment so no secret ever lands on the command line /
shell history:

  AUTOFOLIO_VAULT_KEY_OLD   the key the vault.enc is currently encrypted with.
                            If unset, falls back to the co-located
                            .autofolio/vault.key file (the dev default).
  AUTOFOLIO_VAULT_KEY_NEW   the key to re-encrypt with (REQUIRED). Generate one:
                              python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

Usage:
  # generate a new key, then:
  AUTOFOLIO_VAULT_KEY_NEW=<newkey> python scripts/rotate_vault_key.py
  # explicit old key (production, key not on disk):
  AUTOFOLIO_VAULT_KEY_OLD=<oldkey> AUTOFOLIO_VAULT_KEY_NEW=<newkey> \
      python scripts/rotate_vault_key.py

After a successful rotation, set AUTOFOLIO_VAULT_KEY=<newkey> for the running
app (and remove the stale .autofolio/vault.key if migrating off the disk
fallback).

Exit codes: 0=rotated (or no-op: vault.enc absent) · 1=error · 2=missing new key.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:  # 윈도우 콘솔(cp949)에서 한글/이모지 출력 안전
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from cryptography.fernet import Fernet  # noqa: E402


def rotate_data(old_key: bytes, new_key: bytes, ciphertext: bytes) -> bytes:
    """Decrypt *ciphertext* with *old_key* and re-encrypt with *new_key*.

    Pure function — used by both the CLI and the unit tests. Raises
    ``cryptography.fernet.InvalidToken`` if *old_key* cannot decrypt the data.
    """
    plaintext = Fernet(old_key).decrypt(ciphertext)
    return Fernet(new_key).encrypt(plaintext)


def rotate_file(data_path: Path, old_key: bytes, new_key: bytes) -> bool:
    """Re-wrap *data_path* in place. Returns False if the file does not exist."""
    if not data_path.exists():
        return False
    rewrapped = rotate_data(old_key, new_key, data_path.read_bytes())
    tmp = data_path.with_suffix(data_path.suffix + ".tmp")
    tmp.write_bytes(rewrapped)
    tmp.replace(data_path)
    return True


def _resolve_old_key(home: Path) -> bytes:
    env_old = os.environ.get("AUTOFOLIO_VAULT_KEY_OLD")
    if env_old:
        return env_old.encode("ascii")
    key_file = home / "vault.key"
    if key_file.exists():
        return key_file.read_bytes()
    raise SystemExit(
        "No old key: set AUTOFOLIO_VAULT_KEY_OLD or keep .autofolio/vault.key."
    )


def main() -> int:
    home = Path(os.getenv("AUTOFOLIO_HOME", ".autofolio"))
    data_path = home / "vault.enc"

    new_key = os.environ.get("AUTOFOLIO_VAULT_KEY_NEW")
    if not new_key:
        print("ERROR: AUTOFOLIO_VAULT_KEY_NEW is required.", file=sys.stderr)
        return 2

    old_key = _resolve_old_key(home)
    try:
        rotated = rotate_file(data_path, old_key, new_key.encode("ascii"))
    except Exception as exc:  # noqa: BLE001
        # SECURITY: report only the error type — never the key/ciphertext.
        print(f"ERROR: rotation failed ({type(exc).__name__}).", file=sys.stderr)
        return 1

    if not rotated:
        print(f"No {data_path} to rotate (nothing encrypted yet).")
        return 0
    print(
        f"Rotated {data_path}. Now set AUTOFOLIO_VAULT_KEY=<new key> for the app "
        "and remove the stale .autofolio/vault.key if migrating off disk."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
