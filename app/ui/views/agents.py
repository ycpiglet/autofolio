"""에이전트 — 팀 트리 + 실시간 챗 + 투자위원회(IC). (P2)"""
from __future__ import annotations

import streamlit as st

from app.ui import agents_runtime as ar
from app.ui import ic as ic_mod
from app.ui.mock import data


def render() -> None:
    st.header("🤖 에이전트")
    ok, info = ar.available()
    if ok:
        st.caption(f"🟢 에이전트 실연결 (Anthropic · {info})")
    else:
        st.caption(f"🟡 데모 모드 — {info}. `.env`에 ANTHROPIC_API_KEY 설정 시 실연결.")

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
                    from app.ui import backend
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
