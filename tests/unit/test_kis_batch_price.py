from unittest.mock import MagicMock
import pytest
import app.brokers.kis.kis_client as kc
from app.brokers.kis.kis_client import KisClient
from app.brokers.base import PriceQuote
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


def _resp(body):
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = body
    m.text = str(body)
    m.headers = {}
    return m


def test_get_prices_batch_returns_dict(monkeypatch):
    c = _make_client()
    calls = []

    def fake_request(*args, **kwargs):
        calls.append(kwargs)
        return _resp({
            "rt_cd": "0",
            "msg_cd": "MAAP0",
            "msg1": "ok",
            "output": [
                {"inter_shrn_iscd": "005930", "inter2_prpr": "303000"},
                {"inter_shrn_iscd": "069500", "inter2_prpr": "123000"},
                {"inter_shrn_iscd": "000660", "inter2_prpr": "200000"},
            ],
        })

    monkeypatch.setattr(kc.requests, "request", fake_request)
    result = c.get_prices_batch(["005930", "069500", "000660"])
    assert result == {"005930": 303000.0, "069500": 123000.0, "000660": 200000.0}
    assert len(calls) == 1
    assert calls[0]["headers"]["tr_id"] == "FHKST11300006"
    assert calls[0]["params"]["FID_INPUT_ISCD_1"] == "005930"
    assert calls[0]["params"]["FID_INPUT_ISCD_3"] == "000660"
    assert c._last_batch_price_stats == {
        "symbols": 3,
        "batch_calls": 1,
        "single_fallback_calls": 0,
        "saved_calls": 2,
    }


def test_get_prices_batch_handles_partial_failure(monkeypatch):
    from app.common.errors import BrokerError
    c = _make_client()

    monkeypatch.setattr(
        kc.requests,
        "request",
        lambda *args, **kwargs: _resp({
            "rt_cd": "0",
            "msg_cd": "MAAP0",
            "msg1": "ok",
            "output": [{"inter_shrn_iscd": "005930", "inter2_prpr": "100000"}],
        }),
    )

    def fake_get_price(symbol):
        if symbol == "INVALID":
            raise BrokerError("not found")
        return PriceQuote(symbol=symbol, price=100000.0)

    monkeypatch.setattr(c, "get_current_price", fake_get_price)
    result = c.get_prices_batch(["005930", "INVALID", "069500"])
    assert "005930" in result
    assert "069500" in result
    assert "INVALID" not in result
    assert c._last_batch_price_stats["single_fallback_calls"] == 2


def test_get_prices_batch_empty_list():
    c = _make_client()
    result = c.get_prices_batch([])
    assert result == {}


def test_get_prices_batch_chunks_at_kis_limit(monkeypatch):
    c = _make_client()
    calls = []

    def fake_request(*args, **kwargs):
        calls.append(kwargs)
        output = [
            {"inter_shrn_iscd": symbol, "inter2_prpr": "1000"}
            for key, symbol in sorted(kwargs["params"].items())
            if key.startswith("FID_INPUT_ISCD_")
        ]
        return _resp({"rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok", "output": output})

    monkeypatch.setattr(kc.requests, "request", fake_request)

    symbols = [f"{i:06d}" for i in range(31)]
    result = c.get_prices_batch(symbols)

    assert len(result) == 31
    assert len(calls) == 2
    assert len([k for k in calls[0]["params"] if k.startswith("FID_INPUT_ISCD_")]) == 30
    assert calls[1]["params"]["FID_INPUT_ISCD_1"] == "000030"
    assert c._last_batch_price_stats["batch_calls"] == 2


@pytest.mark.parametrize("size,expected_calls", [(1, 1), (30, 1), (31, 2)])
def test_get_prices_batch_chunk_boundaries(monkeypatch, size, expected_calls):
    c = _make_client()
    calls = []

    def fake_request(*args, **kwargs):
        calls.append(kwargs)
        output = [
            {"inter_shrn_iscd": symbol, "inter2_prpr": "1000"}
            for key, symbol in sorted(kwargs["params"].items())
            if key.startswith("FID_INPUT_ISCD_")
        ]
        return _resp({"rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok", "output": output})

    monkeypatch.setattr(kc.requests, "request", fake_request)

    c.get_prices_batch([f"{i:06d}" for i in range(size)])

    assert len(calls) == expected_calls


def test_get_prices_batch_rejects_non_positive_batch_size():
    c = _make_client()
    with pytest.raises(ValueError, match="batch_size"):
        c.get_prices_batch(["005930"], batch_size=0)
