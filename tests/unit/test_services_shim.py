"""app/services 도메인 모듈 임포트 계약 검증.

각 서비스 모듈이 app.ui.backend 의 공개 이름을 정확히 재-익스포트하는지 확인한다.
이 테스트가 통과하면 app.services.* 경로로 동일한 함수 객체를 사용할 수 있다.
"""
from __future__ import annotations

import app.ui.backend as _backend


# ---------------------------------------------------------------------------
# context
# ---------------------------------------------------------------------------

def test_services_context_exports_ctx():
    from app.services import context
    assert context._ctx is _backend._ctx
    assert context._ctx_lock is _backend._ctx_lock


# ---------------------------------------------------------------------------
# system
# ---------------------------------------------------------------------------

def test_services_system_exports():
    from app.services import system
    for name in ("env", "get_flag", "set_flag", "circuit_breaker_status", "set_risk_limits"):
        assert getattr(system, name) is getattr(_backend, name), f"system.{name} mismatch"


# ---------------------------------------------------------------------------
# portfolio
# ---------------------------------------------------------------------------

def test_services_portfolio_exports():
    from app.services import portfolio
    for name in (
        "HOLDINGS_COLUMNS",
        "_build_holdings_df",
        "holdings_df",
        "kpis",
        "positions",
        "allocation_gap",
        "asset_curve",
        "account_summary",
        "daily_pnl_series",
    ):
        assert getattr(portfolio, name) is getattr(_backend, name), f"portfolio.{name} mismatch"


# ---------------------------------------------------------------------------
# market
# ---------------------------------------------------------------------------

def test_services_market_exports():
    from app.services import market
    for name in (
        "ORDER_BOOK_COLUMNS",
        "DISCLOSURE_COLUMNS",
        "price",
        "watchlist",
        "market_indices_df",
        "sector_performance_df",
        "fundamental",
        "intraday_chart_df",
        "order_book_snapshot",
        "order_book_levels_df",
        "order_book_df",
        "disclosures_df",
    ):
        assert getattr(market, name) is getattr(_backend, name), f"market.{name} mismatch"


# ---------------------------------------------------------------------------
# trading
# ---------------------------------------------------------------------------

def test_services_trading_exports():
    from app.services import trading
    for name in (
        "add_condition",
        "list_conditions",
        "run_engine_once",
        "list_order_logs",
        "recent_fills",
        "kis_today_orders",
        "kis_order_history",
        "propose",
        "list_whitelist",
        "add_whitelist",
        "symbol_options",
    ):
        assert getattr(trading, name) is getattr(_backend, name), f"trading.{name} mismatch"


# ---------------------------------------------------------------------------
# analysis
# ---------------------------------------------------------------------------

def test_services_analysis_exports():
    from app.services import analysis
    for name in (
        "attribution_df",
        "retro_metrics",
        "scenario_analysis",
        "whatif_weight_change",
        "list_journal_entries",
        "add_journal_entry",
    ):
        assert getattr(analysis, name) is getattr(_backend, name), f"analysis.{name} mismatch"


# ---------------------------------------------------------------------------
# alerts
# ---------------------------------------------------------------------------

def test_services_alerts_exports():
    from app.services import alerts
    for name in (
        "add_price_alert",
        "disclosure_gate_state",
        "refresh_disclosure_gate",
    ):
        assert getattr(alerts, name) is getattr(_backend, name), f"alerts.{name} mismatch"
