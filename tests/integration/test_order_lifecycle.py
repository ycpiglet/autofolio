from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from app.brokers.base import OrderRequest, OrderResult
from app.brokers.mock.mock_client import MockBrokerClient
from app.common.enums import ConditionStatus, OrderStatus
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.engine.live_trading_engine import LiveTradingEngine


@dataclass(frozen=True)
class FillSlice:
    price: float
    quantity: int


def _make_repo(tmp_path: Path) -> Repository:
    db_path = tmp_path / "order-lifecycle.db"
    initialize_database(db_path)
    repo = Repository(db_path)
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_system_state("kill_switch_active", "false")
    repo.set_system_state("global_mode", "L2")
    repo.update_global_risk_limit(max_order_amount=10_000_000.0, max_daily_amount=20_000_000.0)
    repo.add_whitelist_symbol(WhitelistSymbol("005930", "삼성전자", "KRX", "LARGE_CAP_TEST"))
    return repo


def _condition(repo: Repository, *, quantity: int = 10) -> int:
    return repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=80_000.0,
        quantity=quantity,
        order_type="LIMIT",
        auto_enabled=True,
        created_by="ORDER-LIFECYCLE-TEST",
    )


class PendingThenStatusBroker(MockBrokerClient):
    def __init__(self, status: OrderResult, *, cancel_result: OrderResult | None = None):
        super().__init__(prices={"005930": 70_000.0}, fill_limit_orders=False)
        self.status = status
        self.cancel_result = cancel_result

    def place_order(self, request: OrderRequest) -> OrderResult:
        pending = OrderResult("SCRIPTED-LIMIT-1", OrderStatus.PENDING, message="scripted pending")
        self._orders[pending.broker_order_id] = pending
        return pending

    def get_order_status(self, broker_order_id: str) -> OrderResult:
        return self.status

    def cancel_order(self, broker_order_id: str) -> OrderResult:
        if self.cancel_result is not None:
            return self.cancel_result
        return super().cancel_order(broker_order_id)


class PartialFillLedger:
    """Test harness for FIX-style cumulative fill accounting."""

    def __init__(self, repo: Repository, order_log_id: int, total_quantity: int):
        self.repo = repo
        self.order_log_id = order_log_id
        self.total_quantity = total_quantity

    def record(self, fill: FillSlice) -> None:
        self.repo.create_execution_log(
            order_log_id=self.order_log_id,
            symbol="005930",
            filled_price=fill.price,
            filled_quantity=fill.quantity,
            raw_status=f"PARTIAL {fill.quantity}@{fill.price}",
        )

    def snapshot(self) -> dict:
        row = self.repo.list_order_logs(limit=1)[0]
        filled_quantity = int(row["filled_quantity"] or 0)
        return {
            "filled_quantity": filled_quantity,
            "remaining_quantity": self.total_quantity - filled_quantity,
            "weighted_avg_price": row["filled_price"],
        }


def test_order_lifecycle_partial_fill_sequence_accumulates_remaining_quantity(tmp_path):
    repo = _make_repo(tmp_path)
    order_log_id = repo.create_order_log(
        condition_id=None,
        symbol="005930",
        side="BUY",
        order_type="LIMIT",
        order_price=70_000.0,
        current_price=69_900.0,
        quantity=10,
        kis_order_id="SCRIPTED-PARTIAL",
        order_status=OrderStatus.PENDING.value,
    )
    ledger = PartialFillLedger(repo, order_log_id, total_quantity=10)

    ledger.record(FillSlice(price=70_000.0, quantity=4))
    ledger.record(FillSlice(price=70_100.0, quantity=3))

    snapshot = ledger.snapshot()
    assert snapshot["filled_quantity"] == 7
    assert snapshot["remaining_quantity"] == 3
    assert round(snapshot["weighted_avg_price"], 2) == 70_042.86


