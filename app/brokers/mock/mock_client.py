from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count
from typing import Dict

from app.brokers.base import BrokerClient, OrderRequest, OrderResult, Position, PriceQuote
from app.common.enums import OrderStatus, OrderType, Side


@dataclass
class MockBrokerClient(BrokerClient):
    prices: Dict[str, float] = field(default_factory=lambda: {
        "005930": 70000.0,
        "069500": 35000.0,
        "360750": 18000.0,
    })
    fill_limit_orders: bool = True

    def __post_init__(self) -> None:
        self._order_seq = count(1)
        self._orders: dict[str, OrderResult] = {}
        self._positions: dict[str, Position] = {}

    def get_current_price(self, symbol: str) -> PriceQuote:
        return PriceQuote(symbol=symbol, price=float(self.prices.get(symbol, 10000.0)))

    def set_price(self, symbol: str, price: float) -> None:
        self.prices[symbol] = float(price)

    def place_order(self, request: OrderRequest) -> OrderResult:
        broker_order_id = f"MOCK-{next(self._order_seq):06d}"
        current_price = self.get_current_price(request.symbol).price

        if request.order_type == OrderType.MARKET:
            result = OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.FILLED,
                filled_price=current_price,
                filled_quantity=request.quantity,
                message="Mock market order filled.",
            )
            self._apply_fill(request, current_price)
            self._orders[broker_order_id] = result
            return result

        if not self.fill_limit_orders:
            result = OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.PENDING,
                message="Mock limit order pending by configuration.",
            )
            self._orders[broker_order_id] = result
            return result

        assert request.price is not None
        fill = False
        if request.side == Side.BUY and request.price >= current_price:
            fill = True
        if request.side == Side.SELL and request.price <= current_price:
            fill = True

        if fill:
            result = OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.FILLED,
                filled_price=request.price,
                filled_quantity=request.quantity,
                message="Mock limit order filled.",
            )
            self._apply_fill(request, request.price)
        else:
            result = OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.PENDING,
                message="Mock limit order pending.",
            )

        self._orders[broker_order_id] = result
        return result

    def cancel_order(self, broker_order_id: str) -> OrderResult:
        existing = self._orders.get(broker_order_id)
        if not existing:
            return OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.FAILED,
                message="Mock order not found.",
            )

        if existing.status == OrderStatus.FILLED:
            return existing

        canceled = OrderResult(
            broker_order_id=broker_order_id,
            status=OrderStatus.CANCELED,
            message="Mock order canceled.",
        )
        self._orders[broker_order_id] = canceled
        return canceled

    def get_order_status(self, broker_order_id: str) -> OrderResult:
        return self._orders.get(
            broker_order_id,
            OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.FAILED,
                message="Mock order not found.",
            ),
        )

    def get_positions(self) -> list[Position]:
        return list(self._positions.values())

    def _apply_fill(self, request: OrderRequest, price: float) -> None:
        current = self._positions.get(request.symbol, Position(request.symbol, 0, None))
        if request.side == Side.BUY:
            new_quantity = current.quantity + request.quantity
            if current.quantity <= 0 or current.avg_price is None:
                avg_price = price
            else:
                total_cost = current.quantity * current.avg_price + request.quantity * price
                avg_price = total_cost / new_quantity
            self._positions[request.symbol] = Position(request.symbol, new_quantity, avg_price)
            return

        new_quantity = max(0, current.quantity - request.quantity)
        self._positions[request.symbol] = Position(request.symbol, new_quantity, current.avg_price)
