from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Callable

import pytest

from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database


@dataclass(frozen=True)
class StrategyIntent:
    strategy: str
    symbol: str
    side: str
    target_price: float
    quantity: int
    order_type: str = "MARKET"
    reason: str = ""


@dataclass(frozen=True)
class ScheduledEvent:
    event_id: str
    run_at: datetime
    callback: Callable[[], list[StrategyIntent]]


@dataclass
class DeterministicClock:
    now: datetime

    def advance_to(self, value: datetime) -> None:
        self.now = value


@dataclass
class SchedulerHarness:
    clock: DeterministicClock
    events: list[ScheduledEvent] = field(default_factory=list)
    executed: set[str] = field(default_factory=set)

    def schedule(self, event: ScheduledEvent) -> None:
        self.events.append(event)

    def due_intents(self) -> list[StrategyIntent]:
        intents: list[StrategyIntent] = []
        for event in sorted(self.events, key=lambda e: e.run_at):
            if event.event_id in self.executed:
                continue
            if event.run_at <= self.clock.now:
                intents.extend(event.callback())
                self.executed.add(event.event_id)
        return intents


def _repo(tmp_path: Path) -> Repository:
    db_path = tmp_path / "scheduled-strategies.db"
    initialize_database(db_path)
    repo = Repository(db_path)
    repo.add_whitelist_symbol(WhitelistSymbol("005930", "삼성전자", "KRX", "LARGE_CAP_TEST"))
    repo.add_whitelist_symbol(WhitelistSymbol("069500", "KODEX 200", "KRX", "ETF_TEST"))
    repo.add_whitelist_symbol(WhitelistSymbol("000660", "SK하이닉스", "KRX", "LARGE_CAP_TEST"))
    return repo


def _intent_to_condition(repo: Repository, intent: StrategyIntent, *, target_env: str = "mock") -> int:
    if target_env == "prod":
        raise RuntimeError("scheduled strategy harness refuses prod order targets")
    return repo.add_trade_condition(
        symbol=intent.symbol,
        side=intent.side,
        target_price=intent.target_price,
        quantity=intent.quantity,
        order_type=intent.order_type,
        auto_enabled=False,
        created_by=f"SCHEDULED-{intent.strategy}",
        rationale=intent.reason,
    )


def _dca(symbol: str, price: float, quantity: int) -> list[StrategyIntent]:
    return [
        StrategyIntent(
            strategy="DCA",
            symbol=symbol,
            side="BUY",
            target_price=price,
            quantity=quantity,
            reason="scheduled dollar-cost averaging",
        )
    ]


def _calendar_rebalance(current_weights: dict[str, float], target_weights: dict[str, float]) -> list[StrategyIntent]:
    intents: list[StrategyIntent] = []
    for symbol, target in target_weights.items():
        current = current_weights.get(symbol, 0.0)
        if current < target - 5:
            intents.append(StrategyIntent("REBALANCE", symbol, "BUY", 100_000.0, 1, reason="below target weight"))
        elif current > target + 5:
            intents.append(StrategyIntent("REBALANCE", symbol, "SELL", 100_000.0, 1, reason="above target weight"))
    return intents


def _pairs_trade(spread_zscore: float) -> list[StrategyIntent]:
    if spread_zscore < -2:
        return [
            StrategyIntent("PAIRS", "005930", "BUY", 70_000.0, 1, reason="long underperformer"),
            StrategyIntent("PAIRS", "000660", "SELL", 280_000.0, 1, reason="short/trim outperformer proxy"),
        ]
    if spread_zscore > 2:
        return [
            StrategyIntent("PAIRS", "005930", "SELL", 70_000.0, 1, reason="trim outperformer proxy"),
            StrategyIntent("PAIRS", "000660", "BUY", 280_000.0, 1, reason="long underperformer"),
        ]
    return []


def _volatility_breakout(symbol: str, previous_high: float, current_price: float) -> list[StrategyIntent]:
    trigger = previous_high * 1.01
    if current_price <= trigger:
        return []
    return [
        StrategyIntent(
            "VOL_BREAKOUT",
            symbol,
            "BUY",
            round(current_price, 2),
            1,
            reason=f"price {current_price} exceeded breakout trigger {trigger}",
        )
    ]


def _eod_liquidation(positions: dict[str, int], close_price: dict[str, float]) -> list[StrategyIntent]:
    return [
        StrategyIntent("EOD_LIQUIDATION", symbol, "SELL", close_price[symbol], quantity, reason="end-of-day flatten")
        for symbol, quantity in positions.items()
        if quantity > 0
    ]


