from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping, Protocol

from app.common.enums import OrderStatus, OrderType, Side


@dataclass(frozen=True)
class PriceQuote:
    symbol: str
    price: float
    as_of: datetime | None = None
    source: str | None = None


@dataclass(frozen=True)
class OrderRequest:
    symbol: str
    side: Side
    order_type: OrderType
    quantity: int
    price: float | None = None
    order_session: str = "REGULAR"
    sell_type: str = "01"
    market: str = "KRX"
    product_type: str = "EQUITY"
    currency: str = "KRW"
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OrderResult:
    broker_order_id: str
    status: OrderStatus
    filled_price: float | None = None
    filled_quantity: int = 0
    message: str | None = None


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: int
    avg_price: float | None = None
    market: str = "KRX"
    currency: str = "KRW"
    fx_rate: float | None = None


class BrokerClient(Protocol):
    def get_current_price(self, symbol: str) -> PriceQuote:
        ...

    def place_order(self, request: OrderRequest) -> OrderResult:
        ...

    def cancel_order(self, broker_order_id: str) -> OrderResult:
        ...

    def get_order_status(self, broker_order_id: str) -> OrderResult:
        ...

    def get_positions(self) -> list[Position]:
        ...
