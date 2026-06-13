"""KIS client network/HTTP failure mode tests."""
from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests as requests_lib

from app.brokers.kis.kis_auth import KisAuth, KisToken
from app.brokers.kis.kis_client import KisClient
from app.common.errors import BrokerError
from app.config.settings import Settings


# ---------------------------------------------------------------------------
# Helper: build a KisClient with a pre-loaded valid token (avoids real HTTP
# during __init__) and a short timeout/zero retries.
# ---------------------------------------------------------------------------

def _make_client() -> KisClient:
    """Return a KisClient wired to paper env with a mocked valid token."""
    s = Settings(
        kis_env="paper",
        kis_base_url="https://openapivts.koreainvestment.com:29443",
        kis_app_key="testkey",
        kis_app_secret="testsecret",
        kis_account_no="12345678",
        kis_account_product_code="01",
        kis_token_path="/oauth2/tokenP",
    )
    client = KisClient.__new__(KisClient)
    client.settings = s
    client._paper = True
    client._timeout = 5
    client._max_retries = 0  # no retry in unit tests
    client._rate_limit_wait = 0
    client._orders = {}
    client._last_batch_price_stats = {}

    # Inject a pre-loaded valid token so _headers() never calls real HTTP
    auth = KisAuth.__new__(KisAuth)
    auth.settings = s
    auth._token = KisToken(access_token="mock-token", expires_at_epoch=time.time() + 3600)
    auth._cache_path = Path("/tmp/fake_cache.json")  # not used — token already loaded
    client.auth = auth
    return client


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_kis_client_request_timeout_raises_broker_error():
    """requests.Timeout during _request must be converted to BrokerError."""
    client = _make_client()
    with patch("requests.request", side_effect=requests_lib.Timeout("timed out")):
        with pytest.raises(BrokerError, match="Timeout"):
            client.get_current_price("005930")


def test_kis_client_connection_error_raises_broker_error():
    """requests.ConnectionError during _request must be converted to BrokerError."""
    client = _make_client()
    with patch("requests.request", side_effect=requests_lib.ConnectionError("connection refused")):
        with pytest.raises(BrokerError, match="ConnectionError"):
            client.get_current_price("005930")


def test_kis_client_non_json_response_raises_broker_error():
    """A response whose .json() raises ValueError should surface as BrokerError."""
    client = _make_client()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.side_effect = ValueError("No JSON object")
    mock_resp.text = "Not JSON"
    mock_resp.headers = {}
    with patch("requests.request", return_value=mock_resp):
        with pytest.raises(BrokerError):
            client.get_current_price("005930")


def test_kis_client_http_500_non_rate_limit_raises_broker_error():
    """HTTP 500 with a non-rate-limit msg_cd must raise BrokerError without infinite retry."""
    client = _make_client()
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.json.return_value = {"rt_cd": "1", "msg_cd": "INTERNAL_ERROR", "msg1": "서버 오류"}
    mock_resp.text = "서버 오류"
    mock_resp.headers = {}
    with patch("requests.request", return_value=mock_resp):
        with pytest.raises(BrokerError, match="500"):
            client.get_current_price("005930")


def test_kis_client_401_unauthorized_raises_broker_error():
    """HTTP 401 must raise BrokerError."""
    client = _make_client()
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.json.return_value = {"rt_cd": "1", "msg_cd": "AUTH_FAIL", "msg1": "Unauthorized"}
    mock_resp.text = "Unauthorized"
    mock_resp.headers = {}
    with patch("requests.request", return_value=mock_resp):
        with pytest.raises(BrokerError, match="401"):
            client.get_current_price("005930")


def test_kis_client_place_order_empty_output_raises():
    """rt_cd=0 but output missing ODNO must raise BrokerError (order accepted but ID absent)."""
    from app.brokers.base import OrderRequest
    from app.common.enums import OrderType, Side

    client = _make_client()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "rt_cd": "0",
        "msg_cd": "MAPIBLPS0",
        "msg1": "주문 접수 완료",
        "output": {},  # ODNO missing
    }
    mock_resp.headers = {}

    with patch("requests.request", return_value=mock_resp):
        request = OrderRequest(
            symbol="005930",
            side=Side.BUY,
            order_type=OrderType.LIMIT,
            quantity=1,
            price=70000.0,
        )
        with pytest.raises(BrokerError, match="ODNO"):
            client.place_order(request)


def test_kis_get_access_token_refreshes_when_near_expiry(tmp_path):
    """Token expiring in 30 s (within the 60 s margin) triggers a network refresh."""
    from app.brokers.kis.kis_auth import KisAuth, KisToken
    from app.config.settings import Settings

    s = Settings(
        kis_env="paper",
        kis_base_url="https://openapivts.koreainvestment.com:29443",
        kis_app_key="testkey",
        kis_app_secret="testsecret",
        kis_token_path="/oauth2/tokenP",
    )
    auth = KisAuth.__new__(KisAuth)
    auth.settings = s
    auth._cache_path = tmp_path / "kis_token_paper.json"
    # Token expires in 30 s — within the 60 s margin → is_valid returns False
    auth._token = KisToken(access_token="old-token", expires_at_epoch=time.time() + 30)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"access_token": "refreshed-token", "expires_in": 86400}

    with patch("requests.post", return_value=mock_resp) as mock_post:
        token = auth.get_access_token()

    assert token == "refreshed-token"
    mock_post.assert_called_once()
