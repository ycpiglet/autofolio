from unittest.mock import MagicMock, patch
from datetime import date
import pytest
import app.brokers.kis.kis_client as kc
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
    c._paper = True
    return c


def _resp(body, headers=None):
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = body
    m.text = str(body)
    m.headers = headers or {}
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
    assert set(rows[0]) >= {"ord_dt", "odno", "pdno", "tot_ccld_qty", "rmn_qty"}


def test_get_order_history_uses_long_term_tr_before_cutoff(monkeypatch):
    c = _make_client()
    calls = []
    monkeypatch.setattr(kc, "_today_kst", lambda: date(2026, 6, 12))

    def fake_request(*args, **kwargs):
        calls.append(kwargs)
        return _resp({"rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok", "output1": []})

    monkeypatch.setattr("requests.request", fake_request)

    rows = c.get_order_history("20260201", "20260228")

    assert rows == []
    assert calls[0]["headers"]["tr_id"] == "VTSC9215R"
    assert calls[0]["params"]["INQR_STRT_DT"] == "20260201"
    assert calls[0]["params"]["INQR_END_DT"] == "20260228"


def test_get_order_history_splits_range_across_three_month_cutoff(monkeypatch):
    c = _make_client()
    calls = []
    monkeypatch.setattr(kc, "_today_kst", lambda: date(2026, 6, 12))

    def fake_request(*args, **kwargs):
        calls.append(kwargs)
        return _resp({"rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok", "output1": []})

    monkeypatch.setattr("requests.request", fake_request)

    c.get_order_history("20260301", "20260315")

    assert [call["headers"]["tr_id"] for call in calls] == ["VTSC9215R", "VTTC0081R"]
    assert calls[0]["params"]["INQR_STRT_DT"] == "20260301"
    assert calls[0]["params"]["INQR_END_DT"] == "20260311"
    assert calls[1]["params"]["INQR_STRT_DT"] == "20260312"
    assert calls[1]["params"]["INQR_END_DT"] == "20260315"


def test_get_order_history_paginates(monkeypatch):
    c = _make_client()
    monkeypatch.setattr(kc, "_today_kst", lambda: date(2026, 6, 12))
    calls = []
    responses = [
        _resp(
            {
                "rt_cd": "0",
                "msg_cd": "MAAP0",
                "msg1": "ok",
                "output1": [{"odno": "1", "pdno": "005930"}],
                "ctx_area_fk100": "FK",
                "ctx_area_nk100": "NK",
            },
            headers={"tr_cont": "M"},
        ),
        _resp(
            {
                "rt_cd": "0",
                "msg_cd": "MAAP0",
                "msg1": "ok",
                "output1": [{"odno": "2", "pdno": "000660"}],
            },
            headers={"tr_cont": "D"},
        ),
    ]

    def fake_request(*args, **kwargs):
        calls.append(kwargs)
        return responses.pop(0)

    monkeypatch.setattr("requests.request", fake_request)

    rows = c.get_order_history("20260601", "20260610")

    assert [row["odno"] for row in rows] == ["1", "2"]
    assert calls[1]["headers"]["tr_cont"] == "N"
    assert calls[1]["params"]["CTX_AREA_FK100"] == "FK"
    assert calls[1]["params"]["CTX_AREA_NK100"] == "NK"


def test_get_today_orders_paginates(monkeypatch):
    c = _make_client()
    calls = []
    responses = [
        _resp(
            {
                "rt_cd": "0",
                "msg_cd": "MAAP0",
                "msg1": "ok",
                "output1": [{"odno": "1", "pdno": "005930"}],
                "ctx_area_fk100": "FK",
                "ctx_area_nk100": "NK",
            },
            headers={"tr_cont": "M"},
        ),
        _resp(
            {
                "rt_cd": "0",
                "msg_cd": "MAAP0",
                "msg1": "ok",
                "output1": [{"odno": "2", "pdno": "000660"}],
            },
            headers={"tr_cont": "D"},
        ),
    ]

    def fake_request(*args, **kwargs):
        calls.append(kwargs)
        return responses.pop(0)

    monkeypatch.setattr("requests.request", fake_request)

    rows = c.get_today_orders()

    assert [row["odno"] for row in rows] == ["1", "2"]
    assert calls[1]["headers"]["tr_cont"] == "N"
    assert calls[1]["params"]["CTX_AREA_FK100"] == "FK"
    assert calls[1]["params"]["CTX_AREA_NK100"] == "NK"


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


def test_get_order_history_validates_date_order():
    c = _make_client()
    with pytest.raises(ValueError, match="end_date"):
        c.get_order_history("20260610", "20260601")
