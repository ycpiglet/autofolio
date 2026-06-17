"""워치리스트 & 스크리너 뷰.

탭 구성:
  1. 저장형 워치리스트 (Saved Watchlists) — CRUD
  2. 스크리너 (Screener)                  — 필터 + 결과
  3. 알림 규칙 미리보기                    — dry-run ONLY, 주문 제출 없음

Constraints:
- order_flow / OrderFlow / place_order / add_condition / run_engine_once 금지.
- 알림 규칙은 dry-run 미리보기 전용.  evaluate_all_alerts만 호출.
- 비즈니스 로직은 app.services.watchlist_screener에 위임.
"""
from __future__ import annotations

import streamlit as st

from app.services import watchlist_screener


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _live() -> bool:
    return st.session_state.get("data_source") == "backend"


def _whitelist_symbols() -> list[str]:
    """Return a list of ticker symbols from the whitelist (fallback: empty)."""
    try:
        from app.services import backend

        wl = backend.list_whitelist()
        if not wl.empty:
            return wl["symbol"].tolist()
    except Exception:  # noqa: BLE001
        pass
    return []


def _whitelist_options() -> dict[str, str]:
    """Return {label: symbol} dict from the whitelist."""
    try:
        from app.services import backend

        return backend.symbol_options()
    except Exception:  # noqa: BLE001
        return {}


# ---------------------------------------------------------------------------
# Tab 1 — 저장형 워치리스트
# ---------------------------------------------------------------------------


def _tab_watchlists() -> None:
    st.subheader("저장형 워치리스트")

    watchlists = watchlist_screener.list_watchlists()

    if not watchlists:
        st.info("저장된 워치리스트가 없습니다. 아래에서 새로 만드세요.")
    else:
        st.markdown(f"**총 {len(watchlists)}개**")
        for wl in watchlists:
            with st.expander(
                f"{wl['name']}  ({len(wl['symbols'])}종목 · {wl['created_at'][:10]})",
                expanded=False,
            ):
                col1, col2 = st.columns([3, 1])
                new_name = col1.text_input(
                    "이름",
                    value=wl["name"],
                    key=f"wl_name_{wl['id']}",
                )
                available = _whitelist_symbols()
                # seed with persisted symbols even if not in whitelist
                existing = list(wl["symbols"])
                options = list(dict.fromkeys(available + existing))
                new_symbols = st.multiselect(
                    "종목",
                    options=options,
                    default=existing,
                    key=f"wl_syms_{wl['id']}",
                )
                c1, c2 = st.columns(2)
                if c1.button("저장", key=f"wl_save_{wl['id']}"):
                    watchlist_screener.update_watchlist(
                        wl["id"],
                        name=new_name.strip() or None,
                        symbols=new_symbols,
                    )
                    st.success("워치리스트가 업데이트되었습니다.")
                    st.rerun()
                if c2.button("삭제", key=f"wl_del_{wl['id']}", type="secondary"):
                    watchlist_screener.delete_watchlist(wl["id"])
                    st.success(f"'{wl['name']}' 삭제 완료.")
                    st.rerun()

    st.divider()
    st.subheader("새 워치리스트 추가")
    new_wl_name = st.text_input("워치리스트 이름", key="wl_new_name", placeholder="예) 관심 반도체")
    available_syms = _whitelist_symbols()
    new_wl_syms = st.multiselect(
        "초기 종목 선택 (화이트리스트)",
        options=available_syms,
        key="wl_new_syms",
    )
    extra_syms = st.text_input(
        "직접 입력 (쉼표 구분, 선택)",
        key="wl_new_extra",
        placeholder="예) 000660,035720",
    )
    if st.button("워치리스트 생성", key="wl_create", type="primary"):
        name = new_wl_name.strip()
        if not name:
            st.warning("워치리스트 이름을 입력하세요.")
        else:
            extra = [s.strip().upper() for s in extra_syms.split(",") if s.strip()]
            combined = list(dict.fromkeys(new_wl_syms + extra))
            watchlist_screener.create_watchlist(name, combined)
            st.success(f"'{name}' 생성 완료 ({len(combined)}종목).")
            st.rerun()


# ---------------------------------------------------------------------------
# Tab 2 — 스크리너
# ---------------------------------------------------------------------------


