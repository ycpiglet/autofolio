"""Unit tests for app/services/perf_report — TASK-040.

All tests use deterministic fixtures (no datetime.now(), no localtime).
Failing on import before implementation.
"""
from __future__ import annotations

import pandas as pd

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_holdings() -> pd.DataFrame:
    """Minimal holdings_df-compatible fixture (mirrors HOLDINGS_COLUMNS schema)."""
    return pd.DataFrame([
        {"종목": "삼성전자", "티커": "005930", "자산군": "주식", "지역": "KR",
         "수량": 10, "평단": 70_000, "현재가": 77_000,
         "평가금액": 770_000, "평가손익": 70_000, "손익률": 10.0,
         "예상연배당": 14_440, "배당수익률": 1.87, "비중": 60.0},
        {"종목": "KODEX 200", "티커": "069500", "자산군": "ETF", "지역": "KR",
         "수량": 40, "평단": 36_500, "현재가": 37_800,
         "평가금액": 1_512_000, "평가손익": 52_000, "손익률": 3.56,
         "예상연배당": 31_200, "배당수익률": 2.06, "비중": 40.0},
    ])


def _make_pnl_series() -> pd.DataFrame:
    """Deterministic daily PnL series (no datetime.now())."""
    return pd.DataFrame([
        {"date": "2026-06-01", "pnl": 50_000},
        {"date": "2026-06-02", "pnl": -20_000},
        {"date": "2026-06-03", "pnl": 80_000},
    ])


def _make_kpis() -> dict:
    return {
        "총자산": 2_500_000,
        "일손익률": 1.2,
        "누적손익률": 8.5,
        "현금비중": 10.0,
        "평가손익": 122_000,
    }


# ---------------------------------------------------------------------------
# Import guard — will FAIL before implementation
# ---------------------------------------------------------------------------

def test_import_perf_report_module():
    """Module must exist and export PortfolioReport + build_portfolio_report."""
    from app.services.perf_report import PortfolioReport, build_portfolio_report  # noqa: F401
    assert True


# ---------------------------------------------------------------------------
# Section 1: PortfolioReport has required fields
# ---------------------------------------------------------------------------

class TestPortfolioReportFields:
    def _build(self):
        from app.services.perf_report import build_portfolio_report
        return build_portfolio_report(
            holdings=_make_holdings(),
            pnl_series=_make_pnl_series(),
            kpis=_make_kpis(),
            realized_pnl=5_000.0,
        )

    def test_has_realized_pnl_field(self):
        r = self._build()
        assert hasattr(r, "realized_pnl")

    def test_has_unrealized_pnl_field(self):
        r = self._build()
        assert hasattr(r, "unrealized_pnl")

    def test_has_cashflow_note_field(self):
        """cashflow_note must be a non-empty string explaining the data limitation."""
        r = self._build()
        assert hasattr(r, "cashflow_note")
        assert isinstance(r.cashflow_note, str) and len(r.cashflow_note) > 0

    def test_has_fee_slippage_note_field(self):
        """fee_slippage_note must mention 'not modeled' or '미반영'."""
        r = self._build()
        assert hasattr(r, "fee_slippage_note")
        note = r.fee_slippage_note.lower()
        assert "not modeled" in note or "미반영" in note

    def test_has_turnover_note_field(self):
        r = self._build()
        assert hasattr(r, "turnover_note")
        assert isinstance(r.turnover_note, str)

    def test_has_attribution_df_field(self):
        """attribution_df must be a DataFrame with '구분' and '기여(만원)' columns."""
        r = self._build()
        assert hasattr(r, "attribution_df")
        assert isinstance(r.attribution_df, pd.DataFrame)
        assert "구분" in r.attribution_df.columns
        assert "기여(만원)" in r.attribution_df.columns

    def test_has_attribution_note_field(self):
        """attribution_note explains data availability honestly."""
        r = self._build()
        assert hasattr(r, "attribution_note")
        assert isinstance(r.attribution_note, str) and len(r.attribution_note) > 0

    def test_has_tax_lot_df_field(self):
        """tax_lot_df must be a DataFrame with expected columns."""
        r = self._build()
        assert hasattr(r, "tax_lot_df")
        assert isinstance(r.tax_lot_df, pd.DataFrame)
        assert "티커" in r.tax_lot_df.columns
        assert "평단" in r.tax_lot_df.columns
        assert "수량" in r.tax_lot_df.columns

    def test_has_tax_lot_disclaimer_field(self):
        """tax_lot_disclaimer must warn the user this is illustrative only."""
        r = self._build()
        assert hasattr(r, "tax_lot_disclaimer")
        disclaimer = r.tax_lot_disclaimer.lower()
        # must include a disclaimer keyword (illustrative / placeholder / 참고용 / 면책)
        keywords = ["illustrative", "placeholder", "참고용", "면책", "세무 조언", "tax advice"]
        assert any(k in disclaimer for k in keywords), (
            f"tax_lot_disclaimer missing disclaimer keyword. Got: {r.tax_lot_disclaimer!r}"
        )

    def test_has_report_date_field(self):
        """report_date must be a non-empty string (ISO date)."""
        r = self._build()
        assert hasattr(r, "report_date")
        assert isinstance(r.report_date, str) and len(r.report_date) == 10  # YYYY-MM-DD


