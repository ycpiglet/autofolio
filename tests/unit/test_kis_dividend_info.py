from __future__ import annotations

from unittest.mock import MagicMock

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
    c._paper = True
    return c


def _resp(body, headers=None):
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = body
    m.text = str(body)
    m.headers = headers or {}
    return m


def test_get_dividend_info_sends_official_params_and_parses(monkeypatch):
    c = _make_client()
    calls = []

    def fake_request(*args, **kwargs):
        calls.append((args, kwargs))
        return _resp(
            {
                "rt_cd": "0",
                "msg_cd": "MAAP0",
                "msg1": "ok",
                "output1": [
                    {
                        "record_date": "20260331",
                        "sht_cd": "005930",
                        "divi_kind": "결산배당",
                        "per_sto_divi_amt": "361",
                        "divi_rate": "0.48",
                        "stk_divi_rate": "",
                        "divi_pay_dt": "20260515",
                        "stk_div_pay_dt": "",
                        "stk_kind": "보통주",
                        "high_divi_gb": "",
                    },
                    {
                        "record_date": "20260630",
                        "sht_cd": "005930",
                        "divi_kind": "중간배당",
                        "per_sto_divi_amt": "361",
                        "divi_rate": "0.49",
                        "divi_pay_dt": "20260815",
                    },
                ],
            }
        )

    monkeypatch.setattr(kc.requests, "request", fake_request)

    result = c.get_dividend_info("005930", start_date="20260101", end_date="20261231")

    args, kwargs = calls[0]
    assert kwargs["headers"]["tr_id"] == "HHKDB669102C0"
    assert kwargs["params"] == {
        "CTS": "",
        "GB1": "0",
        "F_DT": "20260101",
        "T_DT": "20261231",
        "SHT_CD": "005930",
        "HIGH_GB": "",
    }
    assert args[1].endswith("/uapi/domestic-stock/v1/ksdinfo/dividend")
    assert result["symbol"] == "005930"
    assert result["annual_cash_dividend"] == 722.0
    assert result["latest_dividend_rate"] == 0.49
    assert result["records"][0]["pay_date"] == "20260515"
    assert result["records"][0]["cash_dividend"] == 361.0


def test_get_dividend_info_returns_empty_on_broker_error(monkeypatch):
    c = _make_client()
    monkeypatch.setattr(
        kc.requests,
        "request",
        lambda *args, **kwargs: _resp({"rt_cd": "1", "msg_cd": "ERR", "msg1": "fail"}),
    )

    assert c.get_dividend_info("005930", start_date="20260101", end_date="20261231") == {}


def test_get_dividend_info_validates_symbol_and_dates():
    c = _make_client()
    with pytest.raises(ValueError, match="symbol"):
        c.get_dividend_info("")
    with pytest.raises(ValueError, match="YYYYMMDD"):
        c.get_dividend_info("005930", start_date="2026-01-01", end_date="20261231")