def _build_candidates(held_symbols: set[str]) -> list[dict]:
    """Build candidate list from whitelist + prices + fundamentals (live only)."""
    from app.services import backend

    wl = backend.list_whitelist()
    if wl.empty:
        return []

    candidates: list[dict] = []
    for _, row in wl.iterrows():
        sym = str(row["symbol"])
        try:
            p = backend.price(sym)
        except Exception:  # noqa: BLE001
            p = 0.0
        try:
            f = backend.fundamental(sym) or {}
        except Exception:  # noqa: BLE001
            f = {}
        candidates.append(
            {
                "symbol": sym,
                "name": row.get("name", ""),
                "price": p,
                "change_rate": 0.0,
                "volume": 0.0,
                "sector": f.get("sector", ""),
                "per": f.get("per"),
                "pbr": f.get("pbr"),
                "dividend_yield": None,
                "held": sym in held_symbols,
                "disclosure_keywords": [],
            }
        )
    return candidates


def _tab_screener() -> None:
    import pandas as pd

    st.subheader("스크리너 프리셋")

    screeners = watchlist_screener.list_screeners()
    if screeners:
        for sc in screeners:
            with st.expander(f"{sc['name']}  (생성: {sc['created_at'][:10]})", expanded=False):
                st.json(sc["filters"])
                c1, c2 = st.columns(2)
                if c1.button("이 프리셋 불러오기", key=f"sc_load_{sc['id']}"):
                    st.session_state["_screener_loaded"] = sc["filters"]
                    st.rerun()
                if c2.button("삭제", key=f"sc_del_{sc['id']}", type="secondary"):
                    watchlist_screener.delete_screener(sc["id"])
                    st.success("프리셋 삭제 완료.")
                    st.rerun()
    else:
        st.caption("저장된 프리셋이 없습니다.")

    st.divider()
    st.subheader("필터 설정")

    loaded = st.session_state.pop("_screener_loaded", {})

    col1, col2 = st.columns(2)
    price_min = col1.number_input(
        "최저가", min_value=0.0, value=float(loaded.get("price_min") or 0.0), step=1000.0, key="sc_price_min"
    )
    price_max = col2.number_input(
        "최고가", min_value=0.0, value=float(loaded.get("price_max") or 0.0), step=1000.0, key="sc_price_max"
    )
    col3, col4 = st.columns(2)
    chg_min = col3.number_input(
        "등락률 최저(%)", value=float(loaded.get("change_rate_min") or -100.0), step=0.5, key="sc_chg_min"
    )
    chg_max = col4.number_input(
        "등락률 최고(%)", value=float(loaded.get("change_rate_max") or 100.0), step=0.5, key="sc_chg_max"
    )
    col5, col6 = st.columns(2)
    per_max = col5.number_input(
        "PER 최대 (빈 칸=무제한)",
        min_value=0.0,
        value=float(loaded.get("per_max") or 0.0),
        step=1.0,
        key="sc_per_max",
    )
    pbr_max = col6.number_input(
        "PBR 최대 (빈 칸=무제한)",
        min_value=0.0,
        value=float(loaded.get("pbr_max") or 0.0),
        step=0.1,
        key="sc_pbr_max",
    )
    col7, col8 = st.columns(2)
    div_min = col7.number_input(
        "배당수익률 최소(%) (0=무제한)",
        min_value=0.0,
        value=float(loaded.get("dividend_yield_min") or 0.0),
        step=0.1,
        key="sc_div_min",
    )
    sector_input = col8.text_input(
        "업종 (빈 칸=전체)",
        value=str(loaded.get("sector") or ""),
        key="sc_sector",
    )
    disc_kw = st.text_input(
        "공시 키워드 (선택)",
        value=str(loaded.get("disclosure_keyword") or ""),
        key="sc_disc_kw",
    )
    holdings_radio = st.radio(
        "보유 여부",
        ["전체", "보유만", "미보유만"],
        index=0,
        horizontal=True,
        key="sc_holdings_radio",
    )

    c_run, c_save = st.columns(2)
    run_clicked = c_run.button("스크리너 실행", key="sc_run", type="primary")
    save_name = st.text_input("현재 필터를 프리셋으로 저장 (이름 입력 후 저장)", key="sc_save_name")
    save_clicked = st.button("프리셋 저장", key="sc_save_preset")

    filters: dict = {}
    if price_min > 0:
        filters["price_min"] = price_min
    if price_max > 0:
        filters["price_max"] = price_max
    filters["change_rate_min"] = chg_min
    filters["change_rate_max"] = chg_max
    if per_max > 0:
        filters["per_max"] = per_max
    if pbr_max > 0:
        filters["pbr_max"] = pbr_max
    if div_min > 0:
        filters["dividend_yield_min"] = div_min
    if sector_input.strip():
        filters["sector"] = sector_input.strip()
    if disc_kw.strip():
        filters["disclosure_keyword"] = disc_kw.strip()
    if holdings_radio == "보유만":
        filters["only_held"] = True
    elif holdings_radio == "미보유만":
        filters["only_not_held"] = True

    if save_clicked:
        if not save_name.strip():
            st.warning("프리셋 이름을 입력하세요.")
        else:
            watchlist_screener.create_screener(save_name.strip(), filters)
            st.success(f"프리셋 '{save_name.strip()}' 저장 완료.")
            st.rerun()

    if run_clicked:
        if not _live():
            st.info("라이브 모드에서만 스크리너 결과를 계산합니다.")
            st.session_state.setdefault("_screener_results", [])
        else:
            try:
                from app.services import backend

                pos_df = backend.positions()
                held_symbols: set[str] = set()
                if not pos_df.empty and "symbol" in pos_df.columns:
                    held_symbols = set(pos_df["symbol"].tolist())

                candidates = _build_candidates(held_symbols)
                results = watchlist_screener.apply_screener_filters(candidates, filters)
                st.session_state["_screener_results"] = results
            except Exception as exc:  # noqa: BLE001
                st.warning(f"스크리너 실행 실패: {exc}")
                st.session_state.setdefault("_screener_results", [])

    st.divider()
    st.subheader("스크리너 결과")
    results = st.session_state.get("_screener_results", [])
    if not results:
        st.caption("스크리너를 실행하면 결과가 여기에 표시됩니다.")
    else:
        df_results = pd.DataFrame(
            [
                {
                    "종목코드": r["symbol"],
                    "종목명": r.get("name", ""),
                    "현재가": r.get("price", 0.0),
                    "등락률(%)": r.get("change_rate", 0.0),
                    "업종": r.get("sector", ""),
                    "PER": r.get("per"),
                    "PBR": r.get("pbr"),
                    "배당수익률": r.get("dividend_yield"),
                    "보유": "Y" if r.get("held") else "N",
                }
                for r in results
            ]
        )
        st.dataframe(df_results, hide_index=True, use_container_width=True)
        st.caption(f"총 {len(results)}종목 매칭")


