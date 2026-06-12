from __future__ import annotations

import asyncio
import base64
import inspect
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable

import requests
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from app.common.errors import BrokerError, ConfigurationError
from app.config.settings import Settings, settings

logger = logging.getLogger(__name__)

WS_APPROVAL_PATH = "/oauth2/Approval"
WS_API_PATH = "/tryitout"

TR_REALTIME_TRADE = "H0STCNT0"
TR_ORDER_BOOK = "H0STASP0"
TR_EXECUTION_NOTICE_PROD = "H0STCNI0"
TR_EXECUTION_NOTICE_PAPER = "H0STCNI9"


def _as_int(value: Any, default: int = 0) -> int:
    if value in (None, ""):
        return default
    return int(float(value))


def _as_float(value: Any, default: float | None = None) -> float | None:
    if value in (None, ""):
        return default
    return float(value)


@dataclass(frozen=True)
class KisWsSubscription:
    tr_id: str
    tr_key: str
    tr_type: str = "1"


@dataclass(frozen=True)
class KisWsSystemMessage:
    tr_id: str
    tr_key: str | None = None
    ok: bool = False
    message: str | None = None
    is_pingpong: bool = False
    is_unsubscribe: bool = False
    encrypt: str | None = None
    key: str | None = None
    iv: str | None = None
    raw: dict = field(default_factory=dict)


@dataclass(frozen=True)
class KisRealtimeTrade:
    symbol: str
    time: str
    price: float
    change_sign: str
    change: float | None
    change_rate: float | None
    open: float | None
    high: float | None
    low: float | None
    ask_price: float | None
    bid_price: float | None
    volume: int
    accumulated_volume: int
    raw: list[str]


@dataclass(frozen=True)
class KisOrderBookLevel:
    level: int
    ask_price: float | None
    ask_quantity: int
    bid_price: float | None
    bid_quantity: int


@dataclass(frozen=True)
class KisRealtimeQuote:
    symbol: str
    time: str
    levels: list[KisOrderBookLevel]
    total_ask_quantity: int
    total_bid_quantity: int
    raw: list[str]


@dataclass(frozen=True)
class KisExecutionNotice:
    customer_id: str
    account_no: str
    order_no: str
    original_order_no: str
    side: str
    symbol: str
    quantity: int
    price: float | None
    time: str
    rejected: bool
    fill_yn: str
    accepted: bool
    order_quantity: int
    name: str
    order_price: float | None
    raw: list[str]

    @property
    def is_fill(self) -> bool:
        return self.fill_yn == "2"


KisRealtimeEvent = KisWsSystemMessage | KisRealtimeTrade | KisRealtimeQuote | KisExecutionNotice


def execution_notice_tr_id(kis_env: str) -> str:
    return TR_EXECUTION_NOTICE_PAPER if (kis_env or "").lower() == "paper" else TR_EXECUTION_NOTICE_PROD


def build_subscribe_message(
    tr_id: str,
    tr_key: str,
    approval_key: str,
    *,
    tr_type: str = "1",
    custtype: str = "P",
) -> dict:
    if not tr_id:
        raise ValueError("tr_id is required.")
    if not tr_key:
        raise ValueError("tr_key is required.")
    if not approval_key:
        raise ValueError("approval_key is required.")
    return {
        "header": {
            "approval_key": approval_key,
            "custtype": custtype,
            "tr_type": tr_type,
            "content-type": "utf-8",
        },
        "body": {"input": {"tr_id": tr_id, "tr_key": tr_key}},
    }