# ---------------------------------------------------------------------------
# Section 2: Numeric correctness
# ---------------------------------------------------------------------------

class TestPortfolioReportNumerics:
    def test_unrealized_pnl_matches_holdings_sum(self):
        from app.services.perf_report import build_portfolio_report
        holdings = _make_holdings()
        r = build_portfolio_report(
            holdings=holdings,
            pnl_series=_make_pnl_series(),
            kpis=_make_kpis(),
            realized_pnl=5_000.0,
        )
        expected_unrealized = int(holdings["평가손익"].sum())  # 70_000 + 52_000 = 122_000
        assert r.unrealized_pnl == expected_unrealized

    def test_realized_pnl_passes_through(self):
        from app.services.perf_report import build_portfolio_report
        r = build_portfolio_report(
            holdings=_make_holdings(),
            pnl_series=_make_pnl_series(),
            kpis=_make_kpis(),
            realized_pnl=9_999.0,
        )
        assert r.realized_pnl == 9_999.0

    def test_attribution_groups_by_asset_class(self):
        """attribution_df must have one row per 자산군 present in holdings."""
        from app.services.perf_report import build_portfolio_report
        r = build_portfolio_report(
            holdings=_make_holdings(),
            pnl_series=_make_pnl_series(),
            kpis=_make_kpis(),
            realized_pnl=0.0,
        )
        groups = set(r.attribution_df["구분"].tolist())
        assert "주식" in groups
        assert "ETF" in groups

    def test_tax_lot_rows_match_holdings(self):
        """tax_lot_df has one row per holding."""
        from app.services.perf_report import build_portfolio_report
        holdings = _make_holdings()
        r = build_portfolio_report(
            holdings=holdings,
            pnl_series=_make_pnl_series(),
            kpis=_make_kpis(),
            realized_pnl=0.0,
        )
        assert len(r.tax_lot_df) == len(holdings)

    def test_empty_holdings_returns_empty_df_fields(self):
        """build_portfolio_report handles empty holdings without crash."""
        from app.services.perf_report import build_portfolio_report
        from app.services.backend import HOLDINGS_COLUMNS
        empty = pd.DataFrame(columns=HOLDINGS_COLUMNS)
        r = build_portfolio_report(
            holdings=empty,
            pnl_series=pd.DataFrame(columns=["date", "pnl"]),
            kpis={"총자산": 0, "일손익률": 0, "누적손익률": 0, "현금비중": 0, "평가손익": 0},
            realized_pnl=0.0,
        )
        assert r.unrealized_pnl == 0
        assert r.realized_pnl == 0.0
        assert r.tax_lot_df.empty

    def test_build_is_deterministic(self):
        """Same inputs → same output (no datetime.now() or random)."""
        from app.services.perf_report import build_portfolio_report
        r1 = build_portfolio_report(
            holdings=_make_holdings(),
            pnl_series=_make_pnl_series(),
            kpis=_make_kpis(),
            realized_pnl=5_000.0,
        )
        r2 = build_portfolio_report(
            holdings=_make_holdings(),
            pnl_series=_make_pnl_series(),
            kpis=_make_kpis(),
            realized_pnl=5_000.0,
        )
        assert r1.realized_pnl == r2.realized_pnl
        assert r1.unrealized_pnl == r2.unrealized_pnl
        assert r1.report_date == r2.report_date
        assert r1.fee_slippage_note == r2.fee_slippage_note
        assert r1.tax_lot_disclaimer == r2.tax_lot_disclaimer
