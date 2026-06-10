from unittest.mock import patch, MagicMock
import pytest
from app.brokers.kis.kis_client import KisClient
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


def _resp(body):
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = body
    m.text = str(body)
    return m


def test_get_buying_power_returns_dict(monkeypatch):
    c = _make_client()
    body = {
        "rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok",
        "output": {
            "psbl_qty": "10",
            "nrcvb_buy_amt": "3000000",
            "ord_psbl_cash": "3500000",
        }
    }
    monkeypatch.setattr("requests.request", lambda *a, **kw: _resp(body))
    result = c.get_buying_power("005930", price=300000.0)
    assert result["max_quantity"] == 10
    assert result["available_cash"] == 3_500_000.0


def test_get_buying_power_returns_zeros_on_error(monkeypatch):
    c = _make_client()
    body = {"rt_cd": "1", "msg_cd": "ERR", "msg1": "fail"}
    monkeypatch.setattr("requests.request", lambda *a, **kw: _resp(body))
    result = c.get_buying_power("005930", price=300000.0)
    assert result["max_quantity"] == 0
    assert result["available_cash"] == 0.0