def get_approval_key(app_settings: Settings = settings, *, timeout: int = 10) -> str:
    if not app_settings.kis_base_url:
        raise ConfigurationError("KIS_BASE_URL is required for WebSocket approval key.")
    if not app_settings.kis_app_key or not app_settings.kis_app_secret:
        raise ConfigurationError("KIS_APP_KEY and KIS_APP_SECRET are required for WebSocket approval key.")

    url = app_settings.kis_base_url.rstrip("/") + WS_APPROVAL_PATH
    payload = {
        "grant_type": "client_credentials",
        "appkey": app_settings.kis_app_key,
        "secretkey": app_settings.kis_app_secret,
    }
    headers = {"content-type": "application/json"}
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        raise BrokerError(f"KIS WebSocket approval request error: {type(exc).__name__}: {exc}") from exc

    if response.status_code >= 400:
        raise BrokerError(f"KIS WebSocket approval failed: {response.status_code} {response.text}")
    data = response.json()
    approval_key = data.get("approval_key")
    if not approval_key:
        raise BrokerError(f"KIS WebSocket approval response missing approval_key: {data}")
    return approval_key


def parse_system_message(raw: str) -> KisWsSystemMessage:
    data = json.loads(raw)
    header = data.get("header") or {}
    body = data.get("body") or {}
    tr_id = str(header.get("tr_id") or "")
    if tr_id == "PINGPONG":
        return KisWsSystemMessage(tr_id=tr_id, is_pingpong=True, raw=data)

    msg = body.get("msg1")
    output = body.get("output") or {}
    return KisWsSystemMessage(
        tr_id=tr_id,
        tr_key=header.get("tr_key"),
        ok=str(body.get("rt_cd")) == "0",
        message=msg,
        is_unsubscribe=bool(isinstance(msg, str) and msg.startswith("UNSUB")),
        encrypt=header.get("encrypt"),
        key=output.get("key"),
        iv=output.get("iv"),
        raw=data,
    )


def aes_cbc_base64_decrypt(key: str, iv: str, cipher_text: str) -> str:
    decryptor = Cipher(algorithms.AES(key.encode("utf-8")), modes.CBC(iv.encode("utf-8"))).decryptor()
    padded = decryptor.update(base64.b64decode(cipher_text)) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    return (unpadder.update(padded) + unpadder.finalize()).decode("utf-8")


def parse_trade_payload(fields: list[str]) -> KisRealtimeTrade:
    return KisRealtimeTrade(
        symbol=fields[0] if len(fields) > 0 else "",
        time=fields[1] if len(fields) > 1 else "",
        price=float(fields[2] or 0) if len(fields) > 2 else 0.0,
        change_sign=fields[3] if len(fields) > 3 else "",
        change=_as_float(fields[4] if len(fields) > 4 else None),
        change_rate=_as_float(fields[5] if len(fields) > 5 else None),
        open=_as_float(fields[7] if len(fields) > 7 else None),
        high=_as_float(fields[8] if len(fields) > 8 else None),
        low=_as_float(fields[9] if len(fields) > 9 else None),
        ask_price=_as_float(fields[10] if len(fields) > 10 else None),
        bid_price=_as_float(fields[11] if len(fields) > 11 else None),
        volume=_as_int(fields[12] if len(fields) > 12 else None),
        accumulated_volume=_as_int(fields[13] if len(fields) > 13 else None),
        raw=fields,
    )


def parse_quote_payload(fields: list[str]) -> KisRealtimeQuote:
    levels: list[KisOrderBookLevel] = []
    for i in range(10):
        levels.append(
            KisOrderBookLevel(
                level=i + 1,
                ask_price=_as_float(fields[3 + i] if len(fields) > 3 + i else None),
                ask_quantity=_as_int(fields[23 + i] if len(fields) > 23 + i else None),
                bid_price=_as_float(fields[13 + i] if len(fields) > 13 + i else None),
                bid_quantity=_as_int(fields[33 + i] if len(fields) > 33 + i else None),
            )
        )
    return KisRealtimeQuote(
        symbol=fields[0] if len(fields) > 0 else "",
        time=fields[1] if len(fields) > 1 else "",
        levels=levels,
        total_ask_quantity=_as_int(fields[43] if len(fields) > 43 else None),
        total_bid_quantity=_as_int(fields[44] if len(fields) > 44 else None),
        raw=fields,
    )


