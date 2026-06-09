"""Autofolio UI-First 제품 셸 (P1.0a).

mock 데이터로 동작하는 멀티페이지 Streamlit 앱.
실행: run_ui.bat  (또는  set PYTHONPATH=%CD% && streamlit run app/ui/autofolio_app.py)
P1.1에서 app/ui/mock 을 실제 어댑터로 교체하면 화면은 그대로 동작한다.
기존 MVP UI는 app/ui/streamlit_app.py 로 별도 유지된다.
"""
from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from app.ui import auth, state, theme
from app.ui.components import ui
from app.ui.views import (
    agents,
    alerts,
    analysis,
    history,
    home,
    login,
    portfolio,
    settings,
    trade,
)

theme.configure_page()
state.init_state()

# Google OIDC 세션 동기화 (st.login 성공 시)
if auth.oidc_logged_in() and not st.session_state.authed:
    state.login("Google", auth.oidc_email())

# --- 로그인 게이트 ---
if not st.session_state.authed:
    login.render()
    st.stop()

# --- 상단 상태바 ---
ui.top_bar()

# --- 사이드바: 사용자 + 로그아웃 ---
with st.sidebar:
    user = st.session_state.user or {}
    st.caption(f"👤 {user.get('name', '?')} · {user.get('provider', '')}")
    st.radio(
        "데이터 소스",
        ["demo", "backend"],
        key="data_source",
        horizontal=True,
        format_func=lambda x: "데모(mock)" if x == "demo" else "라이브",
        help="라이브 = Mock 브로커 + 실제 SQLite (증권 키 불필요)",
    )
    if st.button("로그아웃", width="stretch"):
        state.logout()
        st.rerun()

# --- 멀티페이지 내비게이션 ---
navigation = st.navigation(
    {
        "운용": [
            st.Page(home.render, title="홈", icon="🏠", url_path="home", default=True),
            st.Page(portfolio.render, title="포트폴리오", icon="💼", url_path="portfolio"),
            st.Page(trade.render, title="매매 / 주문", icon="🧾", url_path="trade"),
            st.Page(history.render, title="내역 · 손익", icon="📒", url_path="history"),
        ],
        "인텔리전스": [
            st.Page(analysis.render, title="분석", icon="📊", url_path="analysis"),
            st.Page(agents.render, title="에이전트", icon="🤖", url_path="agents"),
        ],
        "운영": [
            st.Page(alerts.render, title="알림", icon="🔔", url_path="alerts"),
            st.Page(settings.render, title="설정 · 연동", icon="⚙️", url_path="settings"),
        ],
    }
)
navigation.run()
