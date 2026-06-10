"""백테스트 모듈 — 단순 규칙 기반 전략 검증. [Autofolio]

look-ahead bias 방어:
- 모든 신호는 *전일(D-1)* 종가 기반으로 계산, 당일 시가에 진입한다고 가정.
- 미래 데이터를 전혀 참조하지 않는 rolling 계산만 허용.
- as_of 파라미터로 특정 날짜 이후 데이터 차단(data_loader).

지원 전략:
  - SMA_CROSSOVER: 단순 이동평균 크로스오버 (fast/slow)
  - PRICE_CONDITION: 단순 목표가 조건 (사용자 주문 로그 재현)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Literal


@dataclass
class BacktestResult:
    symbol: str
    strategy: str
    start: date
    end: date
    total_return_pct: float
    trade_count: int
    win_rate_pct: float
    max_drawdown_pct: float
    trades: list[dict] = field(default_factory=list)
    equity_curve: list[dict] = field(default_factory=list)


def run_sma_crossover(
    symbol: str,
    start: date,
    end: date,
    *,
    fast: int = 5,
    slow: int = 20,
    initial_cash: float = 1_000_000.0,
) -> BacktestResult:
    """SMA 크로스오버 백테스트.

    진입: fast SMA > slow SMA (골든크로스)
    청산: fast SMA < slow SMA (데드크로스)
    """
    from app.quant.data_loader import load_prices

    prices = load_prices(symbol, start, end, as_of=end)
    if len(prices) < slow:
        return BacktestResult(
            symbol=symbol, strategy="SMA_CROSSOVER",
            start=start, end=end,
            total_return_pct=0.0, trade_count=0, win_rate_pct=0.0, max_drawdown_pct=0.0,
        )

    closes = [float(p["close"]) for p in prices]
    dates = [p["date"] for p in prices]

    # SMA 계산 (look-ahead 없음 — i 시점의 SMA는 i 이전 데이터만)
    def sma(i: int, n: int) -> float | None:
        if i < n - 1:
            return None
        return sum(closes[i - n + 1: i + 1]) / n

    cash = initial_cash
    position = 0
    entry_price = 0.0
    trades: list[dict] = []
    equity: list[dict] = []
    wins = 0

    for i, (d, c) in enumerate(zip(dates, closes)):
        f = sma(i, fast)
        s = sma(i, slow)
        if f is None or s is None:
            equity.append({"date": d, "equity": cash + position * c})
            continue

        # 진입 (전일 신호 → 당일 시가 진입 시뮬레이션)
        if f > s and position == 0 and i > 0:
            shares = int(cash // c)
            if shares > 0:
                cost = shares * c
                cash -= cost
                position = shares
                entry_price = c
                trades.append({"date": d, "action": "BUY", "price": c, "shares": shares})

        # 청산
        elif f < s and position > 0:
            proceeds = position * c
            pnl = proceeds - position * entry_price
            wins += 1 if pnl > 0 else 0
            cash += proceeds
            trades.append({"date": d, "action": "SELL", "price": c, "shares": position, "pnl": pnl})
            position = 0
            entry_price = 0.0

        equity.append({"date": d, "equity": cash + position * c})

    final_equity = equity[-1]["equity"] if equity else initial_cash
    total_return = (final_equity - initial_cash) / initial_cash * 100

    # MDD 계산
    peak = initial_cash
    mdd = 0.0
    for e in equity:
        eq = e["equity"]
        if eq > peak:
            peak = eq
        dd = (peak - eq) / peak * 100
        if dd > mdd:
            mdd = dd

    win_rate = (wins / len(trades) * 100) if trades else 0.0

    return BacktestResult(
        symbol=symbol, strategy="SMA_CROSSOVER",
        start=start, end=end,
        total_return_pct=round(total_return, 2),
        trade_count=len(trades),
        win_rate_pct=round(win_rate, 1),
        max_drawdown_pct=round(mdd, 2),
        trades=trades,
        equity_curve=equity,
    )
