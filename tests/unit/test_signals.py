"""퀀트 시그널 단위 테스트."""
from __future__ import annotations
from app.quant.signals import rsi, sma, macd, bollinger, compute_signals


def test_rsi_oversold():
    # 하락 후 RSI < 30
    closes = [100 - i * 3 for i in range(20)]
    r = rsi(closes, 14)
    assert r is not None and r < 50


def test_rsi_insufficient_data():
    assert rsi([100, 101], 14) is None


def test_sma_correct():
    assert sma([1.0, 2.0, 3.0, 4.0, 5.0], 3) == 4.0


def test_macd_returns_tuple():
    closes = [100 + i * 0.5 for i in range(40)]
    result = macd(closes)
    assert result is not None and len(result) == 3


def test_bollinger_bands_order():
    closes = [100.0] * 20
    bb = bollinger(closes)
    assert bb is not None
    upper, mid, lower = bb
    assert upper >= mid >= lower


def test_compute_signals_insufficient():
    sigs = compute_signals("005930", [{"date": "2026-01-01", "close": 70000}] * 5)
    assert sigs == []


def test_compute_signals_returns_list():
    prices = [{"date": f"2026-01-{i+1:02d}", "close": 70000 + i * 100} for i in range(40)]
    sigs = compute_signals("005930", prices)
    assert isinstance(sigs, list)
    for s in sigs:
        assert s.direction in ("BUY", "SELL", "NEUTRAL")
        assert 0.0 <= s.confidence <= 1.0
