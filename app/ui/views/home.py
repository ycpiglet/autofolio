"""홈 / 대시보드."""
from __future__ import annotations

import streamlit as st

from app.ui import theme
from app.ui.components import ui
from app.ui.mock import data
from app.brokers.kis.constants import KIS_INDEX_LABELS


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


def _holdings_df():
    """보유 종목 — backend 소스가 가능하면 실제 어댑터, 아니면 mock."""
    if st.session_state.get("data_source") == "backend":
        try:
            from app.ui import backend

            return backend.holdings_df()
        except Exception as exc:  # noqa: BLE001
            st.warning(f"라이브 보유 조회 실패 — 데모 데이터로 대체합니다: {exc}")
    return data.holdings_df()


def _asset_curve():
    """자산 곡선 — backend 실패 시 mock 곡선으로 안전 폴백."""
    if st.session_state.get("data_source") == "backend":
        try:
            from app.ui import backend

            return backend.asset_curve()
        except Exception as exc:  # noqa: BLE001
            st.warning(f"라이브 자산 곡선 조회 실패 — 데모 데이터로 대체합니다: {exc}")
    return data.asset_curve()


def _market_indices() -> list[dict]:
    if st.session_state.get("data_source") != "backend":
        return []
    try:
        from app.ui import backend

        return backend.market_indices()
    except Exception:  # noqa: BLE001
        return []


def _watchlist():
    if st.session_state.get("data_source") == "backend":
        try:
            from app.ui import backend

            return backend.watchlist()
        except Exception:  # noqa: BLE001
            return data.watchlist()
    return data.watchlist()


def _safety_summary() -> dict[str, str]:
    cb_triggered = False
    if st.session_state.get("data_source") == "backend":
        try:
            from app.ui import backend

            cb_triggered = bool(backend.circuit_breaker_status().get("triggered"))
        except Exception:  # noqa: BLE001
            cb_triggered = False
    return ui.build_safety_summary(
        env=st.session_state.get("data_source", "demo"),
        mode=st.session_state.get("mode", "L1"),
        auto=bool(st.session_state.get("auto_enabled", False)),
        kill=bool(st.session_state.get("kill_switch", False)),
        circuit_breaker=cb_triggered,
    )


def render() -> None:
    ui.page_header("🏠 홈", "운영 상태와 포트폴리오 스냅샷")

    with st.spinner("불러오는 중…"):
        k = _kpis()
        holdings = _holdings_df()
        curve = _asset_curve()
        recent_fills = _recent_fills()

    summary = _safety_summary()

    st.subheader("운영 상태")
    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns([2.2, 1.4, 1.4, 1.4, 1.8])
        c1.markdown(f"**환경**  \n{summary['env']}")
        c2.markdown(f"**모드**  \n{summary['mode']}")
        c3.markdown(f"**자동매매**  \n{ui.status_badge(summary['auto'])}")
        c4.markdown(f"**킬스위치**  \n{ui.status_badge(summary['kill'])}")
        c5.markdown(f"**서킷브레이커**  \n{ui.status_badge(summary['circuit_breaker'])}")

    indices = _market_indices()
    if indices:
        st.subheader("시장 상태")
        cols = st.columns(len(indices))
        for col, idx in zip(cols, indices):
            name = KIS_INDEX_LABELS.get(idx["index_code"], idx["index_code"])
            col.metric(
                name,
                f"{idx['price']:,.2f}",
                f"{idx['change']:+.2f} ({idx['change_pct']:+.2f}%)",
            )

    if holdings.empty:
        ui.empty_state("아직 보유 종목이 없습니다", "설정에서 증권계좌를 연동하고 매매를 시작하세요.")
        return

    kr = st.session_state.get("pnl_kr_colors", True)
    st.subheader("계좌 KPI")
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

    left, right = st.columns([2.4, 1.6])
    with left:
        st.subheader("자산 곡선")
        st.line_chart(curve, y="자산", height=260)
    with right:
        st.subheader("보유 요약")
        cols = ["종목", "자산군", "평가금액", "비중", "손익률"]
        st.dataframe(
            holdings[cols].sort_values("비중", ascending=False).head(6),
            hide_index=True,
            width="stretch",
            column_config={
                "평가금액": st.column_config.NumberColumn(format="₩%d"),
                "비중": st.column_config.NumberColumn(format="%.1f%%"),
                "손익률": st.column_config.NumberColumn(format="%.1f%%"),
            },
        )

    left, right = st.columns([3, 2])
    with left:
        st.subheader("검토 대기 제안")
        for _, p in data.proposals().iterrows():
            with st.container(border=True):
                st.markdown(f"**{p['종목']}** · {p['방향']} · 목표 {p['목표가']:,} · {p['수량']}주")
                st.caption(f"🤖 {p['에이전트']} · 확신도 {p['확신도']} — {p['근거']}")
                st.caption("주문 검토와 실행은 매매 / 주문 화면에서만 진행합니다.")
    with right:
        st.subheader("최근 체결")
        st.dataframe(recent_fills, hide_index=True, width="stretch")

        st.subheader("와치리스트")
        wl = _watchlist()
        if wl.empty:
            st.caption("화이트리스트가 비어있습니다.")
        elif {"symbol", "name", "price"} <= set(wl.columns):
            view = wl[["symbol", "name", "price"]].copy()
            view["price"] = view["price"].apply(lambda p: f"{p:,.0f}" if p else "-")
            st.dataframe(view.rename(columns={"price": "현재가"}), hide_index=True, width="stretch")
        else:
            st.dataframe(wl, hide_index=True, width="stretch")

    st.subheader("알림")
    for a in data.alerts_feed()[:5]:
        marker = "[CHECK]" if a.get("level") == "warn" else "[OK]"
        st.caption(f"`{a['t']}` {marker} {a['유형']} · {a['msg']}")
