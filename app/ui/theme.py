"""UI 테마·포맷 헬퍼 (P1.0a). 백엔드 비의존."""
from __future__ import annotations

import streamlit as st

APP_NAME = "Autofolio"
APP_ICON = "📈"

# 자율성 레벨 (PRODUCT_BLUEPRINT §2)
MODES = ["L0", "L1", "L2", "L3", "L4"]
MODE_LABELS = {
    "L0": "관찰",
    "L1": "자문",
    "L2": "반자동",
    "L3": "감독형 자동",
    "L4": "완전자동",
}


def configure_page() -> None:
    st.set_page_config(
        page_title=f"{APP_NAME} — 개인 자산운용 OS",
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def fmt_won(value: float) -> str:
    return f"₩{value:,.0f}"


def fmt_pct(value: float, signed: bool = True) -> str:
    sign = "+" if signed and value > 0 else ""
    return f"{sign}{value:.2f}%"


def pnl_color(value: float, kr: bool = True) -> str:
    """한국 관습: 상승=빨강, 하락=파랑. kr=False면 서구식."""
    up, down = ("red", "blue") if kr else ("green", "red")
    if value > 0:
        return up
    if value < 0:
        return down
    return "gray"


def pnl_md(value: float, text: str | None = None, kr: bool = True) -> str:
    color = pnl_color(value, kr)
    return f":{color}[{text if text is not None else fmt_pct(value)}]"
