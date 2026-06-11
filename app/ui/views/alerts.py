"""알림."""
from __future__ import annotations

import streamlit as st

from app.ui.components import ui
from app.ui.mock import data as mock_data


def render() -> None:
    st.header("🔔 알림")
    live = st.session_state.get("data_source") == "backend"

    st.subheader("피드")
    if live:
        _live_feed()
    else:
        _mock_feed()

    st.divider()
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


def _severity_label(level: str) -> str:
    return {
        "error": "[BLOCK] Critical",
        "warn": "[CHECK] Warning",
        "info": "[OK] Info",
    }.get(level, "[OFF] Unknown")


def _next_action(level: str, source: str) -> str:
    if level == "error":
        return "킬스위치와 주문로그 확인"
    if level == "warn" or source in {"리스크", "서킷브레이커"}:
        return "리스크 한도와 exposure 확인"
    if source == "체결":
        return "체결 수량과 평균가 대조"
    return "상태 모니터링"


def _mock_feed() -> None:
    alerts = mock_data.alerts_feed()
    for level in ("error", "warn", "info"):
        rows = [a for a in alerts if a.get("level") == level]
        if not rows:
            continue
        with st.container(border=True):
            st.markdown(f"**{_severity_label(level)}**")
            for a in rows:
                source = a.get("유형", "system")
                message = f"{a['msg']} · next: {_next_action(level, source)}"
                st.write(ui.console_row(a.get("t", "-"), source, message))


def _live_feed() -> None:
    """라이브: 최근 주문로그를 알림 피드 형식으로 표시."""
    try:
        from app.ui import backend

        logs = backend.list_order_logs(limit=50)
        if logs.empty:
            st.caption("🟢 라이브 — 주문 이력이 없습니다.")
            return

        st.caption(f"라이브 — 최근 주문로그 {len(logs)}건")
        status_level = {
            "FILLED": "info",
            "CANCELED": "warn",
            "FAILED": "error",
            "PENDING": "warn",
            "REQUESTED": "info",
        }
        for _, row in logs.iterrows():
            status = str(row.get("order_status", "UNKNOWN"))
            level = status_level.get(status, "warn")
            ts = str(row.get("created_at", ""))[:16]
            side = row.get("side", "")
            sym = row.get("symbol", "")
            qty = row.get("quantity", "")
            price = row.get("order_price") or row.get("current_price")
            price_str = f"@{float(price):,.0f}" if price else ""
            message = (
                f"{_severity_label(level)} · {sym} {side} {qty}주 {price_str} — "
                f"{status} · next: {_next_action(level, 'order-log')}"
            )
            st.write(ui.console_row(ts or "-", "order-log", message))
    except Exception as exc:  # noqa: BLE001
        st.warning(f"라이브 피드 오류: {exc}")
