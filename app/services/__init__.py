"""app/services — 도메인 서비스 레이어 (Phase 0 Strangler Migration).

Streamlit UI(app/ui/backend.py)와 미래의 FastAPI 레이어가 공유하는 공개 API.
현재 단계(Phase 0)에서는 app/ui/backend 의 구현을 도메인별로 재-익스포트한다.
뷰 코드를 app/services 로 마이그레이션하면 backend.py 가 shim으로 전환된다.

도메인 모듈:
  context   — _ctx() 싱글턴 + _ctx_lock
  system    — env, get_flag, set_flag, circuit_breaker_status, set_risk_limits
  portfolio — holdings_df, kpis, positions, allocation_gap, asset_curve, account_summary,
              daily_pnl_series
  market    — price, watchlist, market_indices_df, sector_performance_df, fundamental,
              intraday_chart_df, order_book_snapshot/levels_df/df, disclosures_df
  trading   — add_condition, list_conditions, run_engine_once, list_order_logs,
              recent_fills, kis_today_orders, kis_order_history, propose,
              list_whitelist, add_whitelist, symbol_options
  analysis  — attribution_df, retro_metrics, scenario_analysis, whatif_weight_change,
              list_journal_entries, add_journal_entry
  alerts    — add_price_alert, disclosure_gate_state, refresh_disclosure_gate
"""
