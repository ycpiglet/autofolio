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

    def test_prod_no_trades_returns_single_point(self):
        """prod 환경 + 체결 내역 없음 + 보유 잔고 있음 → 단일 관측값 (실계정 경로 유지)."""
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
            patch("app.services.backend.env", return_value="prod"),
        ):
            from app.services import backend
            df = backend.asset_curve()
        assert len(df) == 1
        assert float(df["자산"].iloc[0]) == 750_000.0
        assert df.attrs.get("is_demo") is False

    def test_real_trades_path_uses_cumulative_pnl(self):
        """체결 내역 충분(>=14) → 실 누적손익 경로를 사용한다."""
        import datetime
        from app.services.backend import HOLDINGS_COLUMNS, _DEMO_MIN_REAL_POINTS

        # 14행 이상의 PNL 데이터를 생성 (자동전환 임계값 충족)
        base_date = datetime.date(2026, 5, 1)
        pnl_rows = [
            {"date": str(base_date + datetime.timedelta(days=i)), "pnl": 1_000.0 * (i + 1)}
            for i in range(_DEMO_MIN_REAL_POINTS)
        ]
        pnl_df = pd.DataFrame(pnl_rows)
        holdings = pd.DataFrame(
            [{"종목": "삼성전자", "티커": "005930", "자산군": "주식", "지역": "KR",
              "섹터": "반도체", "전략": "", "위험버킷": "", "수량": 10,
              "평단": 70_000, "현재가": 75_000, "평가금액": 750_000,
              "평가손익": 50_000, "손익률": 7.1, "예상연배당": 0, "배당수익률": 0.0, "비중": 100.0}],
            columns=HOLDINGS_COLUMNS,
        )
        with (
            # 임계값 math가 아니라 명시적으로 non-prod rich-history 경로를 고정한다
            # (_DEMO_MIN_REAL_POINTS 변경에도 이 테스트가 실 데이터 경로를 검증하도록).
            patch("app.services.backend.env", return_value="paper"),
            patch("app.services.backend.daily_pnl_series", return_value=pnl_df),
            patch("app.services.backend.holdings_df", return_value=holdings),
        ):
            from app.services import backend
            df = backend.asset_curve(days=90)
        assert len(df) == _DEMO_MIN_REAL_POINTS  # tail(90) of 14 rows = 14 rows
        # 끝값 == base_value (750_000) 확인
        assert float(df["자산"].iloc[-1]) == pytest.approx(750_000.0)
        # 실 데이터 경로 — is_demo=False
        assert df.attrs.get("is_demo") is False


# ---------------------------------------------------------------------------
# Task 3-2: sparse-history 데모 곡선 — 비-prod 한정·prod 제외·앵커·자동전환
# ---------------------------------------------------------------------------


