from __future__ import annotations


def test_top_bar_labels_backend_data_source(tmp_path):
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "top_bar_backend_app.py"
    script.write_text(
        """
import streamlit as st

from app.ui import state
from app.ui.components import ui

state.init_state()
st.session_state["authed"] = True
st.session_state["demo"] = True
st.session_state["data_source"] = "backend"

ui.top_bar()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=10)

    assert not at.exception
    text = " ".join(str(node.value) for node in [*at.caption, *at.markdown])
    assert "라이브 데이터" in text
    assert "mock 데이터" not in text


def test_top_bar_labels_demo_data_source(tmp_path):
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "top_bar_demo_app.py"
    script.write_text(
        """
import streamlit as st

from app.ui import state
from app.ui.components import ui

state.init_state()
st.session_state["authed"] = True
st.session_state["demo"] = True
st.session_state["data_source"] = "demo"

ui.top_bar()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=10)

    assert not at.exception
    text = " ".join(str(node.value) for node in [*at.caption, *at.markdown])
    assert "데모 모드" in text
    assert "mock 데이터" in text
