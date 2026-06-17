"""에이전트 — 팀 트리 + 실시간 챗 + 투자위원회(IC). (P2)"""
from __future__ import annotations

import streamlit as st

from app.ui import agents_runtime as ar
from app.ui import ic as ic_mod
from app.ui.mock import data


def render() -> None:
    st.header("🤖 에이전트")
    ok, info = ar.available()
    agent_count = len(ar.list_agents())
    if ok:
        st.caption(f"🟢 에이전트 실연결 (Anthropic · {info}) · {agent_count}개 에이전트 로드")
    else:
        st.caption(f"🟡 데모 모드 — {info}. `.env`에 ANTHROPIC_API_KEY 설정 시 실연결. · {agent_count}개 에이전트 등록")

    chat_tab, ic_tab = st.tabs(["에이전트 채팅", "투자위원회 (IC)"])
    with chat_tab:
        _chat()
    with ic_tab:
        _ic()


def _chat() -> None:
    tree = data.agents_tree()
    options: list[str] = []
    for team, members in tree.items():
        options.extend(f"{m}  ·  {team}" for m in members)

    left, right = st.columns([2, 3])
    with left:
        selected = st.selectbox("에이전트 선택", options)
        for team, members in tree.items():
            with st.expander(team):
                for m in members:
                    st.write("•", m)

    with right:
        agent = selected.split("  ·  ")[0]
        st.subheader(f"💬 {agent}")
        q = st.text_input("질문", placeholder=f"{agent} 에게 질문…", key="chat_q")
        if st.button("전송", type="primary", key="chat_send") and q:
            with st.spinner("생각 중…"):
                st.session_state["chat_ans"] = {"q": q, "a": ar.ask(agent, q)}
        ans = st.session_state.get("chat_ans")
        if ans:
            with st.chat_message("user"):
                st.write(ans["q"])
            with st.chat_message("assistant"):
                st.markdown(ans["a"])


def _ic() -> None:
    st.caption("전문가 의견 → 악마의 변호인 → 리스크 → PM 종합 → CIO 결정 → 결정 로그")
    topic = st.text_input("안건 (종목/주제)", placeholder="예: TIGER 미국S&P500 비중 확대", key="ic_topic")
    panel = st.multiselect("참여 전문가", ar.list_agents(), default=ic_mod.DEFAULT_PANEL, key="ic_panel")

    if st.button("📋 투자위원회 소집", type="primary", key="ic_run") and topic:
        with st.status("위원회 진행 중…", expanded=True) as status:
            result = ic_mod.run_ic(topic, panel or None, progress=lambda label: status.write(f"• {label}"))
            status.update(label="완료", state="complete")
        st.session_state["ic_result"] = result

    result = st.session_state.get("ic_result")
    if result:
        st.success(f"결정 로그 저장: `{result['path']}`")
        st.subheader("🏛️ CIO 결정")
        st.markdown(result["decision"])

        # IC 결정 → 매매 조건 자동 연결
        if st.session_state.get("data_source") == "backend":
            cond = ic_mod.extract_condition_from_ic(result)
            if cond:
                st.info(
                    f"📌 자동 파싱된 조건: **{cond['symbol']}** {cond['side']} "
                    f"{cond['quantity']}주 @ {cond['target_price']:,.0f}"
                )
                if st.button("✅ 이 조건으로 매매 등록 (사람 확인)", key="ic_apply_cond"):
                    from app.services import backend
                    cid = backend.add_condition(
                        symbol=cond["symbol"],
                        side=cond["side"],
                        target_price=cond["target_price"],
                        quantity=cond["quantity"],
                        order_type="LIMIT",
                        auto_enabled=False,   # 자동주문은 별도 ON 필요
                        created_by="IC",
                        rationale=result["decision"][:300],
                    )
                    st.success(f"✅ 조건 등록 완료 (id={cid}). 자동주문은 매매 화면에서 별도 활성화하세요.")
            else:
                st.caption("ℹ️ 결정문에서 종목코드/목표가/방향 자동 파싱 불가 — 매매 화면에서 수동 등록.")

        # T-25: execution-trader 실행 계획 요청
        if st.session_state.get("data_source") == "backend":
            with st.expander("⚡ Execution Trader에 실행 계획 요청"):
                st.caption("IC 결정을 바탕으로 Execution Trader 에이전트가 최적 실행 방법을 제안합니다.")
                exec_symbol = st.text_input("종목코드", placeholder="005930", key="exec_sym")
                exec_qty = st.number_input("목표 수량", min_value=1, value=1, key="exec_qty")
                exec_side = st.radio("방향", ["BUY", "SELL"], horizontal=True, key="exec_side")
                if st.button("📋 실행 계획 요청", key="exec_plan") and exec_symbol:
                    with st.spinner("Execution Trader 분석 중…"):
                        context = (
                            f"IC 결정: {result['decision'][:500]}\n"
                            f"종목: {exec_symbol}, 방향: {exec_side}, 수량: {exec_qty}주\n"
                            f"현재 환경: {st.session_state.get('data_source','demo')}"
                        )
                        plan = ar.ask(
                            "execution-trader",
                            f"위 IC 결정에 따라 {exec_symbol} {exec_side} {exec_qty}주의 최적 실행 계획을 수립해주세요.",
                            context,
                        )
                        st.session_state["exec_plan_result"] = plan
                plan_result = st.session_state.get("exec_plan_result")
                if plan_result:
                    st.markdown("**Execution Trader 실행 계획:**")
                    st.markdown(plan_result)
                    st.caption("⚠️ 이 계획은 참고용입니다. 실제 주문은 매매 화면에서 직접 진행하세요.")

        with st.expander("전체 회의록"):
            for t in result["transcript"]:
                st.markdown(f"**{t['role']}** (`{t['agent']}`)")
                st.markdown(t["text"])
                st.divider()

    recent = ic_mod.list_decisions()
    if recent:
        st.subheader("최근 결정")
        for d in recent:
            st.caption(f"`{d['file']}`")
