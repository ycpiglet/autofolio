"""Unit tests for backend.asset_curve() and backend._generate_demo_asset_curve().

데모 시드 곡선: mock/demo 환경에서 체결 내역 없고 잔고 0일 때 현실적인 90일 곡선을 반환한다.
실거래 경로는 건드리지 않는다.
"""
from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# _generate_demo_asset_curve — 순수 함수 테스트
# ---------------------------------------------------------------------------


class TestGenerateDemoAssetCurve:
    """_generate_demo_asset_curve()는 결정적·현실적 데모 곡선을 생성한다."""

    def _call(self, days: int = 90, end_value: float = 0.0) -> pd.DataFrame:
        from app.services.backend import _generate_demo_asset_curve
        return _generate_demo_asset_curve(days, end_value)

    def test_returns_dataframe(self):
        df = self._call()
        assert isinstance(df, pd.DataFrame)

    def test_correct_length(self):
        """요청한 days 수만큼 행이 반환된다."""
        for days in (30, 60, 90):
            df = self._call(days=days)
            assert len(df) == days, f"Expected {days} rows, got {len(df)}"

    def test_has_asset_column(self):
        df = self._call()
        assert "자산" in df.columns

    def test_index_name_is_date(self):
        """직렬화(df_records)가 index를 'date' 컬럼으로 승격시키려면 name='date'여야 한다."""
        df = self._call()
        assert df.index.name == "date"

    def test_deterministic(self):
        """같은 인수로 두 번 호출하면 동일한 결과를 반환한다 (고정 시드)."""
        df1 = self._call(days=90, end_value=0.0)
        df2 = self._call(days=90, end_value=0.0)
        pd.testing.assert_frame_equal(df1, df2)

    def test_starts_near_initial_capital(self):
        """첫 값이 _DEMO_INITIAL_CAPITAL ± 30% 이내여야 한다."""
        from app.services.backend import _DEMO_INITIAL_CAPITAL
        df = self._call(days=90, end_value=0.0)
        first = float(df["자산"].iloc[0])
        assert abs(first - _DEMO_INITIAL_CAPITAL) / _DEMO_INITIAL_CAPITAL < 0.3

    def test_ends_at_initial_capital_when_end_value_zero(self):
        """end_value=0이면 끝값이 _DEMO_INITIAL_CAPITAL에 맞춰진다."""
        from app.services.backend import _DEMO_INITIAL_CAPITAL
        df = self._call(days=90, end_value=0.0)
        last = float(df["자산"].iloc[-1])
        assert abs(last - _DEMO_INITIAL_CAPITAL) < 1.0  # round() 오차 허용

    def test_ends_near_given_end_value(self):
        """end_value > 0이면 끝값이 해당 값에 맞춰진다."""
        target = 2_000_000.0
        df = self._call(days=90, end_value=target)
        last = float(df["자산"].iloc[-1])
        assert abs(last - target) < 1.0

    def test_all_values_positive(self):
        """모든 자산값이 양수여야 한다."""
        df = self._call(days=90, end_value=0.0)
        assert (df["자산"] > 0).all()

    def test_no_degenerate_flat_zeros(self):
        """값이 0으로 수렴하지 않는다 (퇴화 곡선 재발 방지)."""
        df = self._call(days=90, end_value=0.0)
        assert df["자산"].nunique() > 10, "곡선이 거의 평탄하거나 퇴화됨"


# ---------------------------------------------------------------------------
# asset_curve() — 분기 테스트
# ---------------------------------------------------------------------------


