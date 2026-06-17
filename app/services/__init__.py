"""app/services — 도메인 서비스 레이어 (Phase 5 runtime).

FastAPI/Next.js runtime이 공유하는 공개 API.
`app.services.backend` 구현을 도메인별로 재-익스포트한다.
Streamlit views는 TASK-049에서 은퇴되어 archive로 이동했다.

도메인 모듈:
  context        — _ctx() 싱글턴 + _ctx_lock
  system         — env, get_flag, set_flag, circuit_breaker_status, set_risk_limits
  portfolio      — holdings_df, kpis, positions, allocation_gap, asset_curve, account_summary, daily_pnl_series
  market         — price, watchlist, market_indices_df, sector_performance_df, fundamental,
                   intraday_chart_df, order_book_snapshot/levels_df/df, disclosures_df
  trading        — add_condition, list_conditions, run_engine_once, list_order_logs,
                   recent_fills, kis_today_orders, kis_order_history, propose,
                   list_whitelist, add_whitelist, symbol_options,
                   GateResult, save_condition_with_gates (서비스 네이티브)
  analysis       — attribution_df, retro_metrics, scenario_analysis, whatif_weight_change,
                   list_journal_entries, add_journal_entry
  alerts         — add_price_alert, disclosure_gate_state, refresh_disclosure_gate
  connections    — get, brokers_public, add_broker, remove_broker, set_default_broker,
                   connect_channel, disconnect_channel (REAL move from app.ui.store)
  auth_service   — login_or_register (SPLIT: pure auth; oidc_* stays in app.ui.auth)
  agents         — ask, available, list_agents, run_ic, list_decisions,
                   extract_condition_from_ic, DEFAULT_PANEL, MODEL, EFFORT
                   (REAL move from app.ui.agents_runtime + app.ui.ic)

레거시 shim 잔존:
  store.py        → REAL move  (streamlit 미사용, 테스트 경로 패치 없음)
  auth.py         → SPLIT      (oidc_* 함수가 st.login/st.user 사용 → app.ui.auth 잔류)
  ic.py           → REAL move  (streamlit 미사용, 테스트 경로 패치 없음)
  agents_runtime  → REAL move  (streamlit 미사용; test_trading_gates 가 app.ui.agents_runtime.ask 를
                   patch 하나, save_condition_with_gates 가 ar.ask 속성 조회로 호출하므로 shim 경로 patch 유효)
"""
