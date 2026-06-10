"""Tests for KisAuth cache methods (_load_cache, _save_cache) and token fetch path."""
import json
import time
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.brokers.kis.kis_auth import KisAuth, KisToken
from app.config.settings import Settings


def _make_auth(tmp_path: Path) -> KisAuth:
    s = Settings(
        kis_env="paper",
        kis_base_url="https://openapivts.koreainvestment.com:29443",
        kis_app_key="testkey",
        kis_app_secret="testsecret",
        kis_account_no="12345678",
        kis_account_product_code="01",
        kis_token_path="/oauth2/tokenP",
    )
    # Patch cache dir to use tmp_path to avoid writing to real .autofolio
    with patch("app.brokers.kis.kis_auth.Path") as mock_path_cls:
        # Make the cache path point to tmp_path
        mock_path_cls.return_value.__truediv__ = lambda self, other: tmp_path / other
        mock_path_cls.return_value.resolve.return_value = tmp_path
        mock_path_cls.return_value.parents = [None, None, None, tmp_path]
        # Let Path still work for other uses
        pass

    # Simpler approach: create auth normally then override _cache_path
    auth = KisAuth.__new__(KisAuth)
    auth.settings = s
    auth._token = None
    auth._cache_path = tmp_path / f"kis_token_{s.kis_env}.json"
    auth._load_cache()
    return auth


def test_load_cache_no_file_leaves_token_none(tmp_path):
    auth = _make_auth(tmp_path)
    assert auth._token is None


def test_save_and_load_cache(tmp_path):
    auth = _make_auth(tmp_path)
    future_epoch = time.time() + 3600
    token = KisToken(access_token="test-token-abc", expires_at_epoch=future_epoch)
    auth._save_cache(token)

    # Verify file exists
    assert auth._cache_path.exists()

    # Fresh auth instance should load the cached token
    auth2 = _make_auth(tmp_path)
    assert auth2._token is not None
    assert auth2._token.access_token == "test-token-abc"


def test_load_cache_handles_corrupt_file(tmp_path):
    auth = _make_auth(tmp_path)
    auth._cache_path.write_text("not valid json")
    # Load cache — should not raise, leaves token as None
    auth._load_cache()
    assert auth._token is None


def test_load_cache_handles_expired_token(tmp_path):
    auth = _make_auth(tmp_path)
    # Write a token with expired epoch
    expired_data = {"access_token": "expired-tok", "expires_at_epoch": 1.0}
    auth._cache_path.write_text(json.dumps(expired_data))
    auth._load_cache()
    # Token exists but is invalid → not loaded
    assert auth._token is None


def test_save_cache_handles_failure(tmp_path):
    auth = _make_auth(tmp_path)
    token = KisToken(access_token="tok", expires_at_epoch=time.time() + 3600)
    # Point to unwritable path
    auth._cache_path = Path("/nonexistent/path/to/file.json")
    # Should not raise
    auth._save_cache(token)


def test_kis_token_is_valid_future():
    token = KisToken(access_token="tok", expires_at_epoch=time.time() + 3600)
    assert token.is_valid is True


def test_kis_token_is_not_valid_expired():
    token = KisToken(access_token="tok", expires_at_epoch=1.0)
    assert token.is_valid is False


def test_kis_token_is_not_valid_empty_access_token():
    token = KisToken(access_token="", expires_at_epoch=time.time() + 3600)
    assert token.is_valid is False


def test_get_access_token_raises_when_missing_base_url(tmp_path):
    from app.common.errors import ConfigurationError
    s = Settings(
        kis_env="paper",
        kis_base_url="",
        kis_token_path="",
        kis_app_key="key",
        kis_app_secret="secret",
    )
    auth = _make_auth(tmp_path)
    auth.settings = s
    auth._token = None
    with pytest.raises(ConfigurationError):
        auth.get_access_token()


def test_get_access_token_raises_when_missing_app_key(tmp_path):
    from app.common.errors import ConfigurationError
    s = Settings(
        kis_env="paper",
        kis_base_url="https://example.com",
        kis_token_path="/oauth2/tokenP",
        kis_app_key="",
        kis_app_secret="",
    )
    auth = _make_auth(tmp_path)
    auth.settings = s
    auth._token = None
    with pytest.raises(ConfigurationError):
        auth.get_access_token()


def test_get_access_token_raises_on_http_error(tmp_path):
    from app.common.errors import BrokerError
    auth = _make_auth(tmp_path)
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized"
    with patch("requests.post", return_value=mock_resp):
        with pytest.raises(BrokerError):
            auth.get_access_token()


def test_get_access_token_raises_when_no_access_token_in_response(tmp_path):
    from app.common.errors import BrokerError
    auth = _make_auth(tmp_path)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"expires_in": 3600}  # no access_token
    with patch("requests.post", return_value=mock_resp):
        with pytest.raises(BrokerError):
            auth.get_access_token()


def test_get_access_token_success_saves_cache(tmp_path):
    auth = _make_auth(tmp_path)
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"access_token": "new-token-xyz", "expires_in": 86400}
    with patch("requests.post", return_value=mock_resp):
        token = auth.get_access_token()
    assert token == "new-token-xyz"
    assert auth._cache_path.exists()


def test_get_access_token_returns_cached_valid_token(tmp_path):
    auth = _make_auth(tmp_path)
    # Pre-load a valid token
    auth._token = KisToken(access_token="cached-token", expires_at_epoch=time.time() + 3600)
    with patch("requests.post") as mock_post:
        token = auth.get_access_token()
        mock_post.assert_not_called()
    assert token == "cached-token"
