from __future__ import annotations


def test_alerts_view_renders_disclosure_panel(tmp_path):
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "alerts_disclosure_app.py"
    script.write_text(
        """
import pandas as pd
import streamlit as st
from unittest.mock import patch

st.session_state["data_source"] = "backend"

from app.ui import backend
from app.ui.views import alerts

with (
    patch.object(backend, "symbol_options", lambda: {"005930 · 삼성전자": "005930"}),
    patch.object(backend, "disclosure_gate_state", lambda symbol: {"symbol": symbol, "blocked": False, "reason": ""}),
    patch.object(backend, "refresh_disclosure_gate", lambda symbol, days=1, notify=False: {
        "symbol": symbol,
        "blocked": False,
        "reason": "",
        "disclosures": pd.DataFrame(columns=["date", "time", "title", "category", "severity", "source"]),
    }),
    patch.object(backend, "list_order_logs", lambda limit=50: pd.DataFrame()),
):
    alerts.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)

    assert not at.exception
    assert any(item.value == "뉴스/공시" for item in at.subheader)
    assert any(item.label == "공시 확인" for item in at.button)