# ---------------------------------------------------------------------------
# Tab 3 — 알림 규칙 미리보기 (dry-run only)
# ---------------------------------------------------------------------------


def _tab_alert_preview() -> None:
    st.warning(
        "⚠️ 알림 규칙은 dry-run(미리보기) 전용입니다. 주문 제출 기능이 없습니다."
    )

    st.session_state.setdefault("_wl_preview_rules", [])
    rules: list[dict] = st.session_state["_wl_preview_rules"]

    st.subheader("알림 규칙 추가")
    opts = _whitelist_options()
    sym_labels = list(opts.keys()) if opts else []

    rule_type = st.radio(
        "규칙 유형",
        ["가격", "거래량", "공시키워드", "포트폴리오비중"],
        horizontal=True,
        key="ar_type",
    )
    if sym_labels:
        sym_label = st.selectbox("종목", sym_labels, key="ar_sym_label")
        symbol = opts[sym_label]
    else:
        symbol = st.text_input("종목코드", key="ar_sym_text", placeholder="005930").strip().upper()

    new_rule: dict = {"type": "", "symbol": symbol}

    if rule_type == "가격":
        new_rule["type"] = "price"
        c1, c2 = st.columns(2)
        new_rule["target_price"] = c1.number_input(
            "목표가", min_value=0.0, value=50000.0, step=500.0, key="ar_price_target"
        )
        new_rule["direction"] = c2.radio("방향", ["ABOVE", "BELOW"], key="ar_price_dir", horizontal=True)

    elif rule_type == "거래량":
        new_rule["type"] = "volume"
        new_rule["threshold_volume"] = st.number_input(
            "거래량 임계값", min_value=0.0, value=1_000_000.0, step=100_000.0, key="ar_vol_thr"
        )

    elif rule_type == "공시키워드":
        new_rule["type"] = "disclosure"
        new_rule["keyword"] = st.text_input("키워드", key="ar_disc_kw", placeholder="자사주")

    elif rule_type == "포트폴리오비중":
        new_rule["type"] = "weight"
        c1, c2 = st.columns(2)
        new_rule["threshold_pct"] = c1.number_input(
            "비중 임계값(%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5, key="ar_wt_thr"
        )
        new_rule["direction"] = c2.radio("방향", ["ABOVE", "BELOW"], key="ar_wt_dir", horizontal=True)

    if st.button("추가", key="ar_add", type="primary"):
        if not symbol:
            st.warning("종목코드를 입력하세요.")
        else:
            st.session_state["_wl_preview_rules"].append(new_rule)
            st.success("규칙이 추가되었습니다.")
            st.rerun()

    st.divider()
    st.subheader("등록된 규칙")
    if not rules:
        st.caption("추가된 알림 규칙이 없습니다.")
    else:
        import pandas as pd

        df_rules = pd.DataFrame(
            [
                {
                    "유형": r.get("type", ""),
                    "종목": r.get("symbol", ""),
                    "파라미터": {
                        k: v for k, v in r.items() if k not in ("type", "symbol")
                    },
                }
                for r in rules
            ]
        )
        st.dataframe(df_rules, hide_index=True, use_container_width=True)

    c_eval, c_clear = st.columns(2)

    if c_eval.button("dry-run 평가", key="ar_eval", type="primary") and rules:
        market_data: dict[str, dict] = {}

        symbols_needed = {r["symbol"] for r in rules}
        if _live():
            from app.services import backend

            pos_df = backend.positions()
            total_market = 0.0
            pos_map: dict[str, dict] = {}
            if not pos_df.empty and "symbol" in pos_df.columns:
                for _, row in pos_df.iterrows():
                    sym = str(row["symbol"])
                    cur_price = 0.0
                    try:
                        cur_price = backend.price(sym)
                    except Exception:  # noqa: BLE001
                        pass
                    qty = float(row.get("quantity", 0) or 0)
                    pos_map[sym] = {"price": cur_price, "qty": qty, "value": cur_price * qty}
                    total_market += cur_price * qty

            for sym in symbols_needed:
                cur_price = 0.0
                volume = 0.0
                disc_titles: list[str] = []
                weight_pct = 0.0

                if sym in pos_map:
                    cur_price = pos_map[sym]["price"]
                    if total_market > 0:
                        weight_pct = pos_map[sym]["value"] / total_market * 100
                else:
                    try:
                        cur_price = backend.price(sym)
                    except Exception:  # noqa: BLE001
                        pass

                try:
                    disc_df = backend.disclosures_df(sym)
                    if disc_df is not None and not disc_df.empty and "title" in disc_df.columns:
                        disc_titles = disc_df["title"].dropna().tolist()
                except Exception:  # noqa: BLE001
                    pass

                market_data[sym] = {
                    "price": cur_price,
                    "volume": volume,
                    "disclosure_titles": disc_titles,
                    "weight_pct": weight_pct,
                }
        else:
            for sym in symbols_needed:
                market_data[sym] = {
                    "price": 0.0,
                    "volume": 0.0,
                    "disclosure_titles": [],
                    "weight_pct": 0.0,
                }

        eval_results = watchlist_screener.evaluate_all_alerts(rules, market_data)
        st.session_state["_ar_eval_results"] = eval_results

    if c_clear.button("전체 규칙 초기화", key="ar_clear"):
        st.session_state["_wl_preview_rules"] = []
        st.session_state.pop("_ar_eval_results", None)
        st.rerun()

    eval_results = st.session_state.get("_ar_eval_results")
    if eval_results:
        st.divider()
        st.subheader("dry-run 평가 결과")
        for item in eval_results:
            rule = item["rule"]
            result = item["result"]
            icon = "✅" if result.get("fires") else "❌"
            st.write(
                f"{icon} **{rule.get('symbol')}** [{rule.get('type')}] — {result.get('reason', '')}"
            )
            matched = result.get("matched")
            if matched:
                st.caption(f"매칭 공시: {matched}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def render() -> None:
    st.header("📋 워치리스트 & 스크리너")

    if _live():
        st.caption("🟢 라이브 모드")
    else:
        st.caption("🧪 데모 모드 — 워치리스트 CRUD는 동작하나 스크리너는 라이브 전용입니다.")

    tab_wl, tab_sc, tab_ar = st.tabs(
        ["저장형 워치리스트", "스크리너", "알림 규칙 미리보기"]
    )

    with tab_wl:
        _tab_watchlists()

    with tab_sc:
        _tab_screener()

    with tab_ar:
        _tab_alert_preview()
