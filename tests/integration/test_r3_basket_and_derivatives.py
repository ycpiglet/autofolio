from __future__ import annotations

from datetime import date, timedelta

from app.brokers.mock.mock_client import MockBrokerClient
from app.common.enums import OrderStatus, OrderType, Side
from app.engine.basket_execution import BasketIntent, BasketLeg, MockBasketExecutor
from app.risk.derivatives import DerivativeContract, estimate_margin, validate_derivative_contract


def test_mock_basket_fills_leg_results_without_live_venue():
    broker = MockBrokerClient(prices={"005930": 70_000.0, "069500": 35_000.0})
    executor = MockBasketExecutor(broker)

    result = executor.execute(
        BasketIntent(
            basket_id="BASKET-1",
            legs=(
                BasketLeg("005930", Side.BUY, 1, OrderType.MARKET),
                BasketLeg("069500", Side.BUY, 2, OrderType.MARKET),
            ),
        )
    )

    assert result.status == OrderStatus.FILLED
    assert [leg.status for leg in result.leg_results] == [OrderStatus.FILLED, OrderStatus.FILLED]
    assert {position.symbol: position.quantity for position in broker.get_positions()} == {
        "005930": 1,
        "069500": 2,
    }


def test_mock_basket_refuses_actual_venue_submission():
    broker = MockBrokerClient()
    executor = MockBasketExecutor(broker)

    result = executor.execute(
        BasketIntent(
            basket_id="BASKET-LIVE",
            venue="KRX_BLOCK",
            legs=(BasketLeg("005930", Side.BUY, 1, OrderType.MARKET),),
        )
    )

    assert result.status == OrderStatus.FAILED
    assert "disabled" in result.message
    assert result.leg_results == ()


def test_derivative_contract_validation_and_margin_estimate():
    contract = DerivativeContract(
        symbol="K200M202612",
        product_type="FUTURES",
        expiry=date.today() + timedelta(days=180),
        multiplier=250_000,
        margin_rate=0.08,
    )

    ok, reason = validate_derivative_contract(contract, today=date.today())
    assert ok, reason
    assert estimate_margin(350.0, 1, contract) == 7_000_000.0


def test_derivative_expired_contract_rejected():
    contract = DerivativeContract(
        symbol="K200M202001",
        product_type="OPTIONS",
        expiry=date.today() - timedelta(days=1),
        multiplier=250_000,
        margin_rate=0.1,
        strike=350.0,
    )

    ok, reason = validate_derivative_contract(contract, today=date.today())
    assert not ok
    assert "expired" in reason
