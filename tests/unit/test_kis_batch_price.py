from unittest.mock import MagicMock, patch, call
import pytest
from app.brokers.kis.kis_client import KisClient
from app.brokers.base import PriceQuote
from app.config.settings import resolve_settings


def _make_client():
    s = resolve_settings("mock")
    c = KisClient(s)
    c.auth.get_access_token = lambda: "fake-token"
    object.__setattr__(c.settings, "kis_env", "paper")
    object.__setattr__(c.settings, "kis_base_url", "https://openapivts.koreainvestment.com:29443")
    object.__setattr__(c.settings, "kis_app_key", "testkey")
    object.__setattr__(c.settings, "kis_app_secret", "testsecret")
    object.__setattr__(c.settings, "kis_account_no", "12345678")
    object.__setattr__(c.settings, "kis_account_product_code", "01")
    return c


def test_get_prices_batch_returns_dict(monkeypatch):
    c = _make_client()
    call_count = {"n": 0}

    def fake_get_price(symbol):
        call_count["n"] += 1
        prices = {"005930": 303000.0, "069500": 123000.0, "000660": 200000.0}
        return PriceQuote(symbol=symbol, price=prices[symbol])

    monkeypatch.setattr(c, "get_current_price", fake_get_price)
    result = c.get_prices_batch(["005930", "069500", "000660"])
    assert result == {"005930": 303000.0, "069500": 123000.0, "000660": 200000.0}
    assert call_count["n"] == 3


def test_get_prices_batch_handles_partial_failure(monkeypatch):
    from app.common.errors import BrokerError
    c = _make_client()

    def fake_get_price(symbol):
        if symbol == "INVALID":
            raise BrokerError("not found")
        return PriceQuote(symbol=symbol, price=100000.0)

    monkeypatch.setattr(c, "get_current_price", fake_get_price)
    result = c.get_prices_batch(["005930", "INVALID", "069500"])
    assert "005930" in result
    assert "069500" in result
    assert "INVALID" not in result


def test_get_prices_batch_empty_list():
    c = _make_client()
    result = c.get_prices_batch([])
    assert result == {}
