from __future__ import annotations

from dataclasses import dataclass

from app.brokers.base import BrokerClient, OrderRequest, OrderResult
from app.common.enums import OrderStatus, OrderType, Side


@dataclass(frozen=True)
class BasketLeg:
    symbol: str
    side: Side
    quantity: int
    order_type: OrderType = OrderType.MARKET
    price: float | None = None
    weight: float | None = None


@dataclass(frozen=True)
class BasketIntent:
    basket_id: str
    legs: tuple[BasketLeg, ...]
    all_or_none: bool = False
    venue: str = "MOCK"


@dataclass(frozen=True)
class BasketExecution:
    basket_id: str
    status: OrderStatus
    leg_results: tuple[OrderResult, ...]
    message: str


class MockBasketExecutor:
    """Mock-only basket executor.

    It intentionally refuses non-mock venues so block/basket modelling cannot
    become a hidden live broker submission path.
    """

    def __init__(self, broker: BrokerClient):
        self.broker = broker

    def execute(self, intent: BasketIntent) -> BasketExecution:
        if intent.venue.upper() != "MOCK":
            return BasketExecution(
                basket_id=intent.basket_id,
                status=OrderStatus.FAILED,
                leg_results=(),
                message="Actual block/basket venue submission is disabled.",
            )
        if not intent.legs:
            return BasketExecution(
                basket_id=intent.basket_id,
                status=OrderStatus.FAILED,
                leg_results=(),
                message="Basket has no legs.",
            )
        for leg in intent.legs:
            if leg.quantity <= 0:
                return BasketExecution(
                    basket_id=intent.basket_id,
                    status=OrderStatus.FAILED,
                    leg_results=(),
                    message=f"Invalid basket quantity for {leg.symbol}.",
                )

        results: list[OrderResult] = []
        for leg in intent.legs:
            result = self.broker.place_order(
                OrderRequest(
                    symbol=leg.symbol,
                    side=leg.side,
                    order_type=leg.order_type,
                    quantity=leg.quantity,
                    price=leg.price,
                    product_type="BASKET",
                    metadata={"basket_id": intent.basket_id, "venue": "MOCK"},
                )
            )
            results.append(result)
            if intent.all_or_none and result.status != OrderStatus.FILLED:
                return BasketExecution(
                    basket_id=intent.basket_id,
                    status=OrderStatus.FAILED,
                    leg_results=tuple(results),
                    message="All-or-none basket rejected after an unfilled leg.",
                )

        if all(result.status == OrderStatus.FILLED for result in results):
            status = OrderStatus.FILLED
            message = "Basket filled."
        elif any(result.status == OrderStatus.FILLED for result in results):
            status = OrderStatus.PENDING
            message = "Basket partially filled."
        else:
            status = OrderStatus.FAILED
            message = "Basket rejected."
        return BasketExecution(intent.basket_id, status, tuple(results), message)
