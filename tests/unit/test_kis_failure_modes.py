"""TASK-066: KISClient failure-mode tests.

All tests mock HTTP transport — no real network calls.
Covers:
- Network timeout → BrokerError raised (not swallowed)
- Auth token expiry response (rt_cd != "0") → BrokerError raised
- Invalid symbol response (missing stck_prpr) → BrokerError raised
- HTTP 4xx error response → BrokerError raised
- Rate-limit retry exhaustion → BrokerError raised
- place_order: missing ODNO in successful response → BrokerError raised
- get_order_status: partial-fill scenario → PENDING + correct filled_quantity
- ConfigurationError when KIS_BASE_URL is not set
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch, PropertyMock
import pytest
import requests

from app.brokers.base import OrderRequest
from app.brokers.kis.kis_client import KisClient
from app.common.enums import OrderStatus, OrderType, Side
from app.common.errors import BrokerError, ConfigurationError
from app.config.settings import Settings


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_client(base_url: str = "https://fake.kis.example") -> KisClient:
    """Build a KisClient with stubbed settings — no real credentials needed."""
    s = Settings(
        kis_env="paper",
        kis_app_key="FAKE_KEY",
        kis_app_secret="FAKE_SECRET",
        kis_account_no="12345678",
        kis_account_product_code="01",
        kis_base_url=base_url,
    )
    client = KisClient(app_settings=s)
    # Stub the auth token so _headers() doesn't hit the network
    client.auth = MagicMock()
    client.auth.get_access_token.return_value = "FAKE_TOKEN"
    return client


def _ok_response(body: dict, status_code: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = body
    resp.headers = {}
    resp.text = str(body)
    resp.encoding = "utf-8"
    return resp


def _buy_request() -> OrderRequest:
    return OrderRequest(
        symbol="005930",
        side=Side.BUY,
        order_type=OrderType.MARKET,
        quantity=1,
        price=None,
    )


# ---------------------------------------------------------------------------
# 1. Network timeout
# ---------------------------------------------------------------------------

class TestNetworkTimeout:
    def test_get_current_price_timeout_raises_broker_error(self):
        """requests.Timeout during get_current_price must surface as BrokerError."""
        client = _make_client()
        with patch("requests.request", side_effect=requests.Timeout("connection timed out")):
            with pytest.raises(BrokerError, match="request error"):
                client.get_current_price("005930")

    def test_place_order_timeout_raises_broker_error(self):
        """requests.Timeout during place_order must surface as BrokerError."""
        client = _make_client()
        with patch("requests.request", side_effect=requests.Timeout("read timeout")):
            with pytest.raises(BrokerError, match="request error"):
                client.place_order(_buy_request())

    def test_connection_error_raises_broker_error(self):
        """requests.ConnectionError must surface as BrokerError (not propagate raw)."""
        client = _make_client()
        with patch("requests.request", side_effect=requests.ConnectionError("refused")):
            with pytest.raises(BrokerError):
                client.get_current_price("005930")


# ---------------------------------------------------------------------------
# 2. Auth / token expiry
# ---------------------------------------------------------------------------

class TestAuthExpiry:
    def test_expired_token_response_raises_broker_error(self):
        """KIS rt_cd != '0' with auth-style msg_cd raises BrokerError."""
        client = _make_client()
        # KIS auth expiry returns rt_cd="1", msg_cd="EGW00123" or similar
        expired_body = {
            "rt_cd": "1",
            "msg_cd": "EGW00123",
            "msg1": "인증 토큰이 만료되었습니다.",
        }
        with patch("requests.request", return_value=_ok_response(expired_body)):
            with pytest.raises(BrokerError, match="rejected"):
                client.get_current_price("005930")

    def test_non_zero_rt_cd_always_raises_broker_error(self):
        """Any rt_cd != '0' is a protocol-level rejection — must raise BrokerError."""
        client = _make_client()
        rejection_body = {"rt_cd": "9", "msg_cd": "ECODE999", "msg1": "서버 오류"}
        with patch("requests.request", return_value=_ok_response(rejection_body)):
            with pytest.raises(BrokerError, match="rejected"):
                client.get_current_price("005930")


# ---------------------------------------------------------------------------
# 3. Invalid symbol / missing price field
# ---------------------------------------------------------------------------

class TestInvalidSymbolResponse:
    def test_missing_stck_prpr_raises_broker_error(self):
        """If KIS returns rt_cd=0 but stck_prpr is absent, raise BrokerError (not KeyError)."""
        client = _make_client()
        # Simulate a valid rt_cd=0 but output is empty — no stck_prpr field
        body = {"rt_cd": "0", "msg_cd": "FHKST01010100", "output": {}}
        with patch("requests.request", return_value=_ok_response(body)):
            with pytest.raises(BrokerError, match="stck_prpr"):
                client.get_current_price("INVALID_SYMBOL")

    def test_http_4xx_raises_broker_error(self):
        """HTTP 4xx (e.g., 403 Forbidden) must raise BrokerError with status code."""
        client = _make_client()
        forbidden_resp = _ok_response({"rt_cd": "1", "msg_cd": "EGW00401", "msg1": "Forbidden"}, status_code=403)
        with patch("requests.request", return_value=forbidden_resp):
            with pytest.raises(BrokerError, match="403"):
                client.get_current_price("005930")


# ---------------------------------------------------------------------------
# 4. Rate-limit retry exhaustion
# ---------------------------------------------------------------------------

class TestRateLimitRetry:
    def test_rate_limit_exhaustion_raises_broker_error(self):
        """After max_retries on rate-limit msg_cd, KisClient raises BrokerError."""
        client = _make_client()
        # Every response returns the rate-limit code
        rate_limit_body = {"rt_cd": "0", "msg_cd": "EGW00201", "msg1": "초당 거래건수 초과"}
        # KIS treats EGW00201 specially: if rt_cd="0" but msg_cd is rate-limit, retry
        # After retries exhausted, raise BrokerError
        # However the current code path: msg_cd == _RATE_LIMIT_MSG_CD triggers retry;
        # when retries are exhausted, it raises BrokerError with "rate-limited"
        with patch("requests.request", return_value=_ok_response(rate_limit_body)):
            with pytest.raises(BrokerError, match="rate-limited|EGW00201"):
                client.get_current_price("005930")


# ---------------------------------------------------------------------------
# 5. place_order: ODNO missing in accepted response
# ---------------------------------------------------------------------------

class TestPlaceOrderEdgeCases:
    def test_missing_odno_raises_broker_error(self):
        """If KIS accepts the order (rt_cd=0) but ODNO is absent, raise BrokerError."""
        client = _make_client()
        # Accepted response without ODNO
        accepted_body = {
            "rt_cd": "0",
            "msg_cd": "TTTC0012U",
            "msg1": "주문이 정상적으로 접수되었습니다.",
            "output": {"KRX_FWDG_ORD_ORGNO": "91011"},  # No ODNO key
        }
        with patch("requests.request", return_value=_ok_response(accepted_body)):
            with pytest.raises(BrokerError, match="ODNO"):
                client.place_order(_buy_request())


# ---------------------------------------------------------------------------
# 6. get_order_status: partial fill
# ---------------------------------------------------------------------------

class TestGetOrderStatusPartialFill:
    def test_partial_fill_returns_pending_with_filled_quantity(self):
        """Partial fill: ccld_qty < ord_qty, rmn_qty > 0 → PENDING with correct filled_quantity."""
        client = _make_client()
        partial_fill_body = {
            "rt_cd": "0",
            "msg_cd": "TTTC0081R",
            "output1": [
                {
                    "odno": "12345",
                    "ord_qty": "10",
                    "tot_ccld_qty": "3",
                    "rmn_qty": "7",
                    "avg_prvs": "70000",
                    "cncl_yn": "N",
                }
            ],
        }
        with patch("requests.request", return_value=_ok_response(partial_fill_body)):
            result = client.get_order_status("12345")

        assert result.status == OrderStatus.PENDING
        assert result.filled_quantity == 3
        assert result.broker_order_id == "12345"

    def test_full_fill_returns_filled_status(self):
        """Full fill: rmn_qty=0, ccld_qty=ord_qty → FILLED with filled_price."""
        client = _make_client()
        full_fill_body = {
            "rt_cd": "0",
            "msg_cd": "TTTC0081R",
            "output1": [
                {
                    "odno": "99999",
                    "ord_qty": "5",
                    "tot_ccld_qty": "5",
                    "rmn_qty": "0",
                    "avg_prvs": "65000",
                    "cncl_yn": "N",
                }
            ],
        }
        with patch("requests.request", return_value=_ok_response(full_fill_body)):
            result = client.get_order_status("99999")

        assert result.status == OrderStatus.FILLED
        assert result.filled_quantity == 5
        assert result.filled_price == 65_000.0

    def test_canceled_order_returns_canceled_status(self):
        """cncl_yn='Y' → CANCELED status."""
        client = _make_client()
        canceled_body = {
            "rt_cd": "0",
            "msg_cd": "TTTC0081R",
            "output1": [
                {
                    "odno": "77777",
                    "ord_qty": "2",
                    "tot_ccld_qty": "0",
                    "rmn_qty": "2",
                    "avg_prvs": "0",
                    "cncl_yn": "Y",
                }
            ],
        }
        with patch("requests.request", return_value=_ok_response(canceled_body)):
            result = client.get_order_status("77777")

        assert result.status == OrderStatus.CANCELED

    def test_order_not_found_returns_pending(self):
        """If ODNO is not found in today's records, return PENDING (assumed still in queue)."""
        client = _make_client()
        empty_body = {"rt_cd": "0", "msg_cd": "TTTC0081R", "output1": []}
        with patch("requests.request", return_value=_ok_response(empty_body)):
            result = client.get_order_status("NON_EXISTENT")

        assert result.status == OrderStatus.PENDING
        assert "pending" in (result.message or "").lower()


# ---------------------------------------------------------------------------
# 7. ConfigurationError when base URL is missing
# ---------------------------------------------------------------------------

class TestConfigurationErrors:
    def test_missing_base_url_raises_configuration_error(self):
        """KisClient._request raises ConfigurationError when kis_base_url is empty."""
        client = _make_client(base_url="")  # empty base URL

        with pytest.raises(ConfigurationError, match="KIS_BASE_URL"):
            client.get_current_price("005930")
