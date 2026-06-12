from __future__ import annotations

from app.brokers.base import OrderRequest
from app.brokers.mock.mock_client import MockBrokerClient
from app.common.enums import OrderStatus, OrderType, Side


def test_default_mock_broker_keeps_legacy_market_fill_behavior():
    broker = MockBrokerClient(prices={"005930": 70_000.0})

    result = broker.place_order(
        OrderRequest("005930", Side.BUY, OrderType.MARKET, 1)
    )

    assert result.status == OrderStatus.FILLED
    assert result.filled_price == 70_000.0
    assert broker.get_positions()[0].quantity == 1
    assert broker.get_cash_balance() == 0.0


def test_cash_fee_and_slippage_are_applied_to_buy_fill():
    broker = MockBrokerClient(
        prices={"005930": 10_000.0},
        cash_balance=100_000.0,
        fee_rate=0.001,
        slippage_bps=50,
    )

    result = broker.place_order(
        OrderRequest("005930", Side.BUY, OrderType.MARKET, 2)
    )

    assert result.status == OrderStatus.FILLED
    assert result.filled_price == 10_050.0
    assert broker.get_positions()[0].avg_price == 10_050.0
    assert round(broker.get_cash_balance(), 1) == 79_879.9


def test_insufficient_cash_rejects_buy_without_position_change():
    broker = MockBrokerClient(
        prices={"005930": 70_000.0},
        cash_balance=50_000.0,
        fee_rate=0.001,
    )

    result = broker.place_order(
        OrderRequest("005930", Side.BUY, OrderType.MARKET, 1)
    )

    assert result.status == OrderStatus.FAILED
    assert "insufficient cash" in (result.message or "")
    assert broker.get_positions() == []
    assert broker.get_cash_balance() == 50_000.0


def test_concentration_limit_rejects_overweight_position():
    broker = MockBrokerClient(
        prices={"005930": 70_000.0},
        cash_balance=100_000.0,
        max_position_weight=0.50,
    )

    result = broker.place_order(
        OrderRequest("005930", Side.BUY, OrderType.MARKET, 1)
    )

    assert result.status == OrderStatus.FAILED
    assert "concentration" in (result.message or "")
    assert broker.get_positions() == []


def test_sell_adds_cash_after_fee_and_sell_side_slippage():
    broker = MockBrokerClient(
        prices={"005930": 10_000.0},
        cash_balance=100_000.0,
        fee_rate=0.001,
        slippage_bps=50,
    )
    broker.place_order(OrderRequest("005930", Side.BUY, OrderType.MARKET, 2))

    result = broker.place_order(
        OrderRequest("005930", Side.SELL, OrderType.MARKET, 1)
    )

    assert result.status == OrderStatus.FILLED
    assert result.filled_price == 9_950.0
    assert round(broker.get_cash_balance(), 2) == 89_819.95
