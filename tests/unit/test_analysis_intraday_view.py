from __future__ import annotations


def test_analysis_view_renders_intraday_controls(tmp_path):
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "analysis_intraday_app.py"
    script.write_text(
        """
import pandas as pd
import streamlit as st
from unittest.mock import patch

st.session_state["data_source"] = "backend"

from app.ui import backend
from app.ui.views import analysis

def intraday_chart_df(symbol, time_unit="1", count=120):
    return pd.DataFrame([
        {
            "datetime": pd.Timestamp("2026-06-11 09:00:00"),
            "open": 302000.0,
            "high": 306000.0,
            "low": 301000.0,
            "close": 304000.0,
            "volume": 8000,
        }
    ])

def sector_performance_df():
    return pd.DataFrame([
        {
            "name": "KOSPI 전기·전자",
            "code": "0013",
            "price": 1234.56,
            "change": 12.34,
            "change_rate": 1.01,
            "trading_value": 987654321,
        }
    ])

def fundamental(symbol):
    return {
        "symbol": symbol,
        "per": 12.3,
        "pbr": 1.4,
        "eps": 5000.0,
        "market_cap": 400000000.0,
        "finance_ratio": {"sale_totl_rate": 10.1, "sale_ntin_rate": 8.2, "lblt_rate": 30.0},
    }

with (
    patch.object(backend, "list_whitelist", lambda: pd.DataFrame([
        {"symbol": "005930", "name": "삼성전자", "market": "KRX", "role": "LARGE_CAP_TEST", "enabled": 1}
    ])),
    patch.object(backend, "fundamental", fundamental),
    patch.object(backend, "intraday_chart_df", intraday_chart_df),
    patch.object(backend, "sector_performance_df", sector_performance_df),
    patch.object(backend, "attribution_df", lambda: pd.DataFrame(columns=["구분", "기여(만원)"])),
    patch.object(backend, "retro_metrics", lambda: {"승률": 0, "평균R": 0.0, "MDD": 0.0, "규율": 0}),
    patch.object(backend, "allocation_gap", lambda: pd.DataFrame(columns=["자산군", "목표%", "현재%", "갭%"])),
    patch.object(backend, "scenario_analysis", lambda: pd.DataFrame()),
    patch.object(backend, "watchlist", lambda: pd.DataFrame()),
):
    analysis.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)

    assert not at.exception
    assert any(item.value == "재무 지표" for item in at.subheader)
    assert any(item.value == "분봉 차트" for item in at.subheader)
    assert any(item.value == "업종 퍼포먼스" for item in at.subheader)
    assert any(item.label == "분봉" for item in at.selectbox)
    assert any(item.label == "개수" for item in at.number_input)
    assert len(at.dataframe) >= 1
