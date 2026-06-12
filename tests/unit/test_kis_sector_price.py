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


def _resp(body):
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = body
    m.text = str(body)
    m.headers = {}
    return m


def test_get_sector_price_maps_alias_to_index_endpoint(monkeypatch):
    c = _make_client()
    calls = []

    def fake_request(*args, **kwargs):
        calls.append((args, kwargs))
        return _resp(
            {
                "rt_cd": "0",
                "msg_cd": "MAAP0",
                "msg1": "ok",
                "output": {
                    "bstp_nmix_prpr": "1234.56",
                    "bstp_nmix_prdy_vrss": "12.34",
                    "prdy_vrss_sign": "2",
                    "bstp_nmix_prdy_ctrt": "1.01",
                    "acml_vol": "123456",
                    "acml_tr_pbmn": "987654321",
                },
            }
        )

    monkeypatch.setattr(kc.requests, "request", fake_request)

    result = c.get_sector_price("KOSPI_ELECTRONICS")

    _, kwargs = calls[0]
    assert kwargs["headers"]["tr_id"] == "FHPUP02100000"
    assert kwargs["params"] == {"FID_COND_MRKT_DIV_CODE": "U", "FID_INPUT_ISCD": "0013"}
    assert result["sector_code"] == "0013"
    assert result["name"] == "KOSPI 전기·전자"
    assert result["price"] == 1234.56
    assert result["change_rate"] == 1.01
    assert result["trading_value"] == 987654321


def test_get_sector_price_accepts_raw_code(monkeypatch):
    c = _make_client()
    monkeypatch.setattr(
        kc.requests,
        "request",
        lambda *args, **kwargs: _resp(
            {
                "rt_cd": "0",
                "msg_cd": "MAAP0",
                "msg1": "ok",
                "output": {"bstp_nmix_prpr": "100", "bstp_nmix_prdy_ctrt": "0.1"},
            }
        ),
    )

    result = c.get_sector_price("0021")

    assert result["sector_code"] == "0021"
    assert result["name"] == "KOSPI 금융"


def test_get_sector_price_validates_code():
    c = _make_client()
    with pytest.raises(ValueError, match="sector_code"):
        c.get_sector_price("")