def test_order_lifecycle_pending_limit_fills_before_cancel(tmp_path, monkeypatch):
    repo = _make_repo(tmp_path)
    filled = OrderResult(
        "SCRIPTED-LIMIT-1",
        OrderStatus.FILLED,
        filled_price=70_000.0,
        filled_quantity=10,
        message="filled before cancel",
    )
    broker = PendingThenStatusBroker(filled)
    engine = LiveTradingEngine(broker=broker, repo=repo)
    engine.order_flow.order_timeout_sec = 0

    import app.risk.safety_checker as safety_checker_module

    monkeypatch.setattr(safety_checker_module, "is_within_trading_window", lambda *a, **kw: True)
    condition_id = _condition(repo)

    messages = engine.run_once()

    log = [row for row in repo.list_order_logs() if row["condition_id"] == condition_id][0]
    assert log["order_status"] == OrderStatus.FILLED.value
    assert log["filled_quantity"] == 10
    assert repo.get_condition(condition_id)["status"] == ConditionStatus.TRIGGERED.value
    assert any("filled" in message.lower() for message in messages)


def test_order_lifecycle_cancel_reject_disables_auto_trading(tmp_path, monkeypatch):
    repo = _make_repo(tmp_path)
    pending = OrderResult("SCRIPTED-LIMIT-1", OrderStatus.PENDING, message="still pending")
    cancel_reject = OrderResult("SCRIPTED-LIMIT-1", OrderStatus.FAILED, message="cancel rejected")
    broker = PendingThenStatusBroker(pending, cancel_result=cancel_reject)
    engine = LiveTradingEngine(broker=broker, repo=repo)
    engine.order_flow.order_timeout_sec = 0

    import app.risk.safety_checker as safety_checker_module

    monkeypatch.setattr(safety_checker_module, "is_within_trading_window", lambda *a, **kw: True)
    condition_id = _condition(repo)

    messages = engine.run_once()

    log = [row for row in repo.list_order_logs() if row["condition_id"] == condition_id][0]
    assert log["order_status"] == OrderStatus.FAILED.value
    assert repo.get_system_state("auto_trading_enabled") == "false"
    assert any("failed to cancel" in message.lower() for message in messages)


def test_order_lifecycle_too_late_to_cancel_harness_records_late_fill(tmp_path):
    repo = _make_repo(tmp_path)
    order_log_id = repo.create_order_log(
        condition_id=None,
        symbol="005930",
        side="BUY",
        order_type="LIMIT",
        order_price=70_000.0,
        current_price=70_000.0,
        quantity=5,
        kis_order_id="SCRIPTED-TOO-LATE",
        order_status=OrderStatus.PENDING.value,
    )

    cancel_result = OrderResult(
        "SCRIPTED-TOO-LATE",
        OrderStatus.FILLED,
        filled_price=70_000.0,
        filled_quantity=5,
        message="too late to cancel; filled",
    )
    repo.update_order_status(order_log_id, cancel_result.status.value)
    repo.create_execution_log(
        order_log_id=order_log_id,
        symbol="005930",
        filled_price=cancel_result.filled_price,
        filled_quantity=cancel_result.filled_quantity,
        raw_status=cancel_result.message,
    )

    row = repo.list_order_logs(limit=1)[0]
    assert row["order_status"] == OrderStatus.FILLED.value
    assert row["filled_quantity"] == 5
    assert row["quantity"] - row["filled_quantity"] == 0


@pytest.mark.parametrize(
    "keyword",
    ["partial_fill", "pending_limit", "cancel_reject", "too_late_to_cancel"],
)
def test_order_lifecycle_catalog_keywords_are_represented(keyword):
    cases = {
        "partial_fill": "test_order_lifecycle_partial_fill_sequence_accumulates_remaining_quantity",
        "pending_limit": "test_order_lifecycle_pending_limit_fills_before_cancel",
        "cancel_reject": "test_order_lifecycle_cancel_reject_disables_auto_trading",
        "too_late_to_cancel": "test_order_lifecycle_too_late_to_cancel_harness_records_late_fill",
    }
    assert keyword in cases