class TestAssetCurveSparseDemo:
    """비-prod sparse-history 시나리오: 4조건 검증."""

    def _empty_pnl(self) -> pd.DataFrame:
        return pd.DataFrame(columns=["date", "pnl"])

    def _sparse_pnl(self, n: int = 3) -> pd.DataFrame:
        """n개의 실 PNL 행 (n < _DEMO_MIN_REAL_POINTS)."""
        import datetime
        base_date = datetime.date(2026, 6, 1)
        rows = [{"date": str(base_date + datetime.timedelta(days=i)), "pnl": 1_000.0} for i in range(n)]
        return pd.DataFrame(rows)

    def _rich_pnl(self) -> pd.DataFrame:
        """_DEMO_MIN_REAL_POINTS 이상의 실 PNL 행."""
        import datetime
        from app.services.backend import _DEMO_MIN_REAL_POINTS
        base_date = datetime.date(2026, 5, 1)
        rows = [{"date": str(base_date + datetime.timedelta(days=i)), "pnl": 1_000.0} for i in range(_DEMO_MIN_REAL_POINTS)]
        return pd.DataFrame(rows)

    def _holdings_with_value(self, value: float = 7_800_000.0) -> "pd.DataFrame":
        from app.services.backend import HOLDINGS_COLUMNS
        return pd.DataFrame(
            [{"종목": "삼성전자", "티커": "005930", "자산군": "주식", "지역": "KR",
              "섹터": "반도체", "전략": "", "위험버킷": "", "수량": 10,
              "평단": 70_000, "현재가": 780_000, "평가금액": value,
              "평가손익": 100_000, "손익률": 1.3, "예상연배당": 0, "배당수익률": 0.0, "비중": 100.0}],
            columns=HOLDINGS_COLUMNS,
        )

    def _empty_holdings(self) -> "pd.DataFrame":
        from app.services.backend import HOLDINGS_COLUMNS
        return pd.DataFrame(columns=HOLDINGS_COLUMNS)

    # ── 조건 1 & 2: sparse + 비-prod → 데모 발동 ─────────────────────────

    def test_paper_sparse_fires_demo(self):
        """KIS_ENV=paper + sparse(3포인트) → is_demo=True 데모 곡선 발동."""
        with (
            patch("app.services.backend.daily_pnl_series", return_value=self._sparse_pnl(3)),
            patch("app.services.backend.holdings_df", return_value=self._holdings_with_value()),
            patch("app.services.backend.env", return_value="paper"),
        ):
            from app.services import backend
            df = backend.asset_curve(days=90)
        assert df.attrs.get("is_demo") is True
        assert len(df) == 90

    def test_mock_sparse_fires_demo(self):
        """KIS_ENV=mock + sparse → is_demo=True."""
        with (
            patch("app.services.backend.daily_pnl_series", return_value=self._empty_pnl()),
            patch("app.services.backend.holdings_df", return_value=self._holdings_with_value()),
            patch("app.services.backend.env", return_value="mock"),
        ):
            from app.services import backend
            df = backend.asset_curve(days=90)
        assert df.attrs.get("is_demo") is True
        assert len(df) == 90

    # ── 조건 3: 실 현재총액 앵커 ─────────────────────────────────────────

    def test_sparse_demo_anchored_to_base_value(self):
        """비-prod sparse + base_value > 0 → 데모 곡선 끝점이 base_value에 고정."""
        base_value = 7_800_000.0
        with (
            patch("app.services.backend.daily_pnl_series", return_value=self._sparse_pnl(3)),
            patch("app.services.backend.holdings_df", return_value=self._holdings_with_value(base_value)),
            patch("app.services.backend.env", return_value="paper"),
        ):
            from app.services import backend
            df = backend.asset_curve(days=90)
        last = float(df["자산"].iloc[-1])
        assert abs(last - base_value) < 1.0, f"끝점 {last} != base_value {base_value}"

    def test_mock_empty_nominal_preserved(self):
        """mock-empty (base_value==0) → 기존 nominal ₩150만 유지."""
        from app.services.backend import _DEMO_INITIAL_CAPITAL
        with (
            patch("app.services.backend.daily_pnl_series", return_value=self._empty_pnl()),
            patch("app.services.backend.holdings_df", return_value=self._empty_holdings()),
            patch("app.services.backend.env", return_value="mock"),
        ):
            from app.services import backend
            df = backend.asset_curve(days=90)
        last = float(df["자산"].iloc[-1])
        assert abs(last - _DEMO_INITIAL_CAPITAL) < 1.0
        assert df.attrs.get("is_demo") is True

    # ── 조건 2: prod 절대 미발동 ────────────────────────────────────────

    def test_prod_sparse_never_fires_demo(self):
        """prod 환경에서는 실 포인트가 sparse해도 데모 곡선 미발동."""
        with (
            patch("app.services.backend.daily_pnl_series", return_value=self._sparse_pnl(3)),
            patch("app.services.backend.holdings_df", return_value=self._holdings_with_value()),
            patch("app.services.backend.env", return_value="prod"),
        ):
            from app.services import backend
            df = backend.asset_curve(days=90)
        # prod: 실 데이터 경로 사용 (3행)
        assert df.attrs.get("is_demo") is False
        assert len(df) == 3  # sparse 실데이터 그대로

    def test_prod_empty_pnl_no_demo(self):
        """prod 환경에서 체결 내역 없음 → 단일 관측값(데모 아님)."""
        with (
            patch("app.services.backend.daily_pnl_series", return_value=self._empty_pnl()),
            patch("app.services.backend.holdings_df", return_value=self._holdings_with_value()),
            patch("app.services.backend.env", return_value="prod"),
        ):
            from app.services import backend
            df = backend.asset_curve(days=90)
        assert df.attrs.get("is_demo") is False
        assert len(df) == 1

    # ── 조건 1: 자동전환 (auto-yield) ───────────────────────────────────

    def test_auto_yield_rich_history_uses_real_data(self):
        """비-prod + 실 포인트 >= _DEMO_MIN_REAL_POINTS → 자동전환하여 실 데이터 반환."""
        with (
            patch("app.services.backend.daily_pnl_series", return_value=self._rich_pnl()),
            patch("app.services.backend.holdings_df", return_value=self._holdings_with_value()),
            patch("app.services.backend.env", return_value="paper"),
        ):
            from app.services import backend
            df = backend.asset_curve(days=90)
        assert df.attrs.get("is_demo") is False
        # 실 누적 PnL 경로 사용 확인 (is_demo=False, 끝점 = base_value)
        assert float(df["자산"].iloc[-1]) == pytest.approx(7_800_000.0)