def test_scheduled_dca_emits_one_mock_condition_per_due_event(tmp_path):
    repo = _repo(tmp_path)
    clock = DeterministicClock(datetime(2026, 6, 12, 9, 0))
    scheduler = SchedulerHarness(clock)
    scheduler.schedule(
        ScheduledEvent(
            "dca-2026-06-12",
            datetime(2026, 6, 12, 9, 30),
            lambda: _dca("069500", 35_000.0, 3),
        )
    )

    assert scheduler.due_intents() == []
    clock.advance_to(datetime(2026, 6, 12, 9, 30))
    condition_ids = [_intent_to_condition(repo, intent) for intent in scheduler.due_intents()]

    condition = repo.get_condition(condition_ids[0])
    assert condition["symbol"] == "069500"
    assert condition["side"] == "BUY"
    assert condition["quantity"] == 3
    assert condition["auto_enabled"] == 0


def test_persistent_scheduled_event_runs_once_across_replay(tmp_path):
    repo = _repo(tmp_path)
    clock = DeterministicClock(datetime(2026, 6, 12, 10, 0))
    scheduler = SchedulerHarness(clock)
    scheduler.schedule(
        ScheduledEvent("dca-once", datetime(2026, 6, 12, 9, 30), lambda: _dca("005930", 70_000.0, 1))
    )

    first = [_intent_to_condition(repo, intent) for intent in scheduler.due_intents()]
    second = [_intent_to_condition(repo, intent) for intent in scheduler.due_intents()]

    assert len(first) == 1
    assert second == []
    assert len(repo.list_conditions()) == 1


def test_calendar_rebalance_emits_buy_and_sell_intents(tmp_path):
    repo = _repo(tmp_path)
    intents = _calendar_rebalance(
        {"005930": 45.0, "069500": 10.0},
        {"005930": 30.0, "069500": 30.0},
    )
    ids = [_intent_to_condition(repo, intent) for intent in intents]
    rows = [repo.get_condition(cid) for cid in ids]

    assert {(row["symbol"], row["side"]) for row in rows} == {
        ("005930", "SELL"),
        ("069500", "BUY"),
    }


def test_pairs_strategy_emits_market_neutral_mock_intents(tmp_path):
    repo = _repo(tmp_path)
    ids = [_intent_to_condition(repo, intent) for intent in _pairs_trade(spread_zscore=-2.5)]
    rows = [repo.get_condition(cid) for cid in ids]

    assert [(row["symbol"], row["side"]) for row in rows] == [
        ("005930", "BUY"),
        ("000660", "SELL"),
    ]


def test_volatility_breakout_waits_until_trigger_then_emits(tmp_path):
    repo = _repo(tmp_path)
    before = _volatility_breakout("005930", previous_high=70_000.0, current_price=70_100.0)
    after = _volatility_breakout("005930", previous_high=70_000.0, current_price=70_900.0)
    ids = [_intent_to_condition(repo, intent) for intent in after]

    assert before == []
    assert len(ids) == 1
    assert repo.get_condition(ids[0])["created_by"] == "SCHEDULED-VOL_BREAKOUT"


def test_eod_liquidation_emits_sell_intents_before_close(tmp_path):
    repo = _repo(tmp_path)
    clock = DeterministicClock(datetime.combine(date(2026, 6, 12), time(15, 19)))
    scheduler = SchedulerHarness(clock)
    scheduler.schedule(
        ScheduledEvent(
            "eod-flat-2026-06-12",
            datetime(2026, 6, 12, 15, 20),
            lambda: _eod_liquidation({"005930": 2, "069500": 0, "000660": 1}, {"005930": 70_000.0, "000660": 280_000.0}),
        )
    )

    assert scheduler.due_intents() == []
    clock.advance_to(clock.now + timedelta(minutes=1))
    ids = [_intent_to_condition(repo, intent) for intent in scheduler.due_intents()]
    rows = [repo.get_condition(cid) for cid in ids]

    assert {(row["symbol"], row["side"], row["quantity"]) for row in rows} == {
        ("005930", "SELL", 2),
        ("000660", "SELL", 1),
    }


def test_strategy_to_condition_harness_refuses_prod_targets(tmp_path):
    repo = _repo(tmp_path)
    intent = _dca("005930", 70_000.0, 1)[0]

    with pytest.raises(RuntimeError, match="refuses prod"):
        _intent_to_condition(repo, intent, target_env="prod")

    assert repo.list_conditions() == []
