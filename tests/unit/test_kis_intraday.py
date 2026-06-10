from unittest.mock import MagicMock, patch
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


def test_get_intraday_chart_returns_list(monkeypatch):
    c = _make_client()
    fake_output2 = [
        {"stck_bsop_date": "20260611", "stck_cntg_hour": "090100",
         "stck_prpr": "303000", "stck_oprc": "302000",
         "stck_hgpr": "304000", "stck_lwpr": "301000", "cntg_vol": "5000"},
        {"stck_bsop_date": "20260611", "stck_cntg_hour": "090200",
         "stck_prpr": "304000", "stck_oprc": "303000",
         "stck_hgpr": "305000", "stck_lwpr": "302000", "cntg_vol": "3000"},
    ]
    body = {"rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok", "output2": fake_output2}
    monkeypatch.setattr("requests.request", lambda *a, **kw: _resp(body))
    rows = c.get_intraday_chart("005930", time_unit="1")
    assert len(rows) == 2
    assert rows[0]["datetime"] == "20260611 090100"
    assert rows[0]["close"] == 303000.0
    assert rows[0]["volume"] == 5000


def test_get_intraday_chart_empty_on_error(monkeypatch):
    c = _make_client()
    body = {"rt_cd": "1", "msg_cd": "ERR", "msg1": "fail"}
    monkeypatch.setattr("requests.request", lambda *a, **kw: _resp(body))
    rows = c.get_intraday_chart("005930")
    assert rows == []


def test_get_intraday_chart_respects_count(monkeypatch):
    c = _make_client()
    fake_output2 = [
        {"stck_bsop_date": "20260611", "stck_cntg_hour": f"09{i:02d}00",
         "stck_prpr": "303000", "stck_oprc": "302000",
         "stck_hgpr": "304000", "stck_lwpr": "301000", "cntg_vol": "1000"}
        for i in range(10)
    ]
    body = {"rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok", "output2": fake_output2}
    monkeypatch.setattr("requests.request", lambda *a, **kw: _resp(body))
    rows = c.get_intraday_chart("005930", count=3)
    assert len(rows) == 3
