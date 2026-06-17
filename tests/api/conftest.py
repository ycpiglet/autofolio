"""Shared fixtures for Autofolio API tests.

Isolation strategy (mirrors existing unit tests):
- All backend functions are monkeypatched via pytest's monkeypatch fixture
  so no network, no real DB, and no KIS keys are needed.
- TestClient from starlette drives the app synchronously.
- The session cookie is injected directly via TestClient.cookies so tests
  can target authed/unauthed states without going through /auth/login.
"""
from __future__ import annotations

import types
from typing import Any

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.api.main import create_app
from app.api.security import encode_session

# ── Sample data ───────────────────────────────────────────────────────────────

SAMPLE_HOLDINGS = pd.DataFrame(
    [
        {
            "종목": "삼성전자",
            "티커": "005930",
            "자산군": "주식",
            "지역": "KR",
            "수량": 10,
            "평단": 70_000,
            "현재가": 75_000,
            "평가금액": 750_000,
            "평가손익": 50_000,
            "손익률": 7.1,
            "예상연배당": 4_000,
            "배당수익률": 0.53,
            "비중": 100.0,
        }
    ]
)

SAMPLE_KPIS: dict[str, Any] = {
    "총자산": 750_000.0,
    "일손익률": 0.5,
    "누적손익률": 7.1,
    "현금비중": 0.0,
    "평가손익": 50_000.0,
}

SAMPLE_ASSET_CURVE = pd.DataFrame(
    {"자산": [700_000.0, 720_000.0, 750_000.0]},
    index=pd.DatetimeIndex(
        ["2026-06-12", "2026-06-13", "2026-06-14"], name="date"
    ),
)

SAMPLE_ALLOCATION_GAP = pd.DataFrame(
    [{"자산군": "주식", "목표%": 35, "현재%": 100.0, "갭%": 65.0}]
)

SAMPLE_INDICES = pd.DataFrame(
    [{"name": "KOSPI", "code": "0001", "price": 2600.0, "change": 10.0, "change_rate": 0.38}]
)

SAMPLE_WATCHLIST = pd.DataFrame(
    [{"symbol": "005930", "name": "삼성전자", "price": 75_000.0}]
)

SAMPLE_FILLS = pd.DataFrame(
    [{"시각": "09:12", "종목": "005930", "방향": "BUY", "수량": 10, "체결가": 70_000.0}]
)

SAMPLE_CB = {
    "triggered": False,
    "threshold_pct": 3.0,
    "consecutive_failures": 0,
    "today_pnl": 0.0,
}

# ── Phase 2 sample data ───────────────────────────────────────────────────────

SAMPLE_CONDITIONS = pd.DataFrame(
    [
        {
            "id": 1,
            "symbol": "005930",
            "side": "BUY",
            "target_price": 70000.0,
            "quantity": 10,
            "order_type": "LIMIT",
            "auto_enabled": False,
            "created_by": "USER",
        }
    ]
)

SAMPLE_ORDER_LOGS = pd.DataFrame(
    [
        {
            "id": 1,
            "symbol": "005930",
            "side": "BUY",
            "quantity": 10,
            "order_price": 70000.0,
            "order_status": "FILLED",
            "created_at": "2026-06-12 09:30:00",
        }
    ]
)

SAMPLE_ORDER_BOOK = pd.DataFrame(
    [
        {
            "level": 1,
            "ask_price": 75100,
            "ask_quantity": 100,
            "bid_price": 74900,
            "bid_quantity": 200,
        }
    ]
)

SAMPLE_INTRADAY = pd.DataFrame(
    [
        {
            "time": "0930",
            "open": 74000,
            "high": 75100,
            "low": 73900,
            "close": 75000,
            "volume": 50000,
        }
    ]
)

SAMPLE_SECTORS = pd.DataFrame(
    [
        {
            "name": "반도체",
            "code": "WMD0700",
            "price": 3200.0,
            "change": 12.0,
            "change_rate": 0.38,
            "trading_value": 1_000_000_000,
        }
    ]
)

SAMPLE_DISCLOSURES = pd.DataFrame(
    [
        {
            "date": "20260612",
            "time": "0900",
            "symbol": "005930",
            "title": "사업보고서",
            "category": "정기공시",
            "severity": "LOW",
            "block_order": False,
            "source": "dart",
            "serial": "abc123",
        }
    ]
)

SAMPLE_ATTRIBUTION = pd.DataFrame(
    [{"구분": "주식", "기여(만원)": 5.0}]
)

SAMPLE_RETRO: dict[str, Any] = {
    "승률": 75,
    "평균R": 1.5,
    "MDD": 0.0,
    "규율": 95,
}

SAMPLE_DAILY_PNL = pd.DataFrame(
    [{"date": "2026-06-12", "pnl": 50_000.0}]
)

