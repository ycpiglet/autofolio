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


def test_get_order_history_returns_parsed_list(monkeypatch):
    c = _make_client()
    fake_output1 = [
        {"odno": "0000037101", "pdno": "005930", "sll_buy_dvsn_cd": "02",
         "ord_qty": "1", "tot_ccld_qty": "1", "rmn_qty": "0",
         "ord_unpr": "303000", "avg_prvs": "303000",
         "cncl_yn": "N", "ord_tmd": "090100", "ord_dt": "20260610"},
    ]
    body = {"rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok",
            "output1": fake_output1, "output2": {}}
    monkeypatch.setattr("requests.request", lambda *a, **kw: _resp(body))
    rows = c.get_order_history("20260601", "20260610")
    assert len(rows) == 1
    assert rows[0]["odno"] == "0000037101"
    assert rows[0]["pdno"] == "005930"


def test_get_order_history_returns_empty_on_error(monkeypatch):
    c = _make_client()
    body = {"rt_cd": "1", "msg_cd": "ERR", "msg1": "fail"}
    monkeypatch.setattr("requests.request", lambda *a, **kw: _resp(body))
    rows = c.get_order_history("20260601", "20260610")
    assert rows == []


def test_get_order_history_validates_date_format():
    c = _make_client()
    with pytest.raises(ValueError, match="YYYYMMDD"):
        c.get_order_history("2026-06-01", "2026-06-10")


def test_get_order_history_validates_end_date_format():
    c = _make_client()
    with pytest.raises(ValueError, match="YYYYMMDD"):
        c.get_order_history("20260601", "2026-06-10")
