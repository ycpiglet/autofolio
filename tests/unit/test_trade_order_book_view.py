from __future__ import annotations


def test_trade_view_renders_order_book_panel(tmp_path):
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "trade_order_book_app.py"
    script.write_text(
        """
import pandas as pd
import streamlit as st
from unittest.mock import patch

st.session_state["data_source"] = "backend"

from app.ui import backend
from app.ui.views import trade

snapshot = {
    "symbol": "005930",
    "market": "J",
    "current_price": 70000.0,
    "expected_price": 70100.0,
    "levels": [
        {"level": 1, "ask_price": 70100.0, "ask_quantity": 100, "bid_price": 70000.0, "bid_quantity": 200},
        {"level": 2, "ask_price": 70200.0, "ask_quantity": 300, "bid_price": 69900.0, "bid_quantity": 400},
    ],
}

with (
    patch.object(backend, "env", lambda: "paper"),
    patch.object(backend, "symbol_options", lambda: {"005930 · 삼성전자": "005930"}),
    patch.object(backend, "price", lambda symbol: 70000.0),
    patch.object(backend, "order_book_snapshot", lambda symbol: snapshot),
    patch.object(backend, "order_book_levels_df", lambda snapshot: pd.DataFrame(snapshot["levels"])),
    patch.object(backend, "disclosure_gate_state", lambda symbol: {"symbol": symbol, "blocked": False, "reason": ""}),
    patch.object(backend, "refresh_disclosure_gate", lambda symbol, days=1: {"symbol": symbol, "blocked": False, "reason": "", "disclosures": pd.DataFrame()}),
    patch.object(backend, "list_conditions", lambda: pd.DataFrame(columns=["id", "symbol", "status"])),
    patch.object(backend, "list_order_logs", lambda limit=100: pd.DataFrame()),
    patch.object(backend, "kis_today_orders", lambda: pd.DataFrame()),
    patch.object(backend, "circuit_breaker_status", lambda: {"triggered": False, "consecutive_failures": 0}),
    patch.object(backend, "get_flag", lambda key: key == "auto_trading_enabled"),
    patch.object(backend, "list_whitelist", lambda: pd.DataFrame([
        {"symbol": "005930", "name": "삼성전자", "market": "KRX", "role": "LARGE_CAP_TEST", "enabled": 1}
    ])),
):
    trade.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)

    assert not at.exception
    assert any(item.value == "호가창" for item in at.subheader)
    assert any(item.label == "예상평균가" for item in at.metric)
    assert len(at.dataframe) >= 1
