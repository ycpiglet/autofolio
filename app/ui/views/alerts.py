"""알림."""
from __future__ import annotations

import streamlit as st

from app.ui.mock import data


def render() -> None:
    st.header("🔔 알림")

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

    st.subheader("피드")
    icons = {"info": "🟢", "warn": "🟡", "error": "🔴"}
    for a in data.alerts_feed():
        st.write(f"{icons.get(a['level'], '⚪')} `{a['t']}` **{a['유형']}** — {a['msg']}")
