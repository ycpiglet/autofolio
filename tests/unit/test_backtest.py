"""백테스트 모듈 단위 테스트 — 실 API 없이 캐시 데이터로 검증."""
from __future__ import annotations

from datetime import date

import pytest

from app.quant.backtest import run_sma_crossover
from app.quant.data_loader import cache_prices, load_prices, _price_cache_db


@pytest.fixture(autouse=True)
def temp_cache(tmp_path, monkeypatch):
    """각 테스트마다 별도 캐시 DB 사용."""
    import app.quant.data_loader as dl
    monkeypatch.setattr(dl, "_price_cache_db", lambda: tmp_path / "price_cache.db")
    yield


def _seed(symbol: str, prices: list[float], start: date):
    rows = [
        {"date": (start.replace(day=start.day + i)).isoformat(),
         "open": p, "high": p * 1.01, "low": p * 0.99, "close": p, "volume": 100_000}
        for i, p in enumerate(prices)
    ]
    cache_prices(symbol, rows)
    return rows


def test_load_prices_point_in_time():
    s = date(2026, 1, 2)
    _seed("005930", [70_000] * 30, s)
    rows = load_prices("005930", s, date(2026, 2, 1), as_of=date(2026, 1, 15))
    # as_of=15일이면 15일까지만 반환
    assert all(r["date"] <= "2026-01-15" for r in rows)


def test_sma_crossover_returns_result():
    s = date(2026, 1, 2)
    # 상승 후 하락하는 가격으로 크로스오버 발생 유도
    prices = [70_000 + i * 200 for i in range(15)] + [71_000 - i * 150 for i in range(15)]
    _seed("005930", prices, s)
    result = run_sma_crossover("005930", s, date(2026, 2, 1), fast=5, slow=10)
    assert result.symbol == "005930"
    assert result.strategy == "SMA_CROSSOVER"
    assert isinstance(result.total_return_pct, float)
    assert isinstance(result.max_drawdown_pct, float)
    assert len(result.equity_curve) > 0


def test_sma_crossover_insufficient_data():
    s = date(2026, 1, 2)
    _seed("005930", [70_000] * 5, s)  # 5개 < slow=20
    result = run_sma_crossover("005930", s, date(2026, 1, 10))
    assert result.trade_count == 0
    assert result.total_return_pct == 0.0
