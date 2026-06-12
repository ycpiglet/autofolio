from __future__ import annotations

from unittest.mock import MagicMock

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


def test_get_index_price_sends_official_params_and_parses(monkeypatch):
    c = _make_client()
    calls = []

    def fake_request(*args, **kwargs):
        calls.append(kwargs)
        return _resp(
            {
                "rt_cd": "0",
                "msg_cd": "MAAP0",
                "msg1": "ok",
                "output": {
                    "bstp_nmix_prpr": "2800.12",
                    "bstp_nmix_prdy_vrss": "12.34",
                    "prdy_vrss_sign": "2",
                    "bstp_nmix_prdy_ctrt": "0.44",
                    "acml_vol": "123456",
                },
            }
        )

    monkeypatch.setattr(kc.requests, "request", fake_request)

    result = c.get_index_price("0001")

    assert calls[0]["headers"]["tr_id"] == "FHPUP02100000"
    assert calls[0]["params"] == {"FID_COND_MRKT_DIV_CODE": "U", "FID_INPUT_ISCD": "0001"}
    assert result["index_code"] == "0001"
    assert result["price"] == 2800.12
    assert result["change"] == 12.34
    assert result["change_rate"] == 0.44
    assert result["volume"] == 123456


def test_get_index_price_accepts_named_constant(monkeypatch):
    c = _make_client()
    calls = []
    monkeypatch.setattr(
        kc.requests,
        "request",
        lambda *args, **kwargs: calls.append(kwargs)
        or _resp({"rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok", "output": {"bstp_nmix_prpr": "900"}}),
    )

    result = c.get_index_price("KOSDAQ")

    assert calls[0]["params"]["FID_INPUT_ISCD"] == "1001"
    assert result["index_code"] == "1001"


def test_get_index_price_returns_empty_on_broker_error(monkeypatch):
    c = _make_client()
    monkeypatch.setattr(
        kc.requests,
        "request",
        lambda *args, **kwargs: _resp({"rt_cd": "1", "msg_cd": "ERR", "msg1": "fail"}),
    )

    assert c.get_index_price("0001") == {}
