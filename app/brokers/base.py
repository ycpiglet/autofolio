from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.common.enums import OrderStatus, OrderType, Side


@dataclass(frozen=True)
class PriceQuote:
    symbol: str
    price: float


@dataclass(frozen=True)
class OrderRequest:
    symbol: str
    side: Side
    order_type: OrderType
    quantity: int
    price: float | None = None


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
