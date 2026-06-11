"""Unit tests for backend.kpis() and backend.recent_fills().

These tests use _build_holdings_df and list_order_logs directly so they do not
require a live DB or broker — pure-function coverage only.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.brokers.kis.constants import DEFAULT_KIS_INDEX_CODES

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_position(symbol: str, quantity: int, avg_price: float) -> SimpleNamespace:
    return SimpleNamespace(symbol=symbol, quantity=quantity, avg_price=avg_price)


# ---------------------------------------------------------------------------
# kpis() — unit
# ---------------------------------------------------------------------------

class TestKpis:
    """kpis() returns the correct structure and numeric values."""

    def _make_holdings_df(self, market_val: float, pnl: float) -> pd.DataFrame:
        from app.ui.backend import HOLDINGS_COLUMNS

        df = pd.DataFrame(
            [{"종목": "A", "티커": "000001", "자산군": "주식", "지역": "KR",
              "수량": 1, "평단": 1000, "현재가": 1100,
              "평가금액": market_val, "평가손익": pnl, "손익률": 10.0, "비중": 100.0}],
            columns=HOLDINGS_COLUMNS,
        )
        return df

    def test_kpis_keys_present(self):
        """All five KPI keys are present in the returned dict."""
        df = self._make_holdings_df(1_000_000.0, 100_000.0)
        with patch("app.ui.backend.holdings_df", return_value=df):
            from app.ui import backend
            result = backend.kpis()
        assert set(result.keys()) == {"총자산", "일손익률", "누적손익률", "현금비중", "평가손익"}

    def test_kpis_total_assets_equals_market_when_no_cash(self):
        """총자산 == 평가금액 합계 when cash placeholder is 0."""
        market = 5_000_000.0
        df = self._make_holdings_df(market, 500_000.0)
        with patch("app.ui.backend.holdings_df", return_value=df):
            from app.ui import backend
            result = backend.kpis()
        assert result["총자산"] == market

    def test_kpis_pnl_matches_holdings_sum(self):
        """평가손익 == holdings_df 평가손익 합계."""
        pnl = 250_000.0
        df = self._make_holdings_df(3_000_000.0, pnl)
        with patch("app.ui.backend.holdings_df", return_value=df):
            from app.ui import backend
            result = backend.kpis()
        assert result["평가손익"] == pnl

    def test_kpis_cash_ratio_zero_when_no_cash(self):
        """현금비중 == 0.0 because the cash placeholder is 0."""
        df = self._make_holdings_df(2_000_000.0, 0.0)
        with patch("app.ui.backend.holdings_df", return_value=df):
            from app.ui import backend
            result = backend.kpis()
        assert result["현금비중"] == 0.0

    def test_kpis_empty_holdings_returns_zero_totals(self):
        """When holdings are empty all numeric KPIs default to 0 / 0.0."""
        from app.ui.backend import HOLDINGS_COLUMNS

        empty_df = pd.DataFrame(columns=HOLDINGS_COLUMNS)
        with patch("app.ui.backend.holdings_df", return_value=empty_df):
            from app.ui import backend
            result = backend.kpis()
        assert result["총자산"] == 0.0
        assert result["평가손익"] == 0.0

    def test_daily_and_cumulative_pnl_rates_are_placeholder(self):
        """일손익률 and 누적손익률 are 0.0 placeholders (not yet live)."""
        df = self._make_holdings_df(1_000_000.0, 50_000.0)
        with patch("app.ui.backend.holdings_df", return_value=df):
            from app.ui import backend
            result = backend.kpis()
        assert result["일손익률"] == 0.0
        assert result["누적손익률"] == 0.0


# ---------------------------------------------------------------------------
# recent_fills() — unit
# ---------------------------------------------------------------------------

class TestRecentFills:
    """recent_fills() filters FILLED rows and maps columns correctly."""

    def _make_logs(self) -> pd.DataFrame:
        return pd.DataFrame([
            {"id": 1, "symbol": "005930", "side": "BUY", "quantity": 10,
             "order_price": 74_000.0, "order_status": "FILLED",
             "created_at": "2026-06-09 09:12:00"},
            {"id": 2, "symbol": "069500", "side": "SELL", "quantity": 5,
             "order_price": 37_800.0, "order_status": "REQUESTED",
             "created_at": "2026-06-09 10:00:00"},
            {"id": 3, "symbol": "360750", "side": "BUY", "quantity": 20,
             "order_price": 19_200.0, "order_status": "FILLED",
             "created_at": "2026-06-09 13:02:00"},
        ])

    def test_only_filled_rows_returned(self):
        """REQUESTED rows are excluded; only FILLED rows appear."""
        logs = self._make_logs()
        with patch("app.ui.backend.list_order_logs", return_value=logs):
            from app.ui import backend
            result = backend.recent_fills(limit=10)
        assert len(result) == 2
        assert set(result["종목"].tolist()) == {"005930", "360750"}

    def test_output_columns(self):
        """Returned DataFrame has exactly the five expected columns."""
        logs = self._make_logs()
        with patch("app.ui.backend.list_order_logs", return_value=logs):
            from app.ui import backend
            result = backend.recent_fills(limit=10)
        assert list(result.columns) == ["시각", "종목", "방향", "수량", "체결가"]

    def test_time_extraction_hh_mm(self):
        """시각 is extracted as HH:MM from created_at."""
        logs = self._make_logs()
        with patch("app.ui.backend.list_order_logs", return_value=logs):
            from app.ui import backend
            result = backend.recent_fills(limit=10)
        assert "09:12" in result["시각"].tolist()
        assert "13:02" in result["시각"].tolist()

    def test_limit_respected(self):
        """At most `limit` rows are returned."""
        rows = [
            {"id": i, "symbol": "005930", "side": "BUY", "quantity": 1,
             "order_price": 70_000.0, "order_status": "FILLED",
             "created_at": f"2026-06-09 0{i % 10}:00:00"}
            for i in range(5)
        ]
        logs = pd.DataFrame(rows)
        with patch("app.ui.backend.list_order_logs", return_value=logs):
            from app.ui import backend
            result = backend.recent_fills(limit=3)
        assert len(result) <= 3

    def test_empty_logs_returns_empty_df(self):
        """Empty order log returns an empty DataFrame with correct columns."""
        with patch("app.ui.backend.list_order_logs", return_value=pd.DataFrame()):
            from app.ui import backend
            result = backend.recent_fills()
        assert result.empty
        assert list(result.columns) == ["시각", "종목", "방향", "수량", "체결가"]

    def test_no_filled_rows_returns_empty_df(self):
        """When no rows are FILLED, returns empty DataFrame with correct columns."""
        logs = pd.DataFrame([
            {"id": 1, "symbol": "069500", "side": "BUY", "quantity": 5,
             "order_price": 37_800.0, "order_status": "REQUESTED",
             "created_at": "2026-06-09 10:00:00"},
        ])
        with patch("app.ui.backend.list_order_logs", return_value=logs):
            from app.ui import backend
            result = backend.recent_fills()
        assert result.empty
        assert list(result.columns) == ["시각", "종목", "방향", "수량", "체결가"]


def test_market_indices_collects_kospi_kosdaq_krx(monkeypatch):
    calls = []

    class FakeKisBroker:
        def get_index_price(self, index_code: str) -> dict:
            calls.append(index_code)
            return {
                "index_code": index_code,
                "price": 1000.0 + len(calls),
                "change": 1.0,
                "change_pct": 0.01,
                "volume": 100,
                "trading_value": 10000.0,
            }

    class FakeRepo:
        pass

    with patch("app.ui.backend._ctx", return_value=(FakeRepo(), FakeKisBroker(), None, None)):
        from app.ui import backend
        backend._ctx.cache_clear()
        result = backend.market_indices()

    assert [r["index_code"] for r in result] == list(DEFAULT_KIS_INDEX_CODES)
    assert calls == list(DEFAULT_KIS_INDEX_CODES)


def test_market_indices_returns_empty_if_not_kis_backend():
    class OtherBroker:
        pass

    with patch("app.ui.backend._ctx", return_value=(None, OtherBroker(), None, None)):
        from app.ui import backend
        backend._ctx.cache_clear()
        result = backend.market_indices()

    assert result == []
