"""Order intent and audit-event regression tests."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from app.brokers.base import BrokerClient, OrderResult, PriceQuote
from app.common.enums import OrderStatus
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.engine.live_trading_engine import LiveTradingEngine


def _repo(tmp_path: Path) -> Repository:
    db = tmp_path / "audit.db"
    initialize_database(db)
    repo = Repository(db)
    repo.add_whitelist_symbol(
        WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
    )
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_system_state("kill_switch_active", "false")
    return repo


def _engine(repo: Repository) -> LiveTradingEngine:
    broker = MagicMock(spec=BrokerClient)
    broker.get_current_price.return_value = PriceQuote(symbol="005930", price=65_000.0)
    broker.place_order.return_value = OrderResult(
        broker_order_id="ORD-001",
        status=OrderStatus.FILLED,
        filled_price=65_000.0,
        filled_quantity=1,
        message="filled",
    )
    return LiveTradingEngine(broker=broker, repo=repo)


def test_run_once_records_user_actor_and_order_audit(tmp_path, monkeypatch):
    import app.risk.safety_checker as safety_checker_module

    monkeypatch.setattr(
        safety_checker_module,
        "is_within_trading_window",
        lambda *args, **kwargs: True,
    )
    repo = _repo(tmp_path)
    repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=70_000.0,
        quantity=1,
        created_by="USER",
    )
    engine = _engine(repo)

    messages = engine.run_once(
        actor_type="USER",
        actor_id="testuser",
        source_surface="api:engine/run-once",
        trigger_reason="manual run_once",
    )

    assert any("filled" in message.lower() for message in messages)
    events = repo.list_order_audit_events(limit=20)
    event_types = {event["event_type"] for event in events}
    assert {"intent_created", "pre_order_check_passed", "order_submitted", "order_filled"} <= event_types
    latest = events[0]
    assert latest["actor_type"] == "USER"
    assert latest["actor_id"] == "testuser"
    assert latest["source_surface"] == "api:engine/run-once"
    assert repo.engine_health()["status"] == "ok"


def test_duplicate_intent_is_blocked_before_broker_submit(tmp_path, monkeypatch):
    import app.risk.safety_checker as safety_checker_module

    monkeypatch.setattr(
        safety_checker_module,
        "is_within_trading_window",
        lambda *args, **kwargs: True,
    )
    repo = _repo(tmp_path)
    cid = repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=70_000.0,
        quantity=1,
    )
    condition = repo.get_condition(cid)
    repo.ensure_order_intent(
        condition=condition,
        actor_type="SCHEDULER",
        actor_id="engine",
        source_surface="engine",
        trigger_reason="scheduled run",
    )
    engine = _engine(repo)

    result = engine.order_flow.process_condition_once(condition)

    assert result.executed is False
    assert result.message == "Duplicate order intent blocked."
    assert engine.broker.place_order.call_count == 0
    events = repo.list_order_audit_events(limit=5)
    assert events[0]["event_type"] == "duplicate_intent_blocked"