def parse_execution_notice_payload(fields: list[str]) -> KisExecutionNotice:
    side_code = fields[4] if len(fields) > 4 else ""
    side = {"01": "SELL", "02": "BUY"}.get(side_code, side_code)
    return KisExecutionNotice(
        customer_id=fields[0] if len(fields) > 0 else "",
        account_no=fields[1] if len(fields) > 1 else "",
        order_no=fields[2] if len(fields) > 2 else "",
        original_order_no=fields[3] if len(fields) > 3 else "",
        side=side,
        symbol=fields[8] if len(fields) > 8 else "",
        quantity=_as_int(fields[9] if len(fields) > 9 else None),
        price=_as_float(fields[10] if len(fields) > 10 else None),
        time=fields[11] if len(fields) > 11 else "",
        rejected=(fields[12] if len(fields) > 12 else "") == "Y",
        fill_yn=fields[13] if len(fields) > 13 else "",
        accepted=(fields[14] if len(fields) > 14 else "") == "Y",
        order_quantity=_as_int(fields[16] if len(fields) > 16 else None),
        name=fields[24] if len(fields) > 24 else "",
        order_price=_as_float(fields[25] if len(fields) > 25 else None),
        raw=fields,
    )


def parse_realtime_message(
    raw: str,
    *,
    decrypt: Callable[[str, str, str], str] | None = None,
    decrypt_keys: dict[str, tuple[str, str]] | None = None,
) -> KisRealtimeEvent:
    if not raw:
        raise ValueError("raw message is empty.")
    if raw[0] not in ("0", "1"):
        return parse_system_message(raw)

    parts = raw.split("|", 3)
    if len(parts) < 4:
        raise ValueError(f"KIS realtime message missing payload: {raw!r}")

    tr_id = parts[1]
    payload = parts[3]
    if raw[0] == "1":
        key_iv = (decrypt_keys or {}).get(tr_id)
        if key_iv is not None:
            fn = decrypt or aes_cbc_base64_decrypt
            payload = fn(key_iv[0], key_iv[1], payload)

    fields = payload.split("^")
    if tr_id == TR_REALTIME_TRADE:
        return parse_trade_payload(fields)
    if tr_id == TR_ORDER_BOOK:
        return parse_quote_payload(fields)
    if tr_id in (TR_EXECUTION_NOTICE_PROD, TR_EXECUTION_NOTICE_PAPER):
        return parse_execution_notice_payload(fields)
    return KisWsSystemMessage(tr_id=tr_id, ok=True, message="unhandled realtime tr_id", raw={"fields": fields})


