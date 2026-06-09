"""홈 / 대시보드."""
from __future__ import annotations

import streamlit as st

from app.ui import theme
from app.ui.components import ui
from app.ui.mock import data


def render() -> None:
    ui.page_header("🏠 홈", "포트폴리오 한눈에 보기")

    with st.spinner("불러오는 중…"):
        k = data.kpis()
        holdings = data.holdings_df()

    if holdings.empty:
        ui.empty_state("아직 보유 종목이 없습니다", "설정에서 증권계좌를 연동하고 매매를 시작하세요.")
        return

    kr = st.session_state.get("pnl_kr_colors", True)
    ui.kpi_cards(
        [
            ("총자산", theme.fmt_won(k["총자산"]), None),
            ("일손익", theme.fmt_pct(k["일손익률"]), theme.fmt_pct(k["일손익률"])),
            ("누적손익", theme.fmt_pct(k["누적손익률"]), None),
            ("현금비중", f'{k["현금비중"]:.0f}%', None),
        ]
    )
    pnl = int(k["평가손익"])
    st.markdown("평가손익  " + theme.pnl_md(pnl, theme.fmt_won(pnl), kr))

    st.line_chart(data.asset_curve(), y="자산", height=260)

    left, right = st.columns([3, 2])
    with left:
        st.subheader("오늘의 제안 (승인 대기)")
        for _, p in data.proposals().iterrows():
            with st.container(border=True):
                a, b = st.columns([5, 2])
                a.markdown(f"**{p['종목']}** · {p['방향']} · 목표 {p['목표가']:,} · {p['수량']}주")
                a.caption(f"🤖 {p['에이전트']} · 확신도 {p['확신도']} — {p['근거']}")
                b.button("승인", key=f"ap_{p['id']}", width="stretch")
                b.button("거부", key=f"rj_{p['id']}", width="stretch")
    with right:
        st.subheader("최근 체결")
        st.dataframe(data.recent_fills(), hide_index=True, width="stretch")
        st.subheader("알림")
        for a in data.alerts_feed()[:4]:
            st.caption(f"`{a['t']}` {a['msg']}")
