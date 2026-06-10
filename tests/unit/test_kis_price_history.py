from unittest.mock import patch, MagicMock
import pytest
from app.brokers.kis.kis_client import KisClient
from app.config.settings import resolve_settings
from app.common.errors import BrokerError


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


def _resp(body: dict):
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = body
    m.text = str(body)
    return m


def test_get_price_history_returns_list_of_dicts(monkeypatch):
    c = _make_client()
    fake_output2 = [
        {"stck_bsop_date": "20260609", "stck_clpr": "302000",
         "stck_oprc": "300000", "stck_hgpr": "305000",
         "stck_lwpr": "299000", "acml_vol": "12000000"},
        {"stck_bsop_date": "20260608", "stck_clpr": "298000",
         "stck_oprc": "297000", "stck_hgpr": "301000",
         "stck_lwpr": "296000", "acml_vol": "9000000"},
    ]
    body = {"rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok", "output2": fake_output2}
    monkeypatch.setattr("requests.request", lambda *a, **kw: _resp(body))
    rows = c.get_price_history("005930", period="D", count=2)
    assert len(rows) == 2
    assert rows[0]["date"] == "20260609"
    assert rows[0]["close"] == 302000.0
    assert rows[0]["volume"] == 12_000_000


def test_get_price_history_respects_count(monkeypatch):
    c = _make_client()
    fake_output2 = [
        {"stck_bsop_date": f"2026060{i}", "stck_clpr": "300000",
         "stck_oprc": "299000", "stck_hgpr": "301000",
         "stck_lwpr": "298000", "acml_vol": "5000000"}
        for i in range(1, 6)
    ]
    body = {"rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok", "output2": fake_output2}
    monkeypatch.setattr("requests.request", lambda *a, **kw: _resp(body))
    rows = c.get_price_history("005930", period="D", count=3)
    assert len(rows) == 3


def test_get_price_history_returns_empty_on_broker_error(monkeypatch):
    c = _make_client()
    body = {"rt_cd": "1", "msg_cd": "ERR", "msg1": "fail"}
    monkeypatch.setattr("requests.request", lambda *a, **kw: _resp(body))
    rows = c.get_price_history("005930")
    assert rows == []
