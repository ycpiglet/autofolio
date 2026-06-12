from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import app.brokers.kis.kis_client as kc
from app.brokers.kis.kis_client import KisClient, estimate_order_book_slippage
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


def test_get_order_book_sends_official_params_and_parses_10_levels(monkeypatch):
    c = _make_client()
    calls = []

    output1 = {
        "stck_shrn_iscd": "005930",
        "aspr_acpt_hour": "093001",
        "stck_prpr": "70000",
        "antc_cnpr": "70100",
        "antc_vol": "12345",
        "total_askp_rsqn": "1111",
        "total_bidp_rsqn": "2222",
    }
    for level in range(1, 11):
        output1[f"askp{level}"] = str(70100 + level * 100)
        output1[f"bidp{level}"] = str(70000 - level * 100)
        output1[f"askp_rsqn{level}"] = str(level * 10)
        output1[f"bidp_rsqn{level}"] = str(level * 20)

    def fake_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return _resp({"rt_cd": "0", "msg_cd": "MAAP0", "msg1": "ok", "output1": output1, "output2": []})

    monkeypatch.setattr(kc.requests, "request", fake_request)

    result = c.get_order_book("005930")

    method, url, kwargs = calls[0]
    assert method == "GET"
    assert url.endswith("/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn")
    assert kwargs["headers"]["tr_id"] == "FHKST01010200"
    assert kwargs["params"] == {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": "005930"}
    assert result["symbol"] == "005930"
    assert result["accepted_at"] == "093001"
    assert result["current_price"] == 70000.0
    assert result["expected_price"] == 70100.0
    assert result["expected_volume"] == 12345
    assert result["total_ask_quantity"] == 1111
    assert result["total_bid_quantity"] == 2222
    assert len(result["levels"]) == 10
    assert result["levels"][0] == {
        "level": 1,
        "ask_price": 70200.0,
        "ask_quantity": 10,
        "bid_price": 69900.0,
        "bid_quantity": 20,
    }
    assert result["levels"][-1]["level"] == 10
    assert result["levels"][-1]["ask_quantity"] == 100


def test_get_order_book_returns_empty_on_broker_error(monkeypatch):
    c = _make_client()
    monkeypatch.setattr(
        kc.requests,
        "request",
        lambda *args, **kwargs: _resp({"rt_cd": "1", "msg_cd": "ERR", "msg1": "fail"}),
    )

    assert c.get_order_book("005930") == {}


def test_get_order_book_validates_symbol_and_market():
    c = _make_client()
    with pytest.raises(ValueError, match="symbol"):
        c.get_order_book("")
    with pytest.raises(ValueError, match="market"):
        c.get_order_book("005930", market="BAD")


def test_estimate_order_book_slippage_for_buy_depth():
    levels = [
        {"ask_price": 100, "ask_quantity": 10, "bid_price": 99, "bid_quantity": 5},
        {"ask_price": 105, "ask_quantity": 20, "bid_price": 98, "bid_quantity": 10},
    ]

    result = estimate_order_book_slippage(levels, "BUY", 15, reference_price=100)

    assert result["side"] == "BUY"
    assert result["filled_quantity"] == 15
    assert result["unfilled_quantity"] == 0
    assert result["average_price"] == pytest.approx(101.6667)
    assert result["notional"] == 1525.0
    assert result["slippage_per_share"] == pytest.approx(1.6667)
    assert result["slippage_rate"] == pytest.approx(1.6667)


def test_estimate_order_book_slippage_for_sell_partial_fill():
    levels = [
        {"ask_price": 101, "ask_quantity": 10, "bid_price": 99, "bid_quantity": 5},
        {"ask_price": 102, "ask_quantity": 10, "bid_price": 98, "bid_quantity": 10},
    ]

    result = estimate_order_book_slippage(levels, "SELL", 20, reference_price=100)

    assert result["side"] == "SELL"
    assert result["filled_quantity"] == 15
    assert result["unfilled_quantity"] == 5
    assert result["average_price"] == pytest.approx(98.3333)
    assert result["slippage_per_share"] == pytest.approx(1.6667)


def test_estimate_order_book_slippage_validates_inputs():
    with pytest.raises(ValueError, match="quantity"):
        estimate_order_book_slippage([], "BUY", 0)
    with pytest.raises(ValueError, match="side"):
        estimate_order_book_slippage([], "HOLD", 1)
