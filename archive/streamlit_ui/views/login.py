"""로그인 — ID/PW(로컬) · 소셜 버튼 · 게스트. 최대한 간단하게."""
from __future__ import annotations

import streamlit as st

from app.ui import auth, state, theme


def render() -> None:
    st.markdown(f"# {theme.APP_ICON} {theme.APP_NAME}")
    st.caption("에이전트 팀이 운용하는 개인용 멀티에셋 자동매매 OS")
    st.write("")

    mid = st.columns([1, 1.3, 1])[1]
    with mid:
        with st.container(border=True):
            st.subheader("로그인 / 가입")
            with st.form("login_form", border=False):
                username = st.text_input("ID", placeholder="아이디")
                password = st.text_input("비밀번호", type="password", placeholder="비밀번호")
                submitted = st.form_submit_button("시작하기", type="primary", width="stretch")
            if submitted:
                ok, msg = auth.login_or_register(username, password)
                if ok:
                    state.login("local", username.strip())
                    st.rerun()
                else:
                    st.error(msg)
            st.caption("처음 보는 ID면 그 비밀번호로 바로 가입됩니다. (비밀번호는 해시로 암호화 저장)")

            st.divider()
            if auth.oidc_configured():
                if st.button("G  Google로 로그인", width="stretch"):
                    st.login()
            else:
                with st.expander("G  Google로 로그인 — 1회 설정 필요"):
                    st.caption(
                        "`.streamlit/secrets.toml`에 `[auth]`를 채우면 버튼 1클릭으로 로그인됩니다. "
                        "양식은 `secrets.toml.example` 참고."
                    )
            st.button("🟡  카카오 (준비중)", width="stretch", disabled=True)
            st.button("🟢  네이버 (준비중)", width="stretch", disabled=True)

            st.divider()
            if st.button("게스트(데모)로 둘러보기 →", width="stretch"):
                state.login("게스트", "게스트", demo=True)
                st.rerun()
