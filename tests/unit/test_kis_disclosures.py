from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

import pytest

import app.brokers.kis.kis_client as kc
from app.brokers.kis.kis_client import KisClient, classify_disclosure_title
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


def test_get_disclosures_sends_official_news_title_params_and_classifies(monkeypatch):
    c = _make_client()
    calls = []
    monkeypatch.setattr(kc, "_today_kst", lambda: date(2026, 6, 12))

    def fake_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return _resp(
            {
                "rt_cd": "0",
                "msg_cd": "MAAP0",
                "msg1": "ok",
                "output": [
                    {
                        "cntt_usiq_srno": "123",
                        "news_ofer_entp_code": "2",
                        "data_dt": "20260612",
                        "data_tm": "091500",
                        "hts_pbnt_titl_cntt": "삼성전자 유상증자 결정",
                        "news_lrdv_code": "01",
                        "dorg": "KRX",
                        "iscd1": "005930",
                    }
                ],
            }
        )

    monkeypatch.setattr(kc.requests, "request", fake_request)

    rows = c.get_disclosures("005930", days=1)

    method, url, kwargs = calls[0]
    assert method == "GET"
    assert url.endswith("/uapi/domestic-stock/v1/quotations/news-title")
    assert kwargs["headers"]["tr_id"] == "FHKST01011800"
    assert kwargs["params"]["FID_INPUT_ISCD"] == "005930"
    assert kwargs["params"]["FID_INPUT_DATE_1"] == "20260612"
    assert rows[0]["title"] == "삼성전자 유상증자 결정"
    assert rows[0]["category"] == "주요사항보고서"
    assert rows[0]["severity"] == "HIGH"
    assert rows[0]["block_order"] is True
    assert rows[0]["matched_keywords"] == ["유상증자"]


def test_get_disclosures_queries_multiple_days_and_dedupes(monkeypatch):
    c = _make_client()
    calls = []
    monkeypatch.setattr(kc, "_today_kst", lambda: date(2026, 6, 12))

    def fake_request(method, url, **kwargs):
        calls.append(kwargs["params"]["FID_INPUT_DATE_1"])
        return _resp(
            {
                "rt_cd": "0",
                "msg_cd": "MAAP0",
                "msg1": "ok",
                "output": {"cntt_usiq_srno": "1", "hts_pbnt_titl_cntt": "분기보고서 제출", "iscd1": "005930"},
            }
        )

    monkeypatch.setattr(kc.requests, "request", fake_request)

    rows = c.get_disclosures("005930", days=2)

    assert calls == ["20260612", "20260611"]
    assert len(rows) == 2
    assert all(row["category"] == "정기공시" for row in rows)


def test_get_disclosures_returns_empty_on_broker_error(monkeypatch):
    c = _make_client()
    monkeypatch.setattr(
        kc.requests,
        "request",
        lambda *args, **kwargs: _resp({"rt_cd": "1", "msg_cd": "ERR", "msg1": "fail"}),
    )

    assert c.get_disclosures("005930") == []


def test_classify_disclosure_title_categories():
    assert classify_disclosure_title("반기보고서 제출")["category"] == "정기공시"
    caution = classify_disclosure_title("단일판매 공급계약 체결")
    assert caution["category"] == "수시공시"
    assert caution["severity"] == "MEDIUM"
    high = classify_disclosure_title("상장폐지 관련 거래정지")
    assert high["block_order"] is True


def test_get_disclosures_validates_inputs():
    c = _make_client()
    with pytest.raises(ValueError, match="symbol"):
        c.get_disclosures("")
    with pytest.raises(ValueError, match="days"):
        c.get_disclosures("005930", days=0)
