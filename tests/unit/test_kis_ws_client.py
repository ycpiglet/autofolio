from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass

import pytest

import app.brokers.kis.kis_ws_client as kw
from app.brokers.kis.kis_ws_client import (
    KisExecutionNotice,
    KisRealtimeQuote,
    KisRealtimeTrade,
    KisWebSocketClient,
    build_subscribe_message,
    execution_notice_tr_id,
    get_approval_key,
    parse_realtime_message,
    parse_system_message,
)
from app.config.settings import Settings


def _settings(env: str = "paper") -> Settings:
    return Settings(
        kis_env=env,
        kis_app_key="app-key",
        kis_app_secret="app-secret",
        kis_account_no="12345678",
        kis_account_product_code="01",
        kis_base_url="https://openapivts.koreainvestment.com:29443",
        kis_ws_url="ws://ops.koreainvestment.com:31000",
        kis_token_path="/oauth2/tokenP",
        kis_hts_id="hts-user",
    )


class FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def json(self) -> dict:
        return self._payload


def test_get_approval_key_posts_official_payload(monkeypatch):
    calls = []

    def fake_post(url, data=None, headers=None, timeout=None):
        calls.append({"url": url, "data": json.loads(data), "headers": headers, "timeout": timeout})
        return FakeResponse({"approval_key": "approval-123"})

    monkeypatch.setattr(kw.requests, "post", fake_post)
    approval_key = get_approval_key(_settings(), timeout=7)

    assert approval_key == "approval-123"
    assert calls[0]["url"].endswith("/oauth2/Approval")
    assert calls[0]["data"] == {
        "grant_type": "client_credentials",
        "appkey": "app-key",
        "secretkey": "app-secret",
    }
    assert calls[0]["headers"]["content-type"] == "application/json"
    assert calls[0]["timeout"] == 7


def test_build_subscribe_message_for_trade():
    msg = build_subscribe_message("H0STCNT0", "005930", "approval-123")

    assert msg["header"]["approval_key"] == "approval-123"
    assert msg["header"]["tr_type"] == "1"
    assert msg["header"]["custtype"] == "P"
    assert msg["body"]["input"] == {"tr_id": "H0STCNT0", "tr_key": "005930"}


def test_execution_notice_tr_id_uses_paper_variant():
    assert execution_notice_tr_id("prod") == "H0STCNI0"
    assert execution_notice_tr_id("paper") == "H0STCNI9"


def test_parse_trade_message():
    fields = [""] * 46
    fields[0] = "005930"
    fields[1] = "093000"
    fields[2] = "70000"
    fields[3] = "2"
    fields[4] = "1000"
    fields[5] = "1.45"
    fields[7] = "69000"
    fields[8] = "71000"
    fields[9] = "68000"
    fields[10] = "70100"
    fields[11] = "69900"
    fields[12] = "10"
    fields[13] = "123456"

    event = parse_realtime_message("0|H0STCNT0|001|" + "^".join(fields))

    assert isinstance(event, KisRealtimeTrade)
    assert event.symbol == "005930"
    assert event.price == 70000.0
    assert event.volume == 10
    assert event.accumulated_volume == 123456


def test_parse_order_book_message():
    fields = [""] * 59
    fields[0] = "005930"
    fields[1] = "093001"
    fields[3] = "70100"
    fields[13] = "70000"
    fields[23] = "11"
    fields[33] = "22"
    fields[43] = "1111"
    fields[44] = "2222"

    event = parse_realtime_message("0|H0STASP0|001|" + "^".join(fields))

    assert isinstance(event, KisRealtimeQuote)
    assert event.symbol == "005930"
    assert event.levels[0].ask_price == 70100.0
    assert event.levels[0].ask_quantity == 11
    assert event.levels[0].bid_price == 70000.0
    assert event.levels[0].bid_quantity == 22
    assert event.total_ask_quantity == 1111
    assert event.total_bid_quantity == 2222


def test_parse_system_pingpong():
    event = parse_system_message(json.dumps({"header": {"tr_id": "PINGPONG"}}))

    assert event.is_pingpong is True
    assert event.tr_id == "PINGPONG"


