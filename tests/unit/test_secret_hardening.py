"""Secret-handling hardening tests — P0 (leak-plugging) + P1 (key off disk).

Covers:
  * P0.1 broker exceptions never include response.text / full body.
  * P0.3 KIS token cache is encrypted (not cleartext) and round-trips.
  * P1.4 vault key sourced from AUTOFOLIO_VAULT_KEY (never on disk) with a
    backward-compatible co-located fallback when the env var is unset.
  * Rotation re-wraps vault.enc; data decrypts under the new key.
"""
import importlib
import json
import os
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from cryptography.fernet import Fernet, InvalidToken

from app.brokers.kis.kis_auth import KisAuth, KisToken
from app.common.errors import BrokerError
from app.config.settings import Settings


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _make_auth(tmp_path: Path) -> KisAuth:
    s = Settings(
        kis_env="paper",
        kis_base_url="https://example.com",
        kis_app_key="testkey",
        kis_app_secret="testsecret",
        kis_token_path="/oauth2/tokenP",
    )
    auth = KisAuth.__new__(KisAuth)
    auth.settings = s
    auth._token = None
    auth._cache_path = tmp_path / f"kis_token_{s.kis_env}.json"
    auth._load_cache()
    return auth


# --------------------------------------------------------------------------- #
# P0.1 — broker exceptions exclude raw secrets
# --------------------------------------------------------------------------- #
def test_token_http_error_excludes_response_text(tmp_path):
    auth = _make_auth(tmp_path)
    resp = MagicMock()
    resp.status_code = 401
    resp.text = "LEAK_appsecret=SUPERSECRET request_body_with_token"
    resp.json.return_value = {"msg_cd": "EGW00133", "msg1": "invalid creds"}
    with patch("requests.post", return_value=resp):
        with pytest.raises(BrokerError) as ei:
            auth.get_access_token()
    msg = str(ei.value)
    assert "LEAK_appsecret" not in msg
    assert "SUPERSECRET" not in msg
    assert "401" in msg            # status preserved
    assert "EGW00133" in msg       # safe KIS diagnostic preserved


def test_token_missing_access_token_excludes_body(tmp_path):
    auth = _make_auth(tmp_path)
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "access_token": "",
        "refresh_token": "LEAKED_REFRESH",
        "msg_cd": "X1",
        "msg1": "no token",
    }
    with patch("requests.post", return_value=resp):
        with pytest.raises(BrokerError) as ei:
            auth.get_access_token()
    msg = str(ei.value)
    assert "LEAKED_REFRESH" not in msg     # full body not dumped
    assert "X1" in msg                     # safe diagnostic preserved


def test_ws_approval_failure_excludes_response_text():
    from app.brokers.kis.kis_ws_client import get_approval_key

    s = Settings(
        kis_base_url="https://example.com",
        kis_app_key="k",
        kis_app_secret="s",
    )
    resp = MagicMock()
    resp.status_code = 403
    resp.text = "WSLEAK approval_key=SECRETAPPROVAL appkey=LEAK"
    resp.json.return_value = {"msg_cd": "OPSQ0001", "msg1": "denied"}
    with patch("requests.post", return_value=resp):
        with pytest.raises(BrokerError) as ei:
            get_approval_key(s)
    msg = str(ei.value)
    assert "WSLEAK" not in msg
    assert "SECRETAPPROVAL" not in msg
    assert "403" in msg
    assert "OPSQ0001" in msg


def test_ws_approval_missing_key_excludes_body():
    from app.brokers.kis.kis_ws_client import get_approval_key

    s = Settings(kis_base_url="https://example.com", kis_app_key="k", kis_app_secret="s")
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {"approval_key": "", "leak_field": "LEAKVAL", "msg_cd": "Z9"}
    with patch("requests.post", return_value=resp):
        with pytest.raises(BrokerError) as ei:
            get_approval_key(s)
    msg = str(ei.value)
    assert "LEAKVAL" not in msg
    assert "Z9" in msg


# --------------------------------------------------------------------------- #
# P0.3 — token cache is encrypted (env key keeps it off disk + deterministic)
# --------------------------------------------------------------------------- #
def test_token_cache_is_encrypted_and_round_trips(tmp_path):
    env_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {"AUTOFOLIO_VAULT_KEY": env_key}):
        auth = _make_auth(tmp_path)
        token = KisToken(access_token="LIVE_BEARER_SECRET", expires_at_epoch=time.time() + 3600)
        auth._save_cache(token)

        raw = auth._cache_path.read_bytes()
        assert b"LIVE_BEARER_SECRET" not in raw           # not cleartext
        with pytest.raises(json.JSONDecodeError):          # not plain JSON
            json.loads(raw.decode("utf-8", "ignore"))
        # decrypts with the vault key
        assert b"LIVE_BEARER_SECRET" in Fernet(env_key.encode()).decrypt(raw)

        auth2 = _make_auth(tmp_path)
        assert auth2._token is not None
        assert auth2._token.access_token == "LIVE_BEARER_SECRET"


