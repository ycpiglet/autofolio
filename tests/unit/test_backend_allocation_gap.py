"""backend.allocation_gap() 라이브 구현 검증.

이 테스트는 TASK-056 회귀 핀(regression pin):
- allocation_gap()이 실 계산 값(holdings_df 기반)을 반환함을 확인한다.
- mock_data.allocation_gap()의 고정값과 '다른 값'을 반환해야 한다.
- 단, 위의 조건은 fixture의 자산군 비중이 mock과 다를 때만 성립하므로
  직접적으로 계산 결과를 검증한다(columns, gap formula, source-of-truth).

TDD: TASK-056 스텁 기준으로는 backend.allocation_gap이 없어서 실패해야 하나,
     리팩터 후 이미 구현되어 있으므로 이 테스트는 regression pin으로 즉시 PASS 한다.
"""
from __future__ import annotations

import pandas as pd

from app.brokers.base import Position
from app.services import backend
from app.services.backend import _build_holdings_df


# ---------------------------------------------------------------------------
# 순수 함수 테스트: _build_holdings_df + allocation_gap 계산 경로
# ---------------------------------------------------------------------------


def test_allocation_gap_uses_holdings_weights(monkeypatch):
    """allocation_gap()은 실 holdings_df의 자산군 비중으로 현재%를 계산한다.

    주식 100% 포지션을 가진 holdings_df를 monkeypatch하면
    allocation_gap()의 현재% 주식 항목이 ~100이어야 한다.
    mock_data.allocation_gap()의 주식 현재%는 그보다 훨씬 작으므로,
    이 테스트는 '라이브 계산'과 'mock 고정값' 이 다름을 증명한다.
    """
    positions = [Position("005930", 10, 70000.0)]
    live_df = _build_holdings_df(
        positions,
        lambda s: 80000.0,
        lambda s: {"name": "삼성전자", "role": "LARGE_CAP_TEST"},
    )
    # 단일 보유종목(주식) → 비중 100%
    assert abs(live_df["비중"].sum() - 100.0) < 0.2

    monkeypatch.setattr(backend, "holdings_df", lambda **kw: live_df)

    result = backend.allocation_gap()

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["자산군", "목표%", "현재%", "갭%"]

    # 주식 현재% ≈ 100 (라이브 계산)
    row = result[result["자산군"] == "주식"].iloc[0]
    assert row["현재%"] >= 90.0, f"주식 현재% 예상 ~100, 실제 {row['현재%']}"

    # gap = 현재% - 목표%
    assert row["갭%"] == round(row["현재%"] - row["목표%"], 1)

    # mock_data는 주식 비중이 절대 ~100이 아님(여러 자산 혼합) → 다른 값
    from app.ui.mock import data as mock_data
    mock_result = mock_data.allocation_gap()
    mock_row = mock_result[mock_result["자산군"] == "주식"]
    if not mock_row.empty:
        assert mock_row.iloc[0]["현재%"] != row["현재%"], (
            "allocation_gap()이 mock과 동일 값을 반환 — 라이브 계산이 mock 경로를 쓰고 있음"
        )


def test_allocation_gap_empty_holdings_returns_negative_targets(monkeypatch):
    """보유종목 없을 때 현재%=0, 갭%=-목표%."""
    empty_df = pd.DataFrame(columns=backend.HOLDINGS_COLUMNS)
    monkeypatch.setattr(backend, "holdings_df", lambda **kw: empty_df)

    result = backend.allocation_gap()

    assert not result.empty
    assert all(result["현재%"] == 0.0)
    assert all(result["갭%"] == -result["목표%"])


def test_allocation_gap_multi_asset_weights(monkeypatch):
    """두 자산군 포지션에서 비중이 올바르게 분배된다."""
    positions = [
        Position("005930", 10, 70000.0),   # 주식: 시가 800,000
        Position("069500", 40, 36500.0),   # ETF:  시가 1,512,000
    ]
    prices = {"005930": 80000.0, "069500": 37800.0}
    live_df = _build_holdings_df(
        positions,
        lambda s: prices[s],
        lambda s: {
            "005930": {"name": "삼성전자", "role": "LARGE_CAP_TEST"},
            "069500": {"name": "KODEX 200", "role": "ETF_TEST"},
        }.get(s, {}),
    )

    monkeypatch.setattr(backend, "holdings_df", lambda **kw: live_df)

    result = backend.allocation_gap(target={"주식": 35, "ETF": 30})

    stock_row = result[result["자산군"] == "주식"].iloc[0]
    etf_row = result[result["자산군"] == "ETF"].iloc[0]

    # 총 평가금액: 800,000 + 1,512,000 = 2,312,000
    # 주식 비중: 800,000 / 2,312,000 * 100 ≈ 34.6%
    # ETF 비중:  1,512,000 / 2,312,000 * 100 ≈ 65.4%
    assert abs(stock_row["현재%"] - 34.6) < 1.0, f"주식 현재% 예상 ~34.6, 실제 {stock_row['현재%']}"
    assert abs(etf_row["현재%"] - 65.4) < 1.0, f"ETF 현재% 예상 ~65.4, 실제 {etf_row['현재%']}"

    # gap = 현재% - 목표%
    assert stock_row["갭%"] == round(stock_row["현재%"] - 35, 1)
    assert etf_row["갭%"] == round(etf_row["현재%"] - 30, 1)


def test_allocation_gap_columns_schema():
    """allocation_gap()이 반환하는 DataFrame은 항상 4-컬럼 스키마를 가진다."""
    # holdings_df()는 mock 환경에서 빈 df 반환하므로 예외 없이 실행된다
    result = backend.allocation_gap()

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["자산군", "목표%", "현재%", "갭%"]
    assert len(result) == 5  # 기본 목표 5개 자산군