def _execution_notice_payload(fill_yn: str = "2") -> str:
    fields = [""] * 26
    fields[0] = "cust-id"
    fields[1] = "12345678"
    fields[2] = "0000117057"
    fields[3] = ""
    fields[4] = "02"
    fields[8] = "005930"
    fields[9] = "1"
    fields[10] = "70500"
    fields[11] = "101010"
    fields[12] = "N"
    fields[13] = fill_yn
    fields[14] = "Y"
    fields[16] = "1"
    fields[24] = "SAMSUNG"
    fields[25] = "70500"
    return "^".join(fields)


def test_parse_encrypted_execution_notice_uses_decrypt_callback():
    event = parse_realtime_message(
        "1|H0STCNI9|001|cipher-text",
        decrypt=lambda key, iv, text: _execution_notice_payload(),
        decrypt_keys={"H0STCNI9": ("k" * 32, "i" * 16)},
    )

    assert isinstance(event, KisExecutionNotice)
    assert event.is_fill is True
    assert event.symbol == "005930"
    assert event.side == "BUY"
    assert event.quantity == 1
    assert event.price == 70500.0


class FakeNotifier:
    def __init__(self) -> None:
        self.fills = []

    def send_fill(self, symbol, side, qty, price):
        self.fills.append((symbol, side, qty, price))


def test_handle_execution_notice_notifies_fill():
    notifier = FakeNotifier()
    client = KisWebSocketClient(_settings(), approval_key="approval-123", notifier=notifier)

    event = client.handle_raw_message("0|H0STCNI9|001|" + _execution_notice_payload())

    assert isinstance(event, KisExecutionNotice)
    assert notifier.fills == [("005930", "BUY", 1, 70500.0)]


class FakeWebSocket:
    def __init__(self, messages: list[str]):
        self.messages = list(messages)
        self.sent: list[str] = []
        self.pongs: list[str] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def send(self, text: str) -> None:
        self.sent.append(text)

    async def pong(self, text: str) -> None:
        self.pongs.append(text)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.messages:
            raise StopAsyncIteration
        return self.messages.pop(0)


class FlakyConnector:
    def __init__(self, websocket: FakeWebSocket):
        self.websocket = websocket
        self.calls = 0
        self.urls: list[str] = []

    def __call__(self, url: str, **kwargs):
        self.calls += 1
        self.urls.append(url)
        if self.calls == 1:
            raise OSError("temporary network failure")
        return self.websocket


def test_run_sends_subscriptions_and_reconnects_once():
    fields = [""] * 46
    fields[0] = "005930"
    fields[1] = "093000"
    fields[2] = "70000"
    websocket = FakeWebSocket(["0|H0STCNT0|001|" + "^".join(fields)])
    connector = FlakyConnector(websocket)
    client = KisWebSocketClient(
        _settings(),
        approval_key="approval-123",
        websocket_connect=connector,
        max_reconnects=1,
        reconnect_sleep=0,
    )
    client.subscribe_current_price(["005930"])
    events = []

    asyncio.run(client.run(events.append, max_messages=1))

    assert connector.calls == 2
    assert connector.urls[-1] == "ws://ops.koreainvestment.com:31000/tryitout"
    assert len(websocket.sent) == 1
    sent = json.loads(websocket.sent[0])
    assert sent["body"]["input"] == {"tr_id": "H0STCNT0", "tr_key": "005930"}
    assert isinstance(events[0], KisRealtimeTrade)
    assert client.latest_prices["005930"] == 70000.0


@dataclass
class FakeQuote:
    price: float


class FakeFallback:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def get_current_price(self, symbol: str) -> FakeQuote:
        self.calls.append(symbol)
        return FakeQuote(81000.0)


def test_get_price_prefers_realtime_cache_then_rest_fallback():
    fallback = FakeFallback()
    client = KisWebSocketClient(_settings(), approval_key="approval-123", fallback_client=fallback)
    client.latest_prices["005930"] = 70000.0

    assert client.get_price("005930") == 70000.0
    assert client.get_price("000660") == 81000.0
    assert fallback.calls == ["000660"]


def test_subscribe_execution_notice_requires_hts_id():
    settings = Settings(kis_env="paper", kis_ws_url="ws://ops.koreainvestment.com:31000")
    client = KisWebSocketClient(settings, approval_key="approval-123")

    with pytest.raises(Exception, match="KIS_HTS_ID"):
        client.subscribe_execution_notice()
