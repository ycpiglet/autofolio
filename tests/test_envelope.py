"""P2 envelope-encryption crypto tests (pure functions, test-generated KEK).

Security-critical. These never touch the environment or a database — they
validate the DEK/KEK envelope scheme directly:
  * payload round-trip under a per-user DEK,
  * cross-user isolation (one user's DEK cannot read another's ciphertext),
  * the KEK correctly wraps/unwraps each user's own DEK,
  * KEK rotation re-wraps a DEK under a new KEK with NO payload re-encryption.
"""
from __future__ import annotations

import pytest
from cryptography.fernet import Fernet, InvalidToken

from app.services import envelope


def _test_kek() -> bytes:
    """A throwaway KEK generated in-test — never the real AUTOFOLIO_VAULT_KEY."""
    return Fernet.generate_key()


# ── Payload round-trip ──────────────────────────────────────────────────────

def test_encrypt_decrypt_round_trip():
    dek = envelope.generate_dek()
    secret = "sk-super-secret-kis-credential-1234"
    token = envelope.encrypt(secret, dek)
    assert token != secret
    assert secret not in token
    assert envelope.decrypt(token, dek) == secret


def test_each_dek_is_distinct():
    assert envelope.generate_dek() != envelope.generate_dek()


def test_encrypt_is_nondeterministic():
    dek = envelope.generate_dek()
    assert envelope.encrypt("same", dek) != envelope.encrypt("same", dek)


# ── DEK wrap / unwrap under the KEK ─────────────────────────────────────────

def test_wrap_unwrap_dek_round_trip():
    kek = _test_kek()
    dek = envelope.generate_dek()
    wrapped = envelope.wrap_dek(dek, kek)
    assert wrapped != dek.decode("ascii")
    assert envelope.unwrap_dek(wrapped, kek) == dek


def test_kek_unwraps_each_users_own_dek():
    """The single KEK correctly unwraps each user's distinct DEK."""
    kek = _test_kek()
    dek_a = envelope.generate_dek()
    dek_b = envelope.generate_dek()
    wrapped_a = envelope.wrap_dek(dek_a, kek)
    wrapped_b = envelope.wrap_dek(dek_b, kek)
    assert envelope.unwrap_dek(wrapped_a, kek) == dek_a
    assert envelope.unwrap_dek(wrapped_b, kek) == dek_b
    assert dek_a != dek_b


def test_wrong_kek_cannot_unwrap_dek():
    dek = envelope.generate_dek()
    wrapped = envelope.wrap_dek(dek, _test_kek())
    with pytest.raises(InvalidToken):
        envelope.unwrap_dek(wrapped, _test_kek())  # different KEK


# ── Cross-user isolation (crypto layer) ─────────────────────────────────────

def test_cross_user_dek_cannot_decrypt_other_users_ciphertext():
    """User A's ciphertext is unreadable with user B's DEK, even though the
    same KEK wraps both DEKs."""
    kek = _test_kek()
    dek_a = envelope.generate_dek()
    dek_b = envelope.generate_dek()

    ct_a = envelope.encrypt("alice-kis-secret", dek_a)
    ct_b = envelope.encrypt("bob-kis-secret", dek_b)

    # Each user reads only their own payload with their own (unwrapped) DEK.
    assert envelope.decrypt(ct_a, envelope.unwrap_dek(envelope.wrap_dek(dek_a, kek), kek)) == "alice-kis-secret"
    assert envelope.decrypt(ct_b, envelope.unwrap_dek(envelope.wrap_dek(dek_b, kek), kek)) == "bob-kis-secret"

    # Cross decryption is impossible.
    with pytest.raises(InvalidToken):
        envelope.decrypt(ct_a, dek_b)
    with pytest.raises(InvalidToken):
        envelope.decrypt(ct_b, dek_a)


# ── KEK rotation ────────────────────────────────────────────────────────────

def test_kek_rotation_rewrap_keeps_payload_decryptable():
    """Re-wrapping the DEK under a new KEK leaves the ciphertext valid — the
    payload is NOT re-encrypted."""
    dek = envelope.generate_dek()
    ciphertext = envelope.encrypt("rotate-me-secret", dek)

    kek_v1 = _test_kek()
    kek_v2 = _test_kek()
    assert kek_v1 != kek_v2

    wrapped_v1 = envelope.wrap_dek(dek, kek_v1)
    wrapped_v2 = envelope.rewrap_dek(wrapped_v1, kek_v1, kek_v2)

    # The wrapped DEK changed; the ciphertext (payload) is byte-identical.
    assert wrapped_v2 != wrapped_v1

    # Old KEK can no longer unwrap the re-wrapped DEK.
    with pytest.raises(InvalidToken):
        envelope.unwrap_dek(wrapped_v2, kek_v1)

    # New KEK unwraps to the SAME DEK, and the original payload still decrypts.
    dek_after = envelope.unwrap_dek(wrapped_v2, kek_v2)
    assert dek_after == dek
    assert envelope.decrypt(ciphertext, dek_after) == "rotate-me-secret"
