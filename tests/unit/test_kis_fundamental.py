from __future__ import annotations

from datetime import date
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


def _resp(body):
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = body
    m.text = str(body)
    m.headers = {}
    return m


def test_get_fundamental_parses_inquire_price_and_finance_ratio(monkeypatch):
    c = _make_client()
    calls = []

    def fake_request(method, url, **kwargs):
        calls.append((url, kwargs))
        if url.endswith("/uapi/domestic-stock/v1/quotations/inquire-price"):
            return _resp(
                {
                    "rt_cd": "0",
                    "msg_cd": "MAAP0",
                    "msg1": "ok",
                    "output": {
                        "stck_prpr": "70000",
                        "per": "12.30",
                        "pbr": "1.40",
                        "eps": "5000",
                        "hts_avls": "400000000",
                        "lstn_stcn": "5969782550",
                    },
                }
            )
        return _resp(
            {
                "rt_cd": "0",
                "msg_cd": "MAAP0",
                "msg1": "ok",
                "output": [
                    {
                        "data_rank": "1",
                        "mksc_shrn_iscd": "005930",
                        "hts_kor_isnm": "삼성전자",
                        "stck_prpr": "70000",
                        "sale_totl_rate": "10.1",
                        "sale_ntin_rate": "8.2",
                        "lblt_rate": "30.0",
                        "grs": "3.3",
                        "bsop_prfi_inrt": "4.4",
                    }
                ],
            }
        )

    monkeypatch.setattr(kc.requests, "request", fake_request)

    result = c.get_fundamental("005930")

    assert calls[0][0].endswith("/uapi/domestic-stock/v1/quotations/inquire-price")
    assert calls[0][1]["headers"]["tr_id"] == "FHKST01010100"
    assert calls[0][1]["params"] == {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": "005930"}
    assert calls[1][0].endswith("/uapi/domestic-stock/v1/ranking/finance-ratio")
    assert calls[1][1]["headers"]["tr_id"] == "FHPST01750000"
    assert calls[1][1]["params"]["fid_cond_scr_div_code"] == "20175"
    assert result["symbol"] == "005930"
    assert result["price"] == 70000.0
    assert result["per"] == 12.3
    assert result["pbr"] == 1.4
    assert result["eps"] == 5000.0
    assert result["market_cap"] == 400000000.0
    assert result["listed_shares"] == 5969782550
    assert result["finance_ratio"]["sale_totl_rate"] == 10.1
    assert result["finance_ratio"]["lblt_rate"] == 30.0


def test_get_finance_ratio_rank_uses_official_defaults(monkeypatch):
    c = _make_client()
    calls = []
    monkeypatch.setattr(kc, "_today_kst", lambda: date(2026, 6, 12))

    def fake_request(method, url, **kwargs):
        calls.append(kwargs)
        return _resp(
            {
                "rt_cd": "0",
                "msg_cd": "MAAP0",
                "msg1": "ok",
                "output": {"data_rank": "2", "mksc_shrn_iscd": "000660", "hts_kor_isnm": "SK하이닉스"},
            }
        )

    monkeypatch.setattr(kc.requests, "request", fake_request)

    rows = c.get_finance_ratio_rank(limit=1)

    params = calls[0]["params"]
    assert params["fid_input_iscd"] == "0000"
    assert params["fid_input_option_1"] == "2025"
    assert params["fid_input_option_2"] == "3"
    assert params["fid_rank_sort_cls_code"] == "7"
    assert rows[0]["symbol"] == "000660"
    assert rows[0]["rank"] == 2


def test_get_fundamental_returns_empty_on_price_error(monkeypatch):
    c = _make_client()
    monkeypatch.setattr(
        kc.requests,
        "request",
        lambda *args, **kwargs: _resp({"rt_cd": "1", "msg_cd": "ERR", "msg1": "fail"}),
    )

    assert c.get_fundamental("005930") == {}


def test_get_fundamental_validates_symbol_and_rank_params():
    c = _make_client()
    with pytest.raises(ValueError, match="symbol"):
        c.get_fundamental("")
    with pytest.raises(ValueError, match="market_code"):
        c.get_finance_ratio_rank(market_code="005930")
    with pytest.raises(ValueError, match="quarter"):
        c.get_finance_ratio_rank(quarter="9")
