"""알림."""
from __future__ import annotations

import streamlit as st

from app.ui.mock import data as mock_data


def render() -> None:
    st.header("🔔 알림")
    live = st.session_state.get("data_source") == "backend"

    st.subheader("채널")
    channels = [("Telegram", True), ("Kakao", False), ("Discord", False), ("Notion", True), ("Email", True)]
    for col, (name, on) in zip(st.columns(len(channels)), channels):
        col.toggle(name, value=on, key=f"alert_ch_{name}")

    st.subheader("알림 규칙")
    st.multiselect(
        "켜둘 알림",
        ["체결", "가격도달", "조건충족", "리스크한도", "서킷브레이커", "뉴스/공시", "일일요약"],
        default=["체결", "가격도달", "리스크한도", "서킷브레이커"],
    )

    if live:
        _disclosure_panel()

    st.subheader("피드")
    if live:
        _live_feed()
    else:
        icons = {"info": "🟢", "warn": "🟡", "error": "🔴"}
        for a in mock_data.alerts_feed():
            st.write(f"{icons.get(a['level'], '⚪')} `{a['t']}` **{a['유형']}** — {a['msg']}")


def _disclosure_panel() -> None:
    st.subheader("뉴스/공시")
    try:
        from app.ui import backend

        opts = backend.symbol_options()
        if not opts:
            st.caption("화이트리스트가 비어있습니다.")
            return
        c1, c2 = st.columns([2, 1])
        label = c1.selectbox("종목", list(opts.keys()), key="disclosure_symbol")
        days = c2.number_input("조회일", min_value=1, max_value=30, value=1, key="disclosure_days")
        symbol = opts[label]
        if st.button("공시 확인", key="disclosure_refresh"):
            result = backend.refresh_disclosure_gate(symbol, days=int(days), notify=True)
            st.session_state["disclosure_result"] = result

        result = st.session_state.get("disclosure_result")
        if not result or result.get("symbol") != symbol:
            state = backend.disclosure_gate_state(symbol)
            if state.get("blocked"):
                st.warning(f"차단 중: {state.get('reason', '')}")
            return

        if result.get("blocked"):
            st.warning(f"차단 중: {result.get('reason', '')}")
        else:
            st.success("중대 공시 없음")
        df = result.get("disclosures")
        if df is not None and not df.empty:
            display = df[["date", "time", "title", "category", "severity", "source"]].rename(
                columns={
                    "date": "일자",
                    "time": "시간",
                    "title": "제목",
                    "category": "분류",
                    "severity": "등급",
                    "source": "출처",
                }
            )
            st.dataframe(display, hide_index=True, width="stretch")
    except Exception as exc:  # noqa: BLE001
        st.warning(f"공시 조회 실패: {exc}")


def _live_feed() -> None:
    """라이브: 최근 주문로그를 알림 피드 형식으로 표시."""
    try:
        from app.ui import backend

        logs = backend.list_order_logs(limit=50)
        if logs.empty:
            st.caption("🟢 라이브 — 주문 이력이 없습니다.")
            return

        st.caption(f"🟢 라이브 — 최근 주문로그 {len(logs)}건")
        status_icon = {
            "FILLED": "✅",
            "CANCELED": "🚫",
            "FAILED": "❌",
            "PENDING": "⏳",
            "REQUESTED": "📤",
        }
        for _, row in logs.iterrows():
            icon = status_icon.get(str(row.get("order_status", "")), "⚪")
            ts = str(row.get("created_at", ""))[:16]
            side = row.get("side", "")
            sym = row.get("symbol", "")
            qty = row.get("quantity", "")
            price = row.get("order_price") or row.get("current_price")
            price_str = f"@{float(price):,.0f}" if price else ""
            st.write(f"{icon} `{ts}` **{sym}** {side} {qty}주 {price_str} — {row.get('order_status', '')}")
    except Exception as exc:  # noqa: BLE001
        st.warning(f"라이브 피드 오류: {exc}")
