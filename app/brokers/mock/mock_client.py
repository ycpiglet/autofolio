from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count
from math import isfinite
from typing import Dict

from app.brokers.base import BrokerClient, OrderRequest, OrderResult, Position, PriceQuote
from app.common.enums import OrderStatus, OrderType, Side


_MARKET_LIKE_TYPES = {OrderType.MARKET, OrderType.MOO, OrderType.MOC, OrderType.STOP, OrderType.TRAILING_STOP}
_LIMIT_LIKE_TYPES = {
    OrderType.LIMIT,
    OrderType.CONDITIONAL_LIMIT,
    OrderType.BEST_LIMIT,
    OrderType.PRIORITY_LIMIT,
    OrderType.STOP_LIMIT,
    OrderType.IOC,
    OrderType.FOK,
}


@dataclass
class MockBrokerClient(BrokerClient):
    prices: Dict[str, float] = field(default_factory=lambda: {
        "005930": 70000.0,
        "069500": 35000.0,
        "360750": 18000.0,
    })
    fill_limit_orders: bool = True
    cash_balance: float | None = None
    fee_rate: float = 0.0
    slippage_bps: float = 0.0
    max_position_weight: float | None = None

    def __post_init__(self) -> None:
        self._order_seq = count(1)
        self._orders: dict[str, OrderResult] = {}
        self._positions: dict[str, Position] = {}
        if self.cash_balance is not None:
            self.cash_balance = float(self.cash_balance)

    def get_current_price(self, symbol: str) -> PriceQuote:
        return PriceQuote(symbol=symbol, price=float(self.prices.get(symbol, 10000.0)))

    def set_price(self, symbol: str, price: float) -> None:
        self.prices[symbol] = float(price)

    def place_order(self, request: OrderRequest) -> OrderResult:
        broker_order_id = f"MOCK-{next(self._order_seq):06d}"
        current_price = self.get_current_price(request.symbol).price

        if request.order_type in _MARKET_LIKE_TYPES:
            filled_price = self._execution_price(request.side, current_price)
            rejection = self._portfolio_rejection(request, filled_price)
            if rejection:
                result = OrderResult(
                    broker_order_id=broker_order_id,
                    status=OrderStatus.FAILED,
                    message=rejection,
                )
                self._orders[broker_order_id] = result
                return result
            result = OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.FILLED,
                filled_price=filled_price,
                filled_quantity=request.quantity,
                message=f"Mock {request.order_type.value.lower()} order filled.",
            )
            self._apply_fill(request, filled_price)
            self._orders[broker_order_id] = result
            return result

        if request.order_type not in _LIMIT_LIKE_TYPES:
            result = OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.FAILED,
                message=f"Mock broker does not support order type {request.order_type.value}.",
            )
            self._orders[broker_order_id] = result
            return result

        if not self.fill_limit_orders:
            if request.order_type in {OrderType.IOC, OrderType.FOK}:
                result = OrderResult(
                    broker_order_id=broker_order_id,
                    status=OrderStatus.CANCELED,
                    message=f"Mock {request.order_type.value} order canceled: immediate fill unavailable.",
                )
                self._orders[broker_order_id] = result
                return result
            result = OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.PENDING,
                message="Mock limit order pending by configuration.",
            )
            self._orders[broker_order_id] = result
            return result

        assert request.price is not None
        available_quantity = int(request.metadata.get("available_quantity", request.quantity))
        if request.order_type == OrderType.FOK and available_quantity < request.quantity:
            result = OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.CANCELED,
                message="Mock FOK order canceled: insufficient immediate quantity.",
            )
            self._orders[broker_order_id] = result
            return result

        fill = False
        if request.side == Side.BUY and request.price >= current_price:
            fill = True
        if request.side == Side.SELL and request.price <= current_price:
            fill = True

        if fill:
            filled_price = self._execution_price(request.side, request.price)
            rejection = self._portfolio_rejection(request, filled_price)
            if rejection:
                result = OrderResult(
                    broker_order_id=broker_order_id,
                    status=OrderStatus.FAILED,
                    message=rejection,
                )
                self._orders[broker_order_id] = result
                return result
            result = OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.FILLED,
                filled_price=filled_price,
                filled_quantity=request.quantity,
                message=f"Mock {request.order_type.value.lower()} order filled.",
            )
            self._apply_fill(request, filled_price)
        elif request.order_type == OrderType.IOC:
            result = OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.CANCELED,
                message="Mock IOC order canceled: no immediate fill.",
            )
        elif request.order_type == OrderType.FOK:
            result = OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.CANCELED,
                message="Mock FOK order canceled: full fill unavailable.",
            )
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

    def get_cash_balance(self) -> float:
        return float(self.cash_balance or 0.0)

    def _apply_fill(self, request: OrderRequest, price: float) -> None:
        current = self._positions.get(request.symbol, Position(request.symbol, 0, None))
        fee = self._fee(price, request.quantity)
        if request.side == Side.BUY:
            new_quantity = current.quantity + request.quantity
            if current.quantity <= 0 or current.avg_price is None:
                avg_price = price
            else:
                total_cost = current.quantity * current.avg_price + request.quantity * price
                avg_price = total_cost / new_quantity
            self._positions[request.symbol] = Position(request.symbol, new_quantity, avg_price)
            if self.cash_balance is not None:
                self.cash_balance -= price * request.quantity + fee
            return

        new_quantity = max(0, current.quantity - request.quantity)
        self._positions[request.symbol] = Position(request.symbol, new_quantity, current.avg_price)
        if self.cash_balance is not None:
            self.cash_balance += price * request.quantity - fee

    def _execution_price(self, side: Side, reference_price: float) -> float:
        if self.slippage_bps == 0:
            return float(reference_price)
        direction = 1 if side == Side.BUY else -1
        price = float(reference_price) * (1 + direction * self.slippage_bps / 10_000)
        return round(price, 4)

    def _fee(self, price: float, quantity: int) -> float:
        fee = float(price) * int(quantity) * float(self.fee_rate)
        return round(fee, 4)

    def _portfolio_rejection(self, request: OrderRequest, price: float) -> str | None:
        if not isfinite(price) or price <= 0:
            return "Mock portfolio ledger rejected invalid execution price."
        if request.quantity <= 0:
            return "Mock portfolio ledger rejected non-positive quantity."
        if request.side == Side.BUY:
            total_cost = price * request.quantity + self._fee(price, request.quantity)
            if self.cash_balance is not None and total_cost > self.cash_balance:
                return "Mock portfolio ledger rejected: insufficient cash."
            if self.max_position_weight is not None:
                projected_weight = self._projected_position_weight(request, price, total_cost)
                if projected_weight > self.max_position_weight:
                    return (
                        "Mock portfolio ledger rejected: concentration "
                        f"{projected_weight:.2%} exceeds {self.max_position_weight:.2%}."
                    )
        return None

    def _projected_position_weight(
        self,
        request: OrderRequest,
        price: float,
        total_cost: float,
    ) -> float:
        projected_cash = max(0.0, float(self.cash_balance or 0.0) - total_cost)
        holdings_value = 0.0
        target_value = 0.0
        for symbol, position in self._positions.items():
            current_price = self.get_current_price(symbol).price
            quantity = position.quantity
            if symbol == request.symbol:
                quantity += request.quantity
            value = quantity * current_price
            holdings_value += value
            if symbol == request.symbol:
                target_value = value
        if request.symbol not in self._positions:
            target_value = request.quantity * price
            holdings_value += target_value
        total_assets = holdings_value + projected_cash
        if total_assets <= 0:
            return 1.0
        return target_value / total_assets
