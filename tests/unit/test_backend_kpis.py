"""Unit tests for backend.kpis() and backend.recent_fills().

These tests use _build_holdings_df and list_order_logs directly so they do not
require a live DB or broker — pure-function coverage only.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


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
        from app.services.backend import HOLDINGS_COLUMNS

        df = pd.DataFrame(
            [{"종목": "A", "티커": "000001", "자산군": "주식", "지역": "KR",
              "수량": 1, "평단": 1000, "현재가": 1100,
              "평가금액": market_val, "평가손익": pnl, "손익률": 10.0, "비중": 100.0}],
            columns=HOLDINGS_COLUMNS,
        )
        return df

    def _no_cash_ctx(self):
        return (None, SimpleNamespace(), None, None)

    def test_kpis_keys_present(self):
        """All five KPI keys are present in the returned dict."""
        df = self._make_holdings_df(1_000_000.0, 100_000.0)
        with (
            patch("app.services.backend.holdings_df", return_value=df),
            patch("app.services.backend._ctx", return_value=self._no_cash_ctx()),
        ):
            from app.services import backend
            result = backend.kpis()
        assert set(result.keys()) == {"총자산", "일손익률", "누적손익률", "현금비중", "평가손익"}

    def test_kpis_total_assets_equals_market_when_no_cash(self):
        """총자산 == 평가금액 합계 when cash placeholder is 0."""
        market = 5_000_000.0
        df = self._make_holdings_df(market, 500_000.0)
        with (
            patch("app.services.backend.holdings_df", return_value=df),
            patch("app.services.backend._ctx", return_value=self._no_cash_ctx()),
        ):
            from app.services import backend
            result = backend.kpis()
        assert result["총자산"] == market

    def test_kpis_pnl_matches_holdings_sum(self):
        """평가손익 == holdings_df 평가손익 합계."""
        pnl = 250_000.0
        df = self._make_holdings_df(3_000_000.0, pnl)
        with (
            patch("app.services.backend.holdings_df", return_value=df),
            patch("app.services.backend._ctx", return_value=self._no_cash_ctx()),
        ):
            from app.services import backend
            result = backend.kpis()
        assert result["평가손익"] == pnl

    def test_kpis_cash_ratio_zero_when_no_cash(self):
        """현금비중 == 0.0 because the cash placeholder is 0."""
        df = self._make_holdings_df(2_000_000.0, 0.0)
        with (
            patch("app.services.backend.holdings_df", return_value=df),
            patch("app.services.backend._ctx", return_value=self._no_cash_ctx()),
        ):
            from app.services import backend
            result = backend.kpis()
        assert result["현금비중"] == 0.0

    def test_kpis_includes_cash_when_broker_supports_cash_balance(self):
        """KIS cash balance is included in total assets and cash ratio."""
        df = self._make_holdings_df(5_000_000.0, 500_000.0)
        fake_broker = SimpleNamespace(get_cash_balance=lambda: 2_000_000.0)
        with (
            patch("app.services.backend.holdings_df", return_value=df),
            patch("app.services.backend._ctx", return_value=(None, fake_broker, None, None)),
        ):
            from app.services import backend
            result = backend.kpis()
        assert result["총자산"] == 7_000_000.0
        assert round(result["현금비중"], 2) == 28.57

    def test_kpis_empty_holdings_returns_zero_totals(self):
        """When holdings are empty all numeric KPIs default to 0 / 0.0."""
        from app.services.backend import HOLDINGS_COLUMNS

        empty_df = pd.DataFrame(columns=HOLDINGS_COLUMNS)
        with (
            patch("app.services.backend.holdings_df", return_value=empty_df),
            patch("app.services.backend._ctx", return_value=self._no_cash_ctx()),
        ):
            from app.services import backend
            result = backend.kpis()
        assert result["총자산"] == 0.0
        assert result["평가손익"] == 0.0

    def test_daily_and_cumulative_pnl_rates_zero_when_no_fills(self):
        """일손익률 and 누적손익률 are 0.0 when no execution fills exist.

        With an empty repo (no execution_logs), both return 0.0.
        This is correct behavior (empty portfolio), not a placeholder.
        """
        import pathlib
        import tempfile
        from types import SimpleNamespace

        from app.database.repositories import Repository
        from app.database.sqlite_db import initialize_database

        with tempfile.TemporaryDirectory() as td:
            db_path = pathlib.Path(td) / "empty.db"
            initialize_database(db_path)
            empty_repo = Repository(db_path)

            df = self._make_holdings_df(1_000_000.0, 50_000.0)
            fake_broker = SimpleNamespace(get_cash_balance=lambda: 0.0)
            with (
                patch("app.services.backend.holdings_df", return_value=df),
                patch("app.services.backend._ctx", return_value=(empty_repo, fake_broker, None, None)),
            ):
                from app.services import backend
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
        """REQUESTED rows are excluded; only FILLED rows appear (종목 shows name, not code)."""
        logs = self._make_logs()
        with patch("app.services.backend.list_order_logs", return_value=logs):
            from app.services import backend
            result = backend.recent_fills(limit=10)
        assert len(result) == 2
        # resolve_symbol_name maps codes to names from _DEFAULT_SYMBOL_META
        종목_values = set(result["종목"].tolist())
        assert "005930" not in 종목_values, "Raw code should not appear — resolver must have run"
        assert "360750" not in 종목_values, "Raw code should not appear — resolver must have run"
        assert "삼성전자" in 종목_values
        # 360750 → TIGER 미국S&P500 (from _DEFAULT_SYMBOL_META)
        assert any("TIGER" in v for v in 종목_values)

    def test_output_columns(self):
        """Returned DataFrame has exactly the five expected columns."""
        logs = self._make_logs()
        with patch("app.services.backend.list_order_logs", return_value=logs):
            from app.services import backend
            result = backend.recent_fills(limit=10)
        assert list(result.columns) == ["시각", "종목", "방향", "수량", "체결가"]

    def test_time_extraction_hh_mm(self):
        """시각 is extracted as HH:MM from created_at."""
        logs = self._make_logs()
        with patch("app.services.backend.list_order_logs", return_value=logs):
            from app.services import backend
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
        with patch("app.services.backend.list_order_logs", return_value=logs):
            from app.services import backend
            result = backend.recent_fills(limit=3)
        assert len(result) <= 3

    def test_empty_logs_returns_empty_df(self):
        """Empty order log returns an empty DataFrame with correct columns."""
        with patch("app.services.backend.list_order_logs", return_value=pd.DataFrame()):
            from app.services import backend
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
        with patch("app.services.backend.list_order_logs", return_value=logs):
            from app.services import backend
            result = backend.recent_fills()
        assert result.empty
        assert list(result.columns) == ["시각", "종목", "방향", "수량", "체결가"]


# ---------------------------------------------------------------------------
# kpis() daily_return / total_return — integration-style (in-process SQLite)
# ---------------------------------------------------------------------------

class TestKpisReturnRates:
    """kpis() daily_return and total_return must be non-zero when there is
    realized PnL and holdings. Uses a real temp SQLite DB — no network."""

    @pytest.fixture()
    def backend_with_fills(self, tmp_path, monkeypatch):
        """Seed: BUY 1 share @ 70_000, SELL 1 @ 75_000 (profit 5_000).
        Holdings: still hold 1 share with avg_price=70_000, current_price=77_000.
        unrealized PnL = (77_000 - 70_000) * 1 = 7_000.
        total_buy_cost = 2 * 70_000 = 140_000  (two BUY fills total).
        total_realized = 5_000.
        unrealized = 7_000.
        total_return = (5_000 + 7_000) / 140_000 * 100 ≈ 8.57%.
        daily holdings buy cost = 1 × 70_000 = 70_000.
        daily_return = 5_000 / 70_000 * 100 ≈ 7.14%.
        """
        from types import SimpleNamespace

        from app.brokers.base import Position
        from app.database.repositories import Repository, WhitelistSymbol
        from app.database.sqlite_db import initialize_database, get_connection
        from app.services import backend

        db_path = tmp_path / "kpi_test.db"
        initialize_database(db_path)
        repo = Repository(db_path)
        repo.add_whitelist_symbol(
            WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
        )

        # BUY 1 @ 70_000 (first buy — will be sold)
        buy1 = repo.create_order_log(
            condition_id=None, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=70000.0, current_price=70000.0,
            quantity=1, kis_order_id="B1", order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=buy1, symbol="005930",
            filled_price=70000.0, filled_quantity=1,
        )

        # BUY 1 @ 70_000 (second buy — still held)
        buy2 = repo.create_order_log(
            condition_id=None, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=70000.0, current_price=70000.0,
            quantity=1, kis_order_id="B2", order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=buy2, symbol="005930",
            filled_price=70000.0, filled_quantity=1,
        )

        # SELL 1 @ 75_000 today (realized = 5_000)
        # Use explicit KST-today timestamp so the test is TZ-independent
        sell1 = repo.create_order_log(
            condition_id=None, symbol="005930", side="SELL",
            order_type="LIMIT", order_price=75000.0, current_price=75000.0,
            quantity=1, kis_order_id="S1", order_status="FILLED",
        )
        # Inject today-KST into filled_at ('+9 hours' = KST; avoids localtime)
        with get_connection(db_path) as conn:
            conn.execute(
                """
                INSERT INTO execution_logs(order_log_id, symbol, filled_price, filled_quantity, filled_at)
                VALUES (?, ?, ?, ?, datetime('now', '+9 hours', 'start of day', '-9 hours', '+1 minute'))
                """,
                (sell1, "005930", 75000.0, 1),
            )

        # Mock holdings: 1 share of 005930 @ avg_price=70_000, current=77_000
        fake_positions = [Position("005930", 1, 70000.0)]
        fake_broker = SimpleNamespace(
            get_positions=lambda: fake_positions,
            get_prices_batch=lambda syms: {"005930": 77000.0},
            get_current_price=lambda s: SimpleNamespace(price=77000.0),
            get_cash_balance=lambda: 0.0,
        )

        monkeypatch.setattr(backend, "_ctx", lambda: (repo, fake_broker, None, None))
        return repo

    def test_daily_return_is_nonzero(self, backend_with_fills, monkeypatch):
        """daily_return must be > 0 when there is today's realized profit.

        Current code returns 0.0 (FAIL before fix).
        """
        from app.services import backend
        result = backend.kpis()
        assert result["일손익률"] > 0.0, (
            f"Expected daily_return > 0 (got {result['일손익률']}). "
            "Hardcoded 0.0 not yet replaced."
        )

    def test_total_return_is_nonzero(self, backend_with_fills, monkeypatch):
        """total_return must be > 0 when there is realized + unrealized profit.

        Current code returns 0.0 (FAIL before fix).
        """
        from app.services import backend
        result = backend.kpis()
        assert result["누적손익률"] > 0.0, (
            f"Expected total_return > 0 (got {result['누적손익률']}). "
            "Hardcoded 0.0 not yet replaced."
        )

    def test_return_values_match_formula(self, backend_with_fills, monkeypatch):
        """Verify exact formula output.

        total_buy_cost = 140_000 (2 BUY fills × 70_000).
        total_realized = 5_000. unrealized = 7_000.
        total_return = (5_000 + 7_000) / 140_000 * 100 ≈ 8.57%.
        daily holdings buy cost = 1 × 70_000 = 70_000.
        daily_return = 5_000 / 70_000 * 100 ≈ 7.14%.
        """
        from app.services import backend
        result = backend.kpis()
        assert result["누적손익률"] == pytest.approx(12000 / 140000 * 100, rel=0.01)
        assert result["일손익률"] == pytest.approx(5000 / 70000 * 100, rel=0.01)
