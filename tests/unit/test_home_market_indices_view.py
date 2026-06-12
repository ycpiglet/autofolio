from __future__ import annotations


def test_home_view_renders_backend_market_indices(tmp_path):
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "home_market_indices_app.py"
    script.write_text(
        """
import pandas as pd
import streamlit as st
from unittest.mock import patch

st.session_state["data_source"] = "backend"

from app.ui import backend
from app.ui.views import home

def market_indices_df():
    return pd.DataFrame([
        {"name": "KOSPI", "code": "0001", "price": 2800.12, "change": 12.34, "change_rate": 0.44},
        {"name": "KOSDAQ", "code": "1001", "price": 900.55, "change": -3.21, "change_rate": -0.35},
    ])

def holdings_df(*args, **kwargs):
    return pd.DataFrame([
        {
            "종목": "KODEX 200",
            "티커": "069500",
            "자산군": "ETF",
            "지역": "KR",
            "수량": 1,
            "평단": 100000,
            "현재가": 101000,
            "평가금액": 101000,
            "평가손익": 1000,
            "손익률": 1.0,
            "예상연배당": 0,
            "배당수익률": 0.0,
            "비중": 100.0,
        }
    ])

with (
    patch.object(backend, "market_indices_df", market_indices_df),
    patch.object(backend, "holdings_df", holdings_df),
    patch.object(backend, "kpis", lambda: {"총자산": 1000000, "일손익률": 0.0, "누적손익률": 0.0, "현금비중": 10.0, "평가손익": 0}),
    patch.object(backend, "asset_curve", lambda: pd.DataFrame({"자산": [1000000, 1005000]})),
    patch.object(backend, "recent_fills", lambda: pd.DataFrame(columns=["시각", "종목", "방향", "수량", "체결가"])),
    patch.object(backend, "watchlist", lambda: pd.DataFrame(columns=["symbol", "name", "price"])),
):
    home.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)

    assert not at.exception
    assert any(metric.label == "KOSPI" for metric in at.metric)
    assert any(metric.label == "KOSDAQ" for metric in at.metric)
