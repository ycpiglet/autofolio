"""퀀트 시그널 모듈 — 기술적 지표·팩터 계산. [Autofolio]

look-ahead bias 방어 원칙:
- 모든 계산은 해당 시점까지의 데이터만 사용 (rolling, no future leakage).
- as_of 파라미터로 데이터 커트오프를 강제한다.
- 시그널은 '다음 날 진입 기준'으로 해석 (현재 시점 신호 → 익일 행동).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Literal


@dataclass
class Signal:
    symbol: str
    date: str
    signal_type: str
    value: float
    direction: Literal["BUY", "SELL", "NEUTRAL"]
    confidence: float  # 0.0~1.0
    note: str = ""


def rsi(closes: list[float], period: int = 14) -> float | None:
    """Relative Strength Index (RSI). 기간 부족 시 None."""
    if len(closes) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, period + 1):
        diff = closes[-period - 1 + i] - closes[-period - 1 + i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def sma(closes: list[float], period: int) -> float | None:
    if len(closes) < period:
        return None
    return sum(closes[-period:]) / period


def macd(
    closes: list[float],
    fast: int = 12,
    slow: int = 26,
    signal_period: int = 9,
) -> tuple[float, float, float] | None:
    """MACD(macd_line, signal_line, histogram). None if insufficient data."""
    if len(closes) < slow + signal_period:
        return None

    def ema(data: list[float], n: int) -> list[float]:
        k = 2 / (n + 1)
        result = [sum(data[:n]) / n]
        for p in data[n:]:
            result.append(p * k + result[-1] * (1 - k))
        return result

    fast_ema = ema(closes, fast)
    slow_ema = ema(closes, slow)
    offset = slow - fast
    macd_line = [f - s for f, s in zip(fast_ema[offset:], slow_ema)]
    if len(macd_line) < signal_period:
        return None
    signal_line = ema(macd_line, signal_period)
    histogram = macd_line[-1] - signal_line[-1]
    return macd_line[-1], signal_line[-1], histogram


def bollinger(closes: list[float], period: int = 20, k: float = 2.0) -> tuple[float, float, float] | None:
    """볼린저 밴드 (upper, middle, lower). None if insufficient data."""
    if len(closes) < period:
        return None
    window = closes[-period:]
    middle = sum(window) / period
    std = math.sqrt(sum((x - middle) ** 2 for x in window) / period)
    return middle + k * std, middle, middle - k * std


def compute_signals(
    symbol: str,
    prices: list[dict],  # [{date, close, ...}]
    as_of: date | None = None,
) -> list[Signal]:
    """주어진 일봉 가격으로 기술적 시그널 계산.

    반환: Signal 목록. 빈 리스트 = 데이터 부족 또는 중립.
    """
    if not prices:
        return []

    cutoff = as_of.isoformat() if as_of else None
    data = [p for p in prices if (not cutoff or p["date"] <= cutoff)]
    if len(data) < 30:
        return []

    closes = [float(p["close"]) for p in data]
    latest_date = data[-1]["date"]
    signals: list[Signal] = []

    # RSI
    r = rsi(closes)
    if r is not None:
        if r < 30:
            signals.append(Signal(symbol, latest_date, "RSI", r, "BUY", 0.7, f"RSI 과매도({r:.1f})"))
        elif r > 70:
            signals.append(Signal(symbol, latest_date, "RSI", r, "SELL", 0.7, f"RSI 과매수({r:.1f})"))
        else:
            signals.append(Signal(symbol, latest_date, "RSI", r, "NEUTRAL", 0.3, f"RSI 중립({r:.1f})"))

    # SMA 크로스
    fast_s = sma(closes, 5)
    slow_s = sma(closes, 20)
    if fast_s and slow_s:
        if fast_s > slow_s * 1.005:
            signals.append(Signal(symbol, latest_date, "SMA_CROSS", fast_s / slow_s, "BUY", 0.6, "5일>20일 골든크로스"))
        elif fast_s < slow_s * 0.995:
            signals.append(Signal(symbol, latest_date, "SMA_CROSS", fast_s / slow_s, "SELL", 0.6, "5일<20일 데드크로스"))

    # MACD
    m = macd(closes)
    if m:
        ml, sl, hist = m
        if hist > 0 and ml > sl:
            signals.append(Signal(symbol, latest_date, "MACD", hist, "BUY", 0.65, f"MACD 상향({hist:.0f})"))
        elif hist < 0 and ml < sl:
            signals.append(Signal(symbol, latest_date, "MACD", hist, "SELL", 0.65, f"MACD 하향({hist:.0f})"))

    # 볼린저 밴드
    bb = bollinger(closes)
    cur = closes[-1]
    if bb:
        upper, mid, lower = bb
        if cur <= lower:
            signals.append(Signal(symbol, latest_date, "BOLLINGER", cur, "BUY", 0.6, "하단 밴드 도달"))
        elif cur >= upper:
            signals.append(Signal(symbol, latest_date, "BOLLINGER", cur, "SELL", 0.6, "상단 밴드 도달"))

    return signals
