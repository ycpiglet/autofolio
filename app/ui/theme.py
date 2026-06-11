"""UI 테마·포맷 헬퍼 (P1.0a). 백엔드 비의존."""
from __future__ import annotations

import streamlit as st
from typing import Final, Mapping

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

SEMANTIC_TOKENS: Final[Mapping[str, Mapping[str, str]]] = {
    "pnl": {
        "up_kr": "red",
        "down_kr": "blue",
        "flat": "gray",
        "up_western": "green",
        "down_western": "red",
    },
    "env": {
        "mock": "green",
        "paper": "yellow",
        "prod": "red",
        "unknown": "gray",
    },
    "surface": {
        "page": "#0b1021",
        "panel": "#f8fafc",
        "border": "#dbeafe",
    },
}

ENV_LABELS: Final[Mapping[str, str]] = {
    "mock": "Mock (데모)",
    "paper": "Paper (모의투자)",
    "prod": "Live (실전)",
    "unknown": "Unknown",
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


def env_label(env: str | None = None) -> str:
    """mock/paper/prod 환경 라벨을 명확하게 반환한다."""
    key = (env or "unknown").strip().lower()
    return ENV_LABELS.get(key, ENV_LABELS["unknown"])


def pnl_color(value: float, kr: bool = True) -> str:
    """한국 관습: 상승=빨강, 하락=파랑. kr=False면 서구식."""
    if kr:
        up, down = SEMANTIC_TOKENS["pnl"]["up_kr"], SEMANTIC_TOKENS["pnl"]["down_kr"]
    else:
        up, down = SEMANTIC_TOKENS["pnl"]["up_western"], SEMANTIC_TOKENS["pnl"]["down_western"]
    if value > 0:
        return up
    if value < 0:
        return down
    return "gray"


def pnl_md(value: float, text: str | None = None, kr: bool = True) -> str:
    color = pnl_color(value, kr)
    return f":{color}[{text if text is not None else fmt_pct(value)}]"
