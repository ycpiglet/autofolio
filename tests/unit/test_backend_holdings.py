"""backend.holdings_df 의 순수 구성 헬퍼 테스트 (네트워크/DB 없음, pandas 만 사용)."""
from __future__ import annotations

from app.brokers.base import Position
from app.ui.backend import HOLDINGS_COLUMNS, _build_holdings_df


def test_build_holdings_empty_returns_schema():
    df = _build_holdings_df([], lambda s: 0.0, lambda s: {})
    assert list(df.columns) == HOLDINGS_COLUMNS
    assert df.empty


def test_build_holdings_computes_pnl_class_and_weight():
    positions = [Position("005930", 10, 70000.0), Position("069500", 40, 36500.0)]
    prices = {"005930": 77000.0, "069500": 37800.0}
    meta = {
        "005930": {"name": "삼성전자", "role": "LARGE_CAP_TEST"},
        "069500": {"name": "KODEX 200", "role": "ETF_TEST"},
    }
    df = _build_holdings_df(positions, lambda s: prices[s], lambda s: meta.get(s, {}))

    assert list(df.columns) == HOLDINGS_COLUMNS
    r0 = df[df["티커"] == "005930"].iloc[0]
    assert r0["종목"] == "삼성전자"
    assert r0["자산군"] == "주식"
    assert r0["평가금액"] == 770000
    assert r0["평가손익"] == 70000          # (77000-70000)*10
    assert r0["손익률"] == 10.0
    assert df[df["티커"] == "069500"].iloc[0]["자산군"] == "ETF"
    # 비중 합은 ~100%
    assert abs(df["비중"].sum() - 100.0) < 0.5


def test_build_holdings_handles_missing_avg_and_name_fallback():
    df = _build_holdings_df([Position("005930", 5, None)], lambda s: 100.0, lambda s: {})
    row = df.iloc[0]
    assert row["평단"] == 0
    assert row["손익률"] == 0.0
    assert row["종목"] == "005930"  # 화이트리스트 메타 없으면 티커로 폴백
