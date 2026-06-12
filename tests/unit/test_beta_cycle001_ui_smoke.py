from __future__ import annotations


def test_cycle001_guest_login_reaches_home():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file("app/ui/autofolio_app.py").run(timeout=20)

    assert not at.exception
    assert any(button.label == "게스트(데모)로 둘러보기 →" for button in at.button)

    guest_button = next(button for button in at.button if button.label == "게스트(데모)로 둘러보기 →")
    at = guest_button.click().run(timeout=20)

    assert not at.exception
    assert at.session_state["authed"] is True
    assert at.session_state["demo"] is True
    assert at.session_state["user"]["name"] == "게스트"
    assert any(metric.label == "총자산" for metric in at.metric)
    assert any(item.value == "오늘의 제안 (승인 대기)" for item in at.subheader)


def test_cycle001_demo_views_render_without_exceptions(tmp_path):
    from streamlit.testing.v1 import AppTest

    expected = {
        "home": "오늘의 제안 (승인 대기)",
        "portfolio": "보유 종목",
        "trade": "주문 (모드·게이트 통과 필요)",
        "history": "내역 · 손익",
        "analysis": "백테스트",
        "agents": "ceo",
        "alerts": "피드",
        "settings": "설정 · 연동",
    }

    for view, visible_text in expected.items():
        script = tmp_path / f"beta_{view}_app.py"
        script.write_text(
            f"""
import streamlit as st

from app.ui import state
from app.ui.views import {view}

state.init_state()
st.session_state["authed"] = True
st.session_state["demo"] = True
st.session_state["user"] = {{"name": "게스트", "provider": "게스트"}}
st.session_state["data_source"] = "demo"

{view}.render()
""",
            encoding="utf-8",
        )

        at = AppTest.from_file(str(script)).run(timeout=20)

        assert not at.exception, view
        visible_nodes = [*at.title, *at.header, *at.subheader, *at.markdown]
        page_text = " ".join(str(node.value) for node in visible_nodes)
        button_text = " ".join(button.label for button in at.button)
        metric_text = " ".join(metric.label for metric in at.metric)
        assert visible_text in f"{page_text} {button_text} {metric_text}", view