def test_token_cache_old_cleartext_degrades_gracefully(tmp_path):
    env_key = Fernet.generate_key().decode()
    with patch.dict(os.environ, {"AUTOFOLIO_VAULT_KEY": env_key}):
        cache = tmp_path / "kis_token_paper.json"
        cache.write_text(json.dumps({"access_token": "old", "expires_at_epoch": time.time() + 999}))
        auth = _make_auth(tmp_path)
        assert auth._token is None      # undecryptable old cache → re-issue


# --------------------------------------------------------------------------- #
# P1.4 — vault key sourcing precedence + backward compatibility
# --------------------------------------------------------------------------- #
def _reload_vault(tmp_path: Path, env_key: str | None):
    env = {"AUTOFOLIO_HOME": str(tmp_path)}
    if env_key is None:
        os.environ.pop("AUTOFOLIO_VAULT_KEY", None)
    else:
        env["AUTOFOLIO_VAULT_KEY"] = env_key
    ctx = patch.dict(os.environ, env)
    ctx.start()
    if env_key is None:
        os.environ.pop("AUTOFOLIO_VAULT_KEY", None)
    import app.ui.vault as vault
    importlib.reload(vault)
    return vault, ctx


def test_vault_uses_env_key_and_never_writes_keyfile(tmp_path):
    env_key = Fernet.generate_key().decode()
    vault, ctx = _reload_vault(tmp_path, env_key)
    try:
        vault.save({"a": 1})
        # CRITICAL: env-key path never writes the key to disk.
        assert not (tmp_path / "vault.key").exists()
        assert vault.load() == {"a": 1}
        raw = (tmp_path / "vault.enc").read_bytes()
        assert json.loads(Fernet(env_key.encode()).decrypt(raw)) == {"a": 1}
    finally:
        ctx.stop()


def test_vault_unset_uses_colocated_file_byte_identical(tmp_path):
    """AUTOFOLIO_VAULT_KEY unset → co-located vault.key fallback (historical)."""
    vault, ctx = _reload_vault(tmp_path, None)
    try:
        vault.save({"b": 2})
        keyfile = tmp_path / "vault.key"
        assert keyfile.exists()                    # generated co-located key
        keybytes = keyfile.read_bytes()
        assert vault.load() == {"b": 2}
        raw = (tmp_path / "vault.enc").read_bytes()
        # data decrypts with the exact co-located key — byte-identical scheme.
        assert json.loads(Fernet(keybytes).decrypt(raw)) == {"b": 2}
    finally:
        ctx.stop()


def test_existing_colocated_data_still_decrypts_after_reload(tmp_path):
    """Existing vault.enc (encrypted with vault.key) stays readable when unset."""
    vault, ctx = _reload_vault(tmp_path, None)
    try:
        vault.save({"existing": "data"})
    finally:
        ctx.stop()
    # New process — env still unset → must use the same co-located key.
    vault, ctx = _reload_vault(tmp_path, None)
    try:
        assert vault.load() == {"existing": "data"}
    finally:
        ctx.stop()


# --------------------------------------------------------------------------- #
# Rotation — decrypt-with-old → re-encrypt-with-new
# --------------------------------------------------------------------------- #
def test_rotate_file_rewraps_and_decrypts_under_new_key(tmp_path):
    from scripts.rotate_vault_key import rotate_file

    old, new = Fernet.generate_key(), Fernet.generate_key()
    data_path = tmp_path / "vault.enc"
    data_path.write_bytes(Fernet(old).encrypt(b'{"x": 1}'))

    assert rotate_file(data_path, old, new) is True
    with pytest.raises(InvalidToken):
        Fernet(old).decrypt(data_path.read_bytes())   # old key no longer works
    assert Fernet(new).decrypt(data_path.read_bytes()) == b'{"x": 1}'


def test_rotate_then_vault_loads_with_new_env_key(tmp_path):
    from scripts.rotate_vault_key import rotate_file

    # Existing data written with the co-located key (env unset).
    vault, ctx = _reload_vault(tmp_path, None)
    try:
        vault.save({"secret": "v"})
        old = (tmp_path / "vault.key").read_bytes()
    finally:
        ctx.stop()

    new = Fernet.generate_key()
    rotate_file(tmp_path / "vault.enc", old, new)

    # After rotation, the app reads it via the NEW env key.
    vault, ctx = _reload_vault(tmp_path, new.decode())
    try:
        assert vault.load() == {"secret": "v"}
    finally:
        ctx.stop()


def test_rotate_file_noop_when_no_data(tmp_path):
    from scripts.rotate_vault_key import rotate_file

    old, new = Fernet.generate_key(), Fernet.generate_key()
    assert rotate_file(tmp_path / "vault.enc", old, new) is False
