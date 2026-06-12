"""Broad paper-safe quant trading scenario catalog tests.

The goal of this file is breadth: asset-like instruments, price bands, order
directions, size bands, repeated churn, order lifecycle edges, and timer entry.
All tests run on isolated SQLite databases with MockBrokerClient. No KIS order
or prod endpoint is touched.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.brokers.base import OrderRequest, OrderResult, Position
from app.brokers.mock.mock_client import MockBrokerClient
from app.common.enums import ConditionStatus, OrderStatus
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import get_connection, initialize_database
from app.engine.live_trading_engine import LiveTradingEngine


@dataclass(frozen=True)
class AssetCase:
    case_id: str
    symbol: str
    name: str
    market: str
    role: str
    price: float


SUPPORTED_ASSET_CASES = [
    AssetCase("krx_stock_cheap", "000020", "low price stock proxy", "KRX", "SMALL_CAP_TEST", 850.0),
    AssetCase("krx_stock_mid", "005930", "large cap stock proxy", "KRX", "LARGE_CAP_TEST", 70_000.0),
    AssetCase("krx_stock_high", "000660", "high price stock proxy", "KRX", "LARGE_CAP_TEST", 280_000.0),
    AssetCase("krx_equity_etf", "069500", "equity ETF proxy", "KRX", "ETF_TEST", 35_000.0),
    AssetCase("krx_bond_etf", "148070", "bond ETF proxy", "KRX", "BOND_PROXY", 108_000.0),
    AssetCase("krx_commodity_etn", "530031", "commodity ETN proxy", "KRX", "ETN_PROXY", 12_345.0),
]

SIZE_CASES = [
    ("one_share", 1),
    ("small_lot", 5),
    ("large_lot", 100),
    ("very_large_lot", 1_000),
]

SIDES = ["BUY", "SELL"]
ORDER_TYPES = ["LIMIT", "MARKET"]

MATRIX_CASES = [
    (asset, side, order_type, size_label, quantity)
    for asset in SUPPORTED_ASSET_CASES
    for side in SIDES
    for order_type in ORDER_TYPES
    for size_label, quantity in SIZE_CASES
]


def _case_id(case) -> str:
    asset, side, order_type, size_label, _ = case
    return f"{asset.case_id}-{side.lower()}-{order_type.lower()}-{size_label}"


def _make_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    asset: AssetCase,
    *,
    fill_limit_orders: bool = True,
) -> tuple[Repository, MockBrokerClient, LiveTradingEngine]:
    db_path = tmp_path / f"{asset.case_id}.db"
    initialize_database(db_path)
    repo = Repository(db_path)
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_system_state("kill_switch_active", "false")
    repo.set_system_state("global_mode", "L2")
    repo.update_global_risk_limit(
        max_order_amount=1_000_000_000_000.0,
        max_daily_amount=2_000_000_000_000.0,
    )
    repo.add_whitelist_symbol(
        WhitelistSymbol(
            symbol=asset.symbol,
            name=asset.name,
            market=asset.market,
            role=asset.role,
        )
    )

    import app.risk.safety_checker as safety_checker_module

    monkeypatch.setattr(
        safety_checker_module,
        "is_within_trading_window",
        lambda *args, **kwargs: True,
    )

    broker = MockBrokerClient(prices={asset.symbol: asset.price}, fill_limit_orders=fill_limit_orders)
    engine = LiveTradingEngine(broker=broker, repo=repo)
    engine.order_flow.order_timeout_sec = 0
    return repo, broker, engine


def _trigger_price(asset: AssetCase, side: str) -> float:
    offset = max(1.0, round(asset.price * 0.01, 2))
    if side == "BUY":
        return asset.price + offset
    return max(1.0, asset.price - offset)


def _execution_count(db_path: Path, condition_id: int | None = None) -> int:
    sql = """
        SELECT COUNT(*) AS count
        FROM execution_logs el
        JOIN order_logs ol ON ol.id = el.order_log_id
    """
    params: list[object] = []
    if condition_id is not None:
        sql += " WHERE ol.condition_id = ?"
        params.append(condition_id)
    with get_connection(db_path) as conn:
        row = conn.execute(sql, params).fetchone()
        return int(row["count"])


def test_catalog_matrix_has_broad_case_count():
    assert len(SUPPORTED_ASSET_CASES) == 6
    assert len(MATRIX_CASES) == 96
    assert {asset.role for asset in SUPPORTED_ASSET_CASES} >= {
        "LARGE_CAP_TEST",
        "ETF_TEST",
        "BOND_PROXY",
        "ETN_PROXY",
    }


@pytest.mark.parametrize("case", MATRIX_CASES, ids=_case_id)
def test_supported_asset_price_size_side_order_matrix_fills(tmp_path, monkeypatch, case):
    asset, side, order_type, _size_label, quantity = case
    repo, broker, engine = _make_env(tmp_path, monkeypatch, asset)
    if side == "SELL":
        broker._positions[asset.symbol] = Position(asset.symbol, quantity, asset.price)

    condition_id = repo.add_trade_condition(
        symbol=asset.symbol,
        side=side,
        target_price=_trigger_price(asset, side),
        quantity=quantity,
        order_type=order_type,
        auto_enabled=True,
        created_by="QUANT-SCENARIO-CATALOG",
    )

    messages = engine.run_once()

    logs = [row for row in repo.list_order_logs(limit=5) if row["condition_id"] == condition_id]
    assert len(logs) == 1
    assert logs[0]["order_status"] == OrderStatus.FILLED.value
    assert logs[0]["side"] == side
    assert logs[0]["order_type"] == order_type
    assert logs[0]["quantity"] == quantity
    assert repo.get_condition(condition_id)["status"] == ConditionStatus.TRIGGERED.value
    assert _execution_count(repo.db_path, condition_id) == 1
    assert any("filled" in msg.lower() for msg in messages)


def test_repeated_buy_sell_churn_returns_to_flat_position(tmp_path, monkeypatch):
    asset = AssetCase("krx_stock_churn", "000020", "low price churn proxy", "KRX", "SMALL_CAP_TEST", 900.0)
    repo, broker, engine = _make_env(tmp_path, monkeypatch, asset)

    for cycle in range(12):
        buy_id = repo.add_trade_condition(
            symbol=asset.symbol,
            side="BUY",
            target_price=asset.price + cycle + 5,
            quantity=100,
            order_type="MARKET",
            auto_enabled=True,
            created_by="QUANT-CHURN-BUY",
        )
        assert any("filled" in msg.lower() for msg in engine.run_once())
        assert repo.get_condition(buy_id)["status"] == ConditionStatus.TRIGGERED.value

        sell_id = repo.add_trade_condition(
            symbol=asset.symbol,
            side="SELL",
            target_price=asset.price - cycle - 5,
            quantity=100,
            order_type="MARKET",
            auto_enabled=True,
            created_by="QUANT-CHURN-SELL",
        )
        assert any("filled" in msg.lower() for msg in engine.run_once())
        assert repo.get_condition(sell_id)["status"] == ConditionStatus.TRIGGERED.value

    logs = repo.list_order_logs(limit=100)
    assert len(logs) == 24
    assert all(row["order_status"] == OrderStatus.FILLED.value for row in logs)
    assert _execution_count(repo.db_path) == 24
    assert broker.get_positions()[0].quantity == 0
    assert repo.get_system_state("consecutive_order_failures", "0") == "0"


def test_multi_asset_rebalance_basket_proxy_fills_all_legs(tmp_path, monkeypatch):
    asset = SUPPORTED_ASSET_CASES[0]
    repo, broker, engine = _make_env(tmp_path, monkeypatch, asset)
    for extra in SUPPORTED_ASSET_CASES[1:4]:
        broker.set_price(extra.symbol, extra.price)
        repo.add_whitelist_symbol(
            WhitelistSymbol(extra.symbol, extra.name, extra.market, extra.role)
        )

    legs = [
        ("005930", 70_000.0, 3),
        ("069500", 35_000.0, 6),
        ("000660", 280_000.0, 1),
    ]
    condition_ids = [
        repo.add_trade_condition(
            symbol=symbol,
            side="BUY",
            target_price=price * 1.01,
            quantity=quantity,
            order_type="LIMIT",
            auto_enabled=True,
            created_by="QUANT-REBALANCE-BASKET",
        )
        for symbol, price, quantity in legs
    ]

    messages = engine.run_once()

    assert len([msg for msg in messages if "filled" in msg.lower()]) == 3
    assert _execution_count(repo.db_path) == 3
    quantities = {position.symbol: position.quantity for position in broker.get_positions()}
    assert quantities == {"005930": 3, "069500": 6, "000660": 1}
    for condition_id in condition_ids:
        assert repo.get_condition(condition_id)["status"] == ConditionStatus.TRIGGERED.value


class CancelRejectBroker(MockBrokerClient):
    def cancel_order(self, broker_order_id: str) -> OrderResult:
        return OrderResult(
            broker_order_id=broker_order_id,
            status=OrderStatus.FAILED,
            message="exchange cancel rejected",
        )


def test_pending_limit_cancel_failure_disables_auto_trading(tmp_path, monkeypatch):
    asset = SUPPORTED_ASSET_CASES[1]
    repo, _broker, _engine = _make_env(tmp_path, monkeypatch, asset, fill_limit_orders=False)
    broker = CancelRejectBroker(prices={asset.symbol: asset.price}, fill_limit_orders=False)
    engine = LiveTradingEngine(broker=broker, repo=repo)
    engine.order_flow.order_timeout_sec = 0
    condition_id = repo.add_trade_condition(
        symbol=asset.symbol,
        side="BUY",
        target_price=asset.price * 1.01,
        quantity=1,
        order_type="LIMIT",
        auto_enabled=True,
        created_by="QUANT-LIFECYCLE-CANCEL-REJECT",
    )

    messages = engine.run_once()

    logs = [row for row in repo.list_order_logs(limit=5) if row["condition_id"] == condition_id]
    assert logs[0]["order_status"] == OrderStatus.FAILED.value
    assert repo.get_system_state("auto_trading_enabled") == "false"
    assert any("failed to cancel" in msg.lower() for msg in messages)


class MarketPendingThenStatusBroker(MockBrokerClient):
    def __init__(self, final_status: OrderStatus, **kwargs):
        super().__init__(**kwargs)
        self.final_status = final_status

    def place_order(self, request: OrderRequest) -> OrderResult:
        broker_order_id = f"SCRIPTED-{next(self._order_seq):06d}"
        pending = OrderResult(
            broker_order_id=broker_order_id,
            status=OrderStatus.PENDING,
            filled_quantity=0,
            message="scripted pending",
        )
        self._orders[broker_order_id] = pending
        return pending

    def get_order_status(self, broker_order_id: str) -> OrderResult:
        if self.final_status == OrderStatus.FILLED:
            return OrderResult(
                broker_order_id=broker_order_id,
                status=OrderStatus.FILLED,
                filled_price=self.get_current_price("005930").price,
                filled_quantity=1,
                message="scripted filled",
            )
        return OrderResult(
            broker_order_id=broker_order_id,
            status=self.final_status,
            filled_quantity=0,
            message=f"scripted {self.final_status.value.lower()}",
        )


@pytest.mark.parametrize(
    ("final_status", "expected_log_status", "expected_condition_status"),
    [
        (OrderStatus.CANCELED, OrderStatus.CANCELED.value, ConditionStatus.ERROR.value),
        (OrderStatus.FAILED, OrderStatus.FAILED.value, ConditionStatus.ERROR.value),
    ],
)
def test_market_pending_terminal_non_fill_states_are_recorded(
    tmp_path,
    monkeypatch,
    final_status,
    expected_log_status,
    expected_condition_status,
):
    asset = SUPPORTED_ASSET_CASES[1]
    repo, _broker, _engine = _make_env(tmp_path, monkeypatch, asset)
    broker = MarketPendingThenStatusBroker(
        final_status,
        prices={asset.symbol: asset.price},
    )
    engine = LiveTradingEngine(broker=broker, repo=repo)
    engine.order_flow.order_timeout_sec = 0
    condition_id = repo.add_trade_condition(
        symbol=asset.symbol,
        side="BUY",
        target_price=asset.price * 1.01,
        quantity=1,
        order_type="MARKET",
        auto_enabled=True,
        created_by="QUANT-LIFECYCLE-MARKET-PENDING",
    )

    engine.run_once()

    logs = [row for row in repo.list_order_logs(limit=5) if row["condition_id"] == condition_id]
    assert logs[0]["order_status"] == expected_log_status
    assert repo.get_condition(condition_id)["status"] == expected_condition_status
    assert repo.get_system_state("consecutive_order_failures") == "1"


def _timer_cfg(db_path: Path) -> SimpleNamespace:
    return SimpleNamespace(
        kis_env="paper",
        kis_base_url="https://openapivts.koreainvestment.com:29443",
        kis_account_no="12345678",
        kis_account_product_code="01",
        db_path=db_path,
        default_trading_start="09:10",
        default_trading_end="15:20",
    )


def test_timer_dry_run_once_processes_active_condition_without_kis(tmp_path, monkeypatch):
    import app.risk.safety_checker as safety_checker_module
    import scripts.run_paper_engine as rpe

    db_path = tmp_path / "timer-dry-run.db"
    initialize_database(db_path)
    repo = Repository(db_path)
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_system_state("kill_switch_active", "false")
    repo.set_system_state("global_mode", "L2")
    repo.add_whitelist_symbol(
        WhitelistSymbol("005930", "timer stock proxy", "KRX", "LARGE_CAP_TEST")
    )
    condition_id = repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=80_000.0,
        quantity=1,
        order_type="MARKET",
        auto_enabled=True,
        created_by="QUANT-TIMER-DRY-RUN",
    )

    monkeypatch.setattr(rpe, "resolve_settings", lambda env: _timer_cfg(db_path))
    monkeypatch.setattr(safety_checker_module, "is_within_trading_window", lambda *a, **kw: True)

    assert rpe.main(["--dry-run", "--once", "--interval", "1"]) == 0
    logs = [row for row in repo.list_order_logs(limit=5) if row["condition_id"] == condition_id]
    assert logs[0]["order_status"] == OrderStatus.FILLED.value
    assert repo.get_condition(condition_id)["status"] == ConditionStatus.TRIGGERED.value
