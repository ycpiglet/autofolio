from __future__ import annotations

import pandas as pd


def test_history_view_queries_kis_order_history_from_date_controls(
    monkeypatch, tmp_path
):
    import streamlit as st
    from streamlit.testing.v1 import AppTest

    from app.ui import backend

    # --- fakes defined in test scope (st.session_state resolved at call-time) ---

    monkeypatch.setattr(backend, "list_order_logs", lambda: pd.DataFrame())

    def fake_order_history(start_date, end_date):
        st.session_state["hist_calls"].append((start_date, end_date))
        return pd.DataFrame(
            [
                {
                    "날짜": start_date,
                    "주문번호": "0000117057",
                    "종목": "005930",
                    "구분": "매수",
                    "주문수량": 1,
                    "체결수량": 1,
                    "주문가": 70500,
                    "체결평균가": 70500,
                    "상태": "체결",
                }
            ]
        )

    monkeypatch.setattr(backend, "kis_order_history", fake_order_history)

    # --- embedded app script (no direct backend assignments) ---
    script = tmp_path / "history_kis_app.py"
    script.write_text(
        """
import streamlit as st

st.session_state["data_source"] = "backend"
if "hist_calls" not in st.session_state:
    st.session_state["hist_calls"] = []

from app.ui.views import history

history.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=15)
    assert not at.exception
    assert any(item.value == "KIS 날짜별 주문내역" for item in at.subheader)

    at.button[0].click().run(timeout=15)

    assert not at.exception
    assert at.session_state["hist_calls"]
    start_date, end_date = at.session_state["hist_calls"][0]
    assert len(start_date) == 8
    assert len(end_date) == 8
    assert len(at.dataframe) >= 1
