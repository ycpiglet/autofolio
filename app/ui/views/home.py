"""홈 / 대시보드."""
from __future__ import annotations

import streamlit as st

from app.ui import theme
from app.ui.components import ui
from app.ui.mock import data


def _kpis() -> dict:
    """KPI 딕셔너리 — data_source=='backend' 면 라이브, 아니면 mock.

    라이브 조회 실패 시 mock으로 안전 폴백한다.
    """
    if st.session_state.get("data_source") == "backend":
        try:
            from app.ui import backend

            return backend.kpis()
        except Exception as exc:  # noqa: BLE001 — UI 폴백
            st.warning(f"라이브 KPI 조회 실패 — 데모 데이터로 대체합니다: {exc}")
    return data.kpis()


def _recent_fills() -> "pd.DataFrame":  # type: ignore[name-defined]
    """최근 체결 내역 — data_source=='backend' 면 라이브, 아니면 mock.

    라이브 조회 실패 시 mock으로 안전 폴백한다.
    """
    if st.session_state.get("data_source") == "backend":
        try:
            from app.ui import backend

            return backend.recent_fills()
        except Exception as exc:  # noqa: BLE001 — UI 폴백
            st.warning(f"라이브 체결 조회 실패 — 데모 데이터로 대체합니다: {exc}")
    return data.recent_fills()


def _holdings_df() -> "pd.DataFrame":  # type: ignore[name-defined]
    """Holdings table for the home view.

    Backend mode should use the same live holdings source as the portfolio page,
    otherwise post-trade sync can be hidden by demo data.
    """
    if st.session_state.get("data_source") == "backend":
        try:
            from app.ui import backend

            return backend.holdings_df(include_dividends=False)
        except Exception as exc:  # noqa: BLE001
            st.warning(f"라이브 보유 종목 조회 실패 — 데모 데이터로 대체합니다: {exc}")
    return data.holdings_df()


def _market_indices() -> "pd.DataFrame":  # type: ignore[name-defined]
    if st.session_state.get("data_source") == "backend":
        try:
            from app.ui import backend

            return backend.market_indices_df()
        except Exception as exc:  # noqa: BLE001
            st.warning(f"시장 지수 조회 실패: {exc}")
    import pandas as pd
    return pd.DataFrame(columns=["name", "code", "price", "change", "change_rate"])


def _handle_approve(proposal_id: str, proposal_row) -> None:
    """승인 핸들러 — 조건 등록(백엔드 모드) 또는 데모 피드백."""
    st.session_state.setdefault("handled_proposals", set()).add(proposal_id)
    if st.session_state.get("data_source") == "backend":
        try:
            from app.ui import backend
            # symbol: proposals from data.proposals() carry 종목(display name); 티커 used when available.
            cid = backend.add_condition(
                symbol=str(proposal_row.get("티커") or proposal_row.get("종목", "")),
                side="BUY" if proposal_row.get("방향") == "매수" else "SELL",
                target_price=float(proposal_row.get("목표가", 0)),
                quantity=int(proposal_row.get("수량", 1)),
                order_type="LIMIT",
                auto_enabled=False,
                created_by="HOME_IC",
                rationale=str(proposal_row.get("근거", "")),
            )
            st.success(f"✅ {proposal_row.get('종목', '?')} 조건 등록 완료 (id={cid}). 매매 화면에서 자동주문을 활성화하세요.")
        except Exception as exc:  # noqa: BLE001
            st.success(f"✅ {proposal_row.get('종목', '?')} 승인됨 (조건 저장 실패: {exc})")
    else:
        st.success(f"✅ {proposal_row.get('종목', '?')} 승인됨 (데모 모드 — 조건은 저장되지 않습니다).")


def _handle_reject(proposal_id: str, proposal_row) -> None:
    """거부 핸들러 — 대기 목록에서 제거 + 피드백."""
    st.session_state.setdefault("handled_proposals", set()).add(proposal_id)
    st.info(f"🚫 {proposal_row.get('종목', '?')} 제안 거부됨.")


def render() -> None:
    ui.page_header("🏠 홈", "포트폴리오 한눈에 보기")

    indices = _market_indices()
    if not indices.empty:
        cols = st.columns(min(len(indices), 4))
        for col, (_, row) in zip(cols, indices.iterrows()):
            price = row.get("price")
            change = row.get("change")
            rate = row.get("change_rate")
            delta = None
            if change is not None and rate is not None:
                delta = f"{change:,.2f} ({rate:.2f}%)"
            col.metric(str(row.get("name")), f"{price:,.2f}" if price is not None else "-", delta)

    with st.spinner("불러오는 중…"):
        k = _kpis()
        holdings = _holdings_df()

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

    if st.session_state.get("data_source") == "backend":
        try:
            from app.ui import backend
            curve = backend.asset_curve()
            st.line_chart(curve["자산"], height=260)
        except Exception:  # noqa: BLE001
            st.line_chart(data.asset_curve(), y="자산", height=260)
    else:
        st.line_chart(data.asset_curve(), y="자산", height=260)

    left, right = st.columns([3, 2])
    with left:
        st.subheader("오늘의 제안 (승인 대기)")
        handled = st.session_state.get("handled_proposals", set())
        pending = data.proposals()
        pending = pending[~pending["id"].isin(handled)]
        if pending.empty:
            st.caption("처리 대기 중인 제안이 없습니다.")
        for _, p in pending.iterrows():
            with st.container(border=True):
                a, b = st.columns([5, 2])
                a.markdown(f"**{p['종목']}** · {p['방향']} · 목표 {p['목표가']:,} · {p['수량']}주")
                a.caption(f"🤖 {p['에이전트']} · 확신도 {p['확신도']} — {p['근거']}")
                if b.button("승인", key=f"ap_{p['id']}", width="stretch"):
                    _handle_approve(p["id"], p)
                if b.button("거부", key=f"rj_{p['id']}", width="stretch"):
                    _handle_reject(p["id"], p)
    with right:
        st.subheader("최근 체결")
        st.dataframe(_recent_fills(), hide_index=True, width="stretch")

        # 와치리스트 (라이브 or mock)
        st.subheader("와치리스트")
        if st.session_state.get("data_source") == "backend":
            try:
                from app.ui import backend
                wl = backend.watchlist()
                if not wl.empty:
                    wl["현재가"] = wl["price"].apply(lambda p: f"{p:,.0f}" if p else "-")
                    st.dataframe(wl[["symbol", "name", "현재가"]], hide_index=True, width="stretch")
                else:
                    st.caption("화이트리스트가 비어있습니다.")
            except Exception:  # noqa: BLE001
                st.dataframe(data.watchlist(), hide_index=True, width="stretch")
        else:
            st.dataframe(data.watchlist(), hide_index=True, width="stretch")

        st.subheader("알림")
        for a in data.alerts_feed()[:4]:
            st.caption(f"`{a['t']}` {a['msg']}")