SAMPLE_WHITELIST = pd.DataFrame(
    [
        {"symbol": "005930", "name": "삼성전자", "market": "KRX", "role": "LARGE_CAP_TEST", "enabled": True},
        {"symbol": "069500", "name": "KODEX 200", "market": "KRX", "role": "ETF_TEST", "enabled": True},
    ]
)


# ── Cookie helpers ─────────────────────────────────────────────────────────────

def guest_cookies() -> dict[str, str]:
    return {"af_session": encode_session({"role": "guest", "data_source": "demo"})}


def owner_cookies(username: str = "testuser") -> dict[str, str]:
    return {
        "af_session": encode_session(
            {"role": "owner", "username": username, "data_source": "backend"}
        )
    }


# ── App fixture ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest.fixture()
def client(app):
    """Plain TestClient — no session cookie set."""
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture()
def guest_client(app):
    """TestClient with a valid guest session cookie."""
    c = TestClient(app, raise_server_exceptions=True)
    c.cookies.set("af_session", encode_session({"role": "guest", "data_source": "demo"}))
    return c


@pytest.fixture()
def owner_client(app):
    """TestClient with a valid owner session cookie."""
    c = TestClient(app, raise_server_exceptions=True)
    c.cookies.set(
        "af_session",
        encode_session({"role": "owner", "username": "testuser", "data_source": "backend"}),
    )
    return c


@pytest.fixture()
def error_client(app):
    """TestClient with guest session that does NOT re-raise server exceptions.

    Use this fixture specifically for fail-loud tests that expect the server
    to return a non-200 HTTP error rather than propagating the exception.
    """
    c = TestClient(app, raise_server_exceptions=False)
    c.cookies.set("af_session", encode_session({"role": "guest", "data_source": "demo"}))
    return c


# ── Backend mock fixture ───────────────────────────────────────────────────────

@pytest.fixture()
def mock_backend(monkeypatch):
    """Monkeypatch app.services.backend with deterministic sample data.

    Returns the fake module so individual tests can override specific attrs.
    """
    import app.services.backend as backend_mod

    monkeypatch.setattr(backend_mod, "holdings_df", lambda **kw: SAMPLE_HOLDINGS)
    monkeypatch.setattr(backend_mod, "kpis", lambda: SAMPLE_KPIS)
    monkeypatch.setattr(backend_mod, "asset_curve", lambda days=90: SAMPLE_ASSET_CURVE)
    monkeypatch.setattr(backend_mod, "allocation_gap", lambda target=None: SAMPLE_ALLOCATION_GAP)
    monkeypatch.setattr(backend_mod, "market_indices_df", lambda: SAMPLE_INDICES)
    monkeypatch.setattr(backend_mod, "watchlist", lambda: SAMPLE_WATCHLIST)
    monkeypatch.setattr(backend_mod, "recent_fills", lambda limit=10: SAMPLE_FILLS)
    monkeypatch.setattr(backend_mod, "circuit_breaker_status", lambda: SAMPLE_CB)
    monkeypatch.setattr(backend_mod, "env", lambda: "mock")
    monkeypatch.setattr(backend_mod, "get_flag", lambda key: False)

    # Phase 2 additions
    monkeypatch.setattr(backend_mod, "price", lambda symbol: 75_000.0)
    monkeypatch.setattr(backend_mod, "fundamental", lambda symbol: {"per": 12.5, "pbr": 1.3})
    monkeypatch.setattr(backend_mod, "order_book_df", lambda symbol, market="J": SAMPLE_ORDER_BOOK)
    monkeypatch.setattr(
        backend_mod,
        "intraday_chart_df",
        lambda symbol, time_unit="1", count=120: SAMPLE_INTRADAY,
    )
    monkeypatch.setattr(backend_mod, "sector_performance_df", lambda: SAMPLE_SECTORS)
    monkeypatch.setattr(backend_mod, "disclosures_df", lambda symbol, days=1: SAMPLE_DISCLOSURES)
    monkeypatch.setattr(backend_mod, "list_conditions", lambda: SAMPLE_CONDITIONS)
    monkeypatch.setattr(backend_mod, "list_order_logs", lambda limit=200: SAMPLE_ORDER_LOGS)
    monkeypatch.setattr(backend_mod, "attribution_df", lambda: SAMPLE_ATTRIBUTION)
    monkeypatch.setattr(backend_mod, "retro_metrics", lambda: SAMPLE_RETRO)
    monkeypatch.setattr(backend_mod, "daily_pnl_series", lambda: SAMPLE_DAILY_PNL)
    monkeypatch.setattr(backend_mod, "list_whitelist", lambda: SAMPLE_WHITELIST)

    return backend_mod
