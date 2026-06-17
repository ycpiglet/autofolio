from __future__ import annotations

import pytest

import app.brokers.kis.kis_client as kc
from app.brokers.base import OrderRequest
from app.brokers.kis.kis_client import KisClient
from app.common.enums import OrderStatus, OrderType, Side
from app.common.errors import BrokerError
from app.config.settings import Settings


class FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code
        self.headers = {}
        self.text = str(payload)

    def json(self) -> dict:
        return self._payload


def _ok(output=None):
    return FakeResponse({"rt_cd": "0", "msg_cd": "OK", "msg1": "정상처리", "output": output or {}})


def _client(monkeypatch, responder, *, env: str = "paper"):
    calls: list[dict] = []

    def fake_request(method, url, headers=None, params=None, json=None, timeout=None):
        calls.append({"method": method, "url": url, "headers": headers or {}, "params": params, "json": json})
        return responder(calls[-1])

    monkeypatch.setattr(kc.requests, "request", fake_request)
    client = KisClient(
        Settings(
            kis_env=env,
            kis_app_key="app-key",
            kis_app_secret="app-secret",
            kis_account_no="12345678",
            kis_account_product_code="01",
            kis_base_url="https://paper.example:29443",
            kis_token_path="/oauth2/tokenP",
        )
    )
    monkeypatch.setattr(client.auth, "get_access_token", lambda: "token")
    return client, calls


def test_after_close_order_maps_ord_dvsn_06(monkeypatch):
    client, calls = _client(monkeypatch, lambda call: _ok({"KRX_FWDG_ORD_ORGNO": "06010", "ODNO": "A1"}))

    result = client.place_order(
        OrderRequest(
            symbol="005930",
            side=Side.BUY,
            order_type=OrderType.MOC,
            quantity=1,
            order_session="AFTER_CLOSE_SINGLE",
        )
    )

    assert result.status == OrderStatus.PENDING
    assert calls[0]["json"]["ORD_DVSN"] == "06"
    assert calls[0]["json"]["ORD_UNPR"] == "0"


def test_short_sell_sets_sll_type_05_in_paper(monkeypatch):
    client, calls = _client(monkeypatch, lambda call: _ok({"KRX_FWDG_ORD_ORGNO": "06010", "ODNO": "S1"}))

    client.place_order(
        OrderRequest(
            symbol="005930",
            side=Side.SELL,
            order_type=OrderType.LIMIT,
            quantity=1,
            price=70_000,
            sell_type="05",
        )
    )

    assert calls[0]["json"]["SLL_TYPE"] == "05"


def test_r3_domestic_prod_order_requires_explicit_hardguard(monkeypatch):
    client, _calls = _client(monkeypatch, lambda call: _ok({"ODNO": "P1"}), env="prod")

    with pytest.raises(BrokerError, match="R3 domestic"):
        client.place_order(
            OrderRequest(
                symbol="005930",
                side=Side.SELL,
                order_type=OrderType.LIMIT,
                quantity=1,
                price=70_000,
                sell_type="05",
            )
        )


def test_overseas_paper_order_builds_payload(monkeypatch):
    client, calls = _client(monkeypatch, lambda call: _ok({"ODNO": "OV1"}))

    result = client.place_overseas_order(
        symbol="AAPL",
        market="NASD",
        side=Side.BUY,
        quantity=2,
        price=195.25,
    )

    assert result.broker_order_id == "OV1"
    assert calls[0]["url"].endswith("/uapi/overseas-stock/v1/trading/order")
    assert calls[0]["headers"]["tr_id"] == "VTTT1002U"
    body = calls[0]["json"]
    assert body["OVRS_EXCG_CD"] == "NASD"
    assert body["PDNO"] == "AAPL"
    assert body["OVRS_ORD_UNPR"] == "195.25"
    assert body["ORD_CRNCY_CD"] == "USD"


def test_overseas_prod_order_requires_explicit_hardguard(monkeypatch):
    client, _calls = _client(monkeypatch, lambda call: _ok({"ODNO": "OVP"}), env="prod")

    with pytest.raises(BrokerError, match="Overseas stock prod"):
        client.place_overseas_order(
            symbol="AAPL",
            market="NASD",
            side=Side.BUY,
            quantity=2,
            price=195.25,
        )