class KisWebSocketClient:
    def __init__(
        self,
        app_settings: Settings = settings,
        *,
        approval_key: str | None = None,
        websocket_connect: Callable[..., Any] | None = None,
        notifier: Any | None = None,
        fallback_client: Any | None = None,
        max_reconnects: int = 3,
        reconnect_sleep: float = 1.0,
    ) -> None:
        self.settings = app_settings
        self.approval_key = approval_key
        self.websocket_connect = websocket_connect
        self.notifier = notifier
        self.fallback_client = fallback_client
        self.max_reconnects = max_reconnects
        self.reconnect_sleep = reconnect_sleep
        self.subscriptions: list[KisWsSubscription] = []
        self.decrypt_keys: dict[str, tuple[str, str]] = {}
        self.latest_prices: dict[str, float] = {}

    @property
    def websocket_url(self) -> str:
        if not self.settings.kis_ws_url:
            raise ConfigurationError("KIS_WS_URL is required for WebSocket connection.")
        return self.settings.kis_ws_url.rstrip("/") + WS_API_PATH

    def subscribe_current_price(self, symbols: str | list[str]) -> None:
        for symbol in _to_list(symbols):
            self.subscriptions.append(KisWsSubscription(TR_REALTIME_TRADE, symbol))

    def subscribe_order_book(self, symbols: str | list[str]) -> None:
        for symbol in _to_list(symbols):
            self.subscriptions.append(KisWsSubscription(TR_ORDER_BOOK, symbol))

    def subscribe_execution_notice(self, hts_id: str | None = None) -> None:
        tr_key = hts_id or self.settings.kis_hts_id
        if not tr_key:
            raise ConfigurationError("KIS_HTS_ID is required for execution notice subscription.")
        self.subscriptions.append(KisWsSubscription(execution_notice_tr_id(self.settings.kis_env), tr_key))

    def get_price(self, symbol: str) -> float | None:
        if symbol in self.latest_prices:
            return self.latest_prices[symbol]
        if self.fallback_client is None:
            return None
        quote = self.fallback_client.get_current_price(symbol)
        return getattr(quote, "price", None)

    async def run(
        self,
        on_event: Callable[[KisRealtimeEvent], Any] | None = None,
        *,
        max_messages: int | None = None,
    ) -> None:
        if len(self.subscriptions) > 40:
            raise ValueError("KIS WebSocket supports at most 40 subscriptions per connection.")
        if not self.subscriptions:
            raise ValueError("At least one subscription is required.")
        if not self.approval_key:
            self.approval_key = get_approval_key(self.settings)

        attempts = 0
        while attempts <= self.max_reconnects:
            try:
                await self._run_connection(on_event=on_event, max_messages=max_messages)
                return
            except Exception:
                attempts += 1
                if attempts > self.max_reconnects:
                    raise
                logger.warning("KIS WebSocket connection failed; reconnecting (%s/%s)", attempts, self.max_reconnects)
                if self.reconnect_sleep > 0:
                    await asyncio.sleep(self.reconnect_sleep)

    async def _run_connection(
        self,
        *,
        on_event: Callable[[KisRealtimeEvent], Any] | None,
        max_messages: int | None,
    ) -> None:
        connector = self.websocket_connect or _default_websocket_connect
        async with connector(self.websocket_url, ping_interval=None) as ws:
            for sub in self.subscriptions:
                msg = build_subscribe_message(
                    sub.tr_id,
                    sub.tr_key,
                    self.approval_key or "",
                    tr_type=sub.tr_type,
                )
                await ws.send(json.dumps(msg, ensure_ascii=False))

            seen = 0
            async for raw in ws:
                event = self.handle_raw_message(raw)
                if isinstance(event, KisWsSystemMessage) and event.is_pingpong and hasattr(ws, "pong"):
                    await ws.pong(raw)
                if on_event is not None:
                    await _emit(on_event, event)
                seen += 1
                if max_messages is not None and seen >= max_messages:
                    return

    def handle_raw_message(self, raw: str) -> KisRealtimeEvent:
        event = parse_realtime_message(raw, decrypt_keys=self.decrypt_keys)
        if isinstance(event, KisWsSystemMessage) and event.key and event.iv:
            self.decrypt_keys[event.tr_id] = (event.key, event.iv)
        elif isinstance(event, KisRealtimeTrade):
            self.latest_prices[event.symbol] = event.price
        elif isinstance(event, KisExecutionNotice) and event.is_fill:
            self._notify_fill(event)
        return event

    def _notify_fill(self, notice: KisExecutionNotice) -> None:
        if self.notifier is None:
            return
        if hasattr(self.notifier, "send_fill"):
            self.notifier.send_fill(notice.symbol, notice.side, notice.quantity, notice.price)
            return
        if hasattr(self.notifier, "send"):
            self.notifier.send(
                f"Fill: {notice.symbol} {notice.side} {notice.quantity} @ {notice.price or ''}".strip()
            )


def _to_list(value: str | list[str]) -> list[str]:
    return [value] if isinstance(value, str) else list(value)


def _default_websocket_connect(*args: Any, **kwargs: Any) -> Any:
    try:
        import websockets
    except ImportError as exc:
        raise ConfigurationError("Install websockets to use KIS WebSocket runtime.") from exc
    return websockets.connect(*args, **kwargs)


async def _emit(callback: Callable[[KisRealtimeEvent], Any], event: KisRealtimeEvent) -> None:
    result = callback(event)
    if inspect.isawaitable(result):
        await result
