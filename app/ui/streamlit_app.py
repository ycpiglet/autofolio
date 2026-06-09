from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from app.agents.research_agent import ResearchAgent
from app.brokers.factory import create_broker_client
from app.common.enums import OrderType, Side, SymbolRole
from app.config.settings import settings
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.engine.live_trading_engine import LiveTradingEngine
from app.notification.telegram_notifier import TelegramNotifier


st.set_page_config(page_title="KIS AutoTrading MVP", layout="wide")

initialize_database(settings.db_path)
repo = Repository(settings.db_path)


@st.cache_resource
def get_broker():
    return create_broker_client()


broker = get_broker()
notifier = TelegramNotifier()
engine = LiveTradingEngine(broker=broker, repo=repo, notifier=notifier)
research_agent = ResearchAgent()


def bool_state(key: str) -> bool:
    return repo.get_system_state(key, "false") == "true"


def set_bool_state(key: str, value: bool) -> None:
    repo.set_system_state(key, "true" if value else "false")


st.title("KIS 기반 개인용 국장 자동매매 MVP")

with st.sidebar:
    st.subheader("System")
    st.write(f"Environment: `{settings.kis_env}`")
    auto_enabled = st.toggle(
        "Auto Trading Enabled",
        value=bool_state("auto_trading_enabled"),
    )
    set_bool_state("auto_trading_enabled", auto_enabled)

    kill_switch_active = bool_state("kill_switch_active")
    st.write(f"Kill Switch: `{kill_switch_active}`")

    if st.button("KILL SWITCH: 자동매매 중단", type="primary"):
        set_bool_state("auto_trading_enabled", False)
        set_bool_state("kill_switch_active", True)
        st.error("Kill Switch activated. Auto trading disabled.")
        notifier.send_message("[KILL SWITCH] Auto trading disabled.")

    if st.button("Kill Switch 해제"):
        set_bool_state("kill_switch_active", False)
        st.success("Kill Switch released. Auto trading remains OFF by default.")

tabs = st.tabs([
    "Overview",
    "Whitelist",
    "Conditions",
    "Live Monitor",
    "Orders",
    "Research Agent",
])

with tabs[0]:
    st.header("Overview")
    st.write("자동매매는 기본 OFF다. 테스트 단계에서는 Mock Broker로 주문 흐름을 먼저 검증한다.")

    col1, col2, col3 = st.columns(3)
    col1.metric("KIS_ENV", settings.kis_env)
    col2.metric("Auto Trading", str(bool_state("auto_trading_enabled")))
    col3.metric("Kill Switch", str(bool_state("kill_switch_active")))

    if st.button("Run Engine Once"):
        messages = engine.run_once()
        for msg in messages:
            st.write(msg)

with tabs[1]:
    st.header("Whitelist")

    with st.form("add_symbol_form"):
        symbol = st.text_input("종목 코드", value="005930")
        name = st.text_input("종목명", value="삼성전자")
        role = st.selectbox("역할", [r.value for r in SymbolRole])
        enabled = st.checkbox("활성화", value=True)
        submitted = st.form_submit_button("화이트리스트 저장")
        if submitted:
            repo.add_whitelist_symbol(
                WhitelistSymbol(
                    symbol=symbol.strip(),
                    name=name.strip(),
                    market="KRX",
                    role=role,
                    enabled=enabled,
                )
            )
            st.success("저장 완료")

    items = repo.list_whitelist_symbols()
    st.dataframe(pd.DataFrame(items), use_container_width=True)

with tabs[2]:
    st.header("Conditions")

    whitelist = repo.list_whitelist_symbols(enabled_only=True)
    if not whitelist:
        st.warning("먼저 화이트리스트 종목을 등록해줘.")
    else:
        symbol_options = {f"{x['symbol']} - {x['name']}": x["symbol"] for x in whitelist}
        with st.form("add_condition_form"):
            label = st.selectbox("종목", list(symbol_options.keys()))
            side = st.selectbox("매수/매도", [Side.BUY.value, Side.SELL.value])
            target_price = st.number_input("목표 가격", min_value=1.0, value=70000.0, step=100.0)
            quantity = st.number_input("수량", min_value=1, value=1, step=1)
            order_type = st.selectbox("주문 방식", [OrderType.LIMIT.value, OrderType.MARKET.value])
            allow_market_fallback = st.checkbox("지정가 미체결 시 시장가 fallback 허용", value=False)
            auto_enabled = st.checkbox("자동주문 ON", value=False)
            submitted = st.form_submit_button("조건 저장")
            if submitted:
                condition_id = repo.add_trade_condition(
                    symbol=symbol_options[label],
                    side=side,
                    target_price=float(target_price),
                    quantity=int(quantity),
                    order_type=order_type,
                    allow_market_fallback=allow_market_fallback,
                    auto_enabled=auto_enabled,
                    created_by="USER",
                )
                st.success(f"조건 저장 완료: id={condition_id}")

    conditions = repo.list_conditions()
    st.dataframe(pd.DataFrame(conditions), use_container_width=True)

with tabs[3]:
    st.header("Live Monitor")
    whitelist = repo.list_whitelist_symbols(enabled_only=True)
    rows = []
    for item in whitelist:
        try:
            quote = broker.get_current_price(item["symbol"])
            rows.append({
                "symbol": item["symbol"],
                "name": item["name"],
                "role": item["role"],
                "price": quote.price,
            })
        except Exception as exc:
            rows.append({
                "symbol": item["symbol"],
                "name": item["name"],
                "role": item["role"],
                "price": None,
                "error": str(exc),
            })
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

with tabs[4]:
    st.header("Orders")
    logs = repo.list_order_logs(limit=200)
    st.dataframe(pd.DataFrame(logs), use_container_width=True)

with tabs[5]:
    st.header("Research Agent")
    whitelist = repo.list_whitelist_symbols(enabled_only=True)
    if not whitelist:
        st.warning("화이트리스트 종목을 먼저 등록해줘.")
    else:
        symbol_options = {f"{x['symbol']} - {x['name']}": x["symbol"] for x in whitelist}
        label = st.selectbox("분석할 종목", list(symbol_options.keys()), key="agent_symbol")
        side = st.selectbox("제안 방향", [Side.BUY.value, Side.SELL.value], key="agent_side")
        if st.button("조건 제안 받기"):
            symbol = symbol_options[label]
            quote = broker.get_current_price(symbol)
            proposal = research_agent.propose_price_condition(
                symbol=symbol,
                current_price=quote.price,
                side=side,
            )
            st.session_state["proposal"] = proposal

        proposal = st.session_state.get("proposal")
        if proposal:
            st.subheader("제안")
            st.write(proposal)
            st.info("제안 조건은 승인 전 저장되지 않으며, 저장되더라도 자동주문은 OFF다.")
            if st.button("제안 조건 저장"):
                condition_id = repo.add_trade_condition(
                    symbol=proposal.symbol,
                    side=proposal.side,
                    target_price=proposal.target_price,
                    quantity=proposal.quantity,
                    order_type=proposal.order_type,
                    allow_market_fallback=proposal.allow_market_fallback,
                    auto_enabled=False,
                    created_by="AGENT",
                    rationale=proposal.rationale,
                    risk_note=proposal.risk_note,
                )
                st.success(f"에이전트 제안 조건 저장 완료: id={condition_id}, auto_enabled=false")
