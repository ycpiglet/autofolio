from __future__ import annotations

from types import SimpleNamespace

import pandas as pd

from app.ui import theme
from app.ui.views import trade


class _TradeBackend:
    def __init__(self, *, auto: bool = True, kill: bool = False):
        self._auto = auto
        self._kill = kill

    def env(self) -> str:
        return "paper"

    def get_flag(self, key: str) -> bool:
        values = {
            "auto_trading_enabled": self._auto,
            "kill_switch_active": self._kill,
        }
        return values[key]

    def circuit_breaker_status(self) -> dict:
        return {"triggered": False}

    def list_whitelist(self) -> pd.DataFrame:
        return pd.DataFrame(
            [{"symbol": "005930", "name": "Samsung", "enabled": True}]
        )

    def list_conditions(self) -> pd.DataFrame:
        return pd.DataFrame()

    def today_order_amount(self) -> float:
        return 0.0

    def get_global_risk_limit(self) -> dict:
        return {"max_order_amount": 100_000.0, "max_daily_amount": 1_000_000.0}


def test_trade_gate_accepts_backend_dataframe_whitelist(monkeypatch):
    monkeypatch.setitem(trade.st.session_state, "data_source", "backend")
    monkeypatch.setitem(trade.st.session_state, "mode", "L2")
    monkeypatch.setitem(trade.st.session_state, "kill_switch", False)

    state = trade._collect_trade_gate_state(_TradeBackend())

    assert state["env_label"] == theme.env_label("paper")
    assert state["source"] == "backend"
    assert state["whitelist_count"] == 1
    assert state["today_order_amount"] == 0.0
    assert state["max_order_amount"] == 100_000.0
    assert state["max_daily_amount"] == 1_000_000.0
    assert state["all_ok"] is True


def test_trade_gate_blocks_when_kill_switch_is_active(monkeypatch):
    monkeypatch.setitem(trade.st.session_state, "data_source", "backend")
    monkeypatch.setitem(trade.st.session_state, "mode", "L2")
    monkeypatch.setitem(trade.st.session_state, "kill_switch", False)

    state = trade._collect_trade_gate_state(_TradeBackend(kill=True))

    assert state["env_label"] == theme.env_label("paper")
    assert state["kill_active"] is True
    assert state["all_ok"] is False
    assert any(
        label == "킬스위치" and ok is False and "활성" in reason
        for label, ok, reason in state["checks"]
    )


def test_backend_exposes_trade_guard_read_contract(monkeypatch):
    from app.ui import backend

    repo = SimpleNamespace(
        today_order_amount=lambda: 12345.0,
        get_global_risk_limit=lambda: {
            "max_order_amount": 100_000.0,
            "max_daily_amount": 1_000_000.0,
        },
    )
    monkeypatch.setattr(backend, "_ctx", lambda: (repo, None, None, None))

    assert backend.today_order_amount() == 12345.0
    assert backend.get_global_risk_limit()["max_daily_amount"] == 1_000_000.0
