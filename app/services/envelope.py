"""Envelope encryption for per-user secret durability (P2).

Scheme (envelope / DEK-under-KEK)
---------------------------------
::

    plaintext  --encrypt(DEK)-->  ciphertext     # payload sealed under a per-user DEK
    DEK        --wrap(KEK)----->  wrapped_dek     # the DEK sealed ("wrapped") under the master KEK

Only ``{wrapped_dek, ciphertext, key_version}`` are ever persisted (e.g. in
Postgres). The master **KEK** (``AUTOFOLIO_VAULT_KEY``) lives ONLY in the app
environment (Railway) and is NEVER written to the database. Compromising the
database WITHOUT the KEK yields nothing: the wrapped DEK cannot be unwrapped, so
the ciphertext cannot be decrypted.

* **Per-user isolation** — every secret gets a fresh random DEK, so one user's
  ``wrapped_dek``/``ciphertext`` is meaningless to another user.
* **KEK rotation** — :func:`rewrap_dek` re-wraps an existing DEK under a new KEK
  version; the payload (``ciphertext``) is left untouched because it is sealed
  under the DEK, not the KEK. ``key_version`` records which KEK wrapped a DEK.

All functions here are PURE and fully unit-testable with a test-generated KEK —
they never read the environment. KEK sourcing for the running app is the
caller's job (see :func:`app.ui.vault.key_bytes`, which reads
``AUTOFOLIO_VAULT_KEY`` off-disk and fails loud on a malformed key).
"""
from __future__ import annotations

from cryptography.fernet import Fernet

# Master-key version stamped onto newly wrapped DEKs. Bump (and re-wrap existing
# blobs via :func:`rewrap_dek`) when the KEK is rotated, so every stored blob
# records which KEK version wrapped its DEK.
CURRENT_KEY_VERSION = 1


def generate_dek() -> bytes:
    """Return a fresh per-secret Data Encryption Key (a urlsafe-base64 Fernet key)."""
    return Fernet.generate_key()


def encrypt(plaintext: str, dek: bytes) -> str:
    """Encrypt *plaintext* under the per-user *dek*. Returns a urlsafe token string."""
    return Fernet(dek).encrypt(plaintext.encode("utf-8")).decode("ascii")


def decrypt(token: str, dek: bytes) -> str:
    """Decrypt a token produced by :func:`encrypt` with the same *dek*.

    Raises ``cryptography.fernet.InvalidToken`` if *dek* is not the DEK that
    produced *token* (this is what enforces cross-user isolation at the crypto
    layer: another user's DEK cannot read this payload).
    """
    return Fernet(dek).decrypt(token.encode("ascii")).decode("utf-8")


def wrap_dek(dek: bytes, kek: bytes) -> str:
    """Wrap (encrypt) *dek* under the master *kek*. Returns a urlsafe token string."""
    return Fernet(kek).encrypt(dek).decode("ascii")


def unwrap_dek(wrapped: str, kek: bytes) -> bytes:
    """Unwrap (decrypt) a wrapped DEK with the master *kek*. Returns the DEK bytes.

    Raises ``cryptography.fernet.InvalidToken`` if *kek* did not wrap this DEK.
    """
    return Fernet(kek).decrypt(wrapped.encode("ascii"))


def rewrap_dek(wrapped: str, old_kek: bytes, new_kek: bytes) -> str:
    """Re-wrap a DEK from *old_kek* to *new_kek* WITHOUT touching the payload.

    KEK rotation primitive: unwrap the DEK with the old KEK and re-wrap it with
    the new KEK. The ciphertext stays valid and is never re-encrypted, because
    it is sealed under the (unchanged) DEK — only the DEK's wrapping key changes.
    """
    dek = unwrap_dek(wrapped, old_kek)
    return wrap_dek(dek, new_kek)