class TestAssetCurve:
    """asset_curve()는 상황에 따라 올바른 경로를 선택한다."""

    def _empty_holdings(self) -> pd.DataFrame:
        from app.services.backend import HOLDINGS_COLUMNS
        return pd.DataFrame(columns=HOLDINGS_COLUMNS)

    def _empty_pnl(self) -> pd.DataFrame:
        return pd.DataFrame(columns=["date", "pnl"])

    def test_demo_mode_returns_90_rows_by_default(self):
        """체결 내역 없음 + 잔고 0 → 데모 곡선 90행."""
        with (
            patch("app.services.backend.daily_pnl_series", return_value=self._empty_pnl()),
            patch("app.services.backend.holdings_df", return_value=self._empty_holdings()),
        ):
            from app.services import backend
            df = backend.asset_curve(days=90)
        assert len(df) == 90

    def test_demo_mode_respects_days_param(self):
        """days 파라미터가 데모 곡선 길이에 반영된다."""
        with (
            patch("app.services.backend.daily_pnl_series", return_value=self._empty_pnl()),
            patch("app.services.backend.holdings_df", return_value=self._empty_holdings()),
        ):
            from app.services import backend
            df = backend.asset_curve(days=30)
        assert len(df) == 30

    def test_demo_mode_has_asset_column_and_named_index(self):
        with (
            patch("app.services.backend.daily_pnl_series", return_value=self._empty_pnl()),
            patch("app.services.backend.holdings_df", return_value=self._empty_holdings()),
        ):
            from app.services import backend
            df = backend.asset_curve()
        assert "자산" in df.columns
        assert df.index.name == "date"

    def test_demo_curve_values_are_nonzero(self):
        """데모 곡선 자산값이 0이 아니어야 한다 (퇴화 재발 방지)."""
        with (
            patch("app.services.backend.daily_pnl_series", return_value=self._empty_pnl()),
            patch("app.services.backend.holdings_df", return_value=self._empty_holdings()),
        ):
            from app.services import backend
            df = backend.asset_curve()
        assert (df["자산"] > 0).all(), "데모 곡선에 0 이하 값이 있음"

    def test_real_holdings_no_trades_returns_single_point(self):
        """체결 내역 없음 + 보유 잔고 있음 → 단일 관측값 (실계정 경로 유지)."""
        from app.services.backend import HOLDINGS_COLUMNS

        holdings = pd.DataFrame(
            [{"종목": "삼성전자", "티커": "005930", "자산군": "주식", "지역": "KR",
              "섹터": "반도체", "전략": "", "위험버킷": "", "수량": 10,
              "평단": 70_000, "현재가": 75_000, "평가금액": 750_000,
              "평가손익": 50_000, "손익률": 7.1, "예상연배당": 0, "배당수익률": 0.0, "비중": 100.0}],
            columns=HOLDINGS_COLUMNS,
        )
        with (
            patch("app.services.backend.daily_pnl_series", return_value=self._empty_pnl()),
            patch("app.services.backend.holdings_df", return_value=holdings),
        ):
            from app.services import backend
            df = backend.asset_curve()
        assert len(df) == 1
        assert float(df["자산"].iloc[0]) == 750_000.0

    def test_real_trades_path_uses_cumulative_pnl(self):
        """체결 내역 있음 → 실 누적손익 경로를 사용한다."""
        from app.services.backend import HOLDINGS_COLUMNS

        pnl_df = pd.DataFrame([
            {"date": "2026-06-01", "pnl": 10_000.0},
            {"date": "2026-06-02", "pnl": 5_000.0},
            {"date": "2026-06-03", "pnl": -3_000.0},
        ])
        holdings = pd.DataFrame(
            [{"종목": "삼성전자", "티커": "005930", "자산군": "주식", "지역": "KR",
              "섹터": "반도체", "전략": "", "위험버킷": "", "수량": 10,
              "평단": 70_000, "현재가": 75_000, "평가금액": 750_000,
              "평가손익": 50_000, "손익률": 7.1, "예상연배당": 0, "배당수익률": 0.0, "비중": 100.0}],
            columns=HOLDINGS_COLUMNS,
        )
        with (
            patch("app.services.backend.daily_pnl_series", return_value=pnl_df),
            patch("app.services.backend.holdings_df", return_value=holdings),
        ):
            from app.services import backend
            df = backend.asset_curve(days=90)
        assert len(df) == 3  # tail(90) of 3 rows = 3 rows
        # 끝값 == base_value (750_000) 확인
        assert float(df["자산"].iloc[-1]) == pytest.approx(750_000.0)
