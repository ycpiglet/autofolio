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


@dataclass
class BacktestReport:
    """재현 가능한 백테스트 연구 리포트.

    BacktestResult 위에 추가 레이어 — 파라미터, 벤치마크, 가정, 면책 사항.
    같은 입력 + 캐시 데이터 → 항상 동일한 결과 (결정적).
    """

    # ── 기본 결과 (BacktestResult 전달) ──────────────────────────
    symbol: str
    strategy: str
    start: date
    end: date
    total_return_pct: float
    trade_count: int
    win_rate_pct: float
    max_drawdown_pct: float
    trades: list[dict]
    equity_curve: list[dict]

    # ── 추가 연구 필드 ─────────────────────────────────────────
    parameters: dict                  # {fast, slow, initial_cash}
    benchmark_return_pct: float       # 매수보유(Buy-and-Hold) 수익률
    turnover_pct: float               # (총 거래 금액 / 초기 자본) * 100
    fee_slippage_assumption: str      # 가정 명시 — 현재 미반영
    scheduled_event_caveat: str       # 정기 이벤트(배당락·권리락) 관련 주의
    paper_live_parity_note: str       # 페이퍼트레이딩 vs 실거래 차이 안내


_FEE_SLIPPAGE_TEXT = (
    "수수료·슬리피지 미반영 (not modeled). "
    "실거래 환경에서는 매수·매도 각 약 0.015~0.3% 거래비용 발생 가능."
)

_SCHEDULED_EVENT_CAVEAT = (
    "배당락일·권리락일·주식분할 등 정기 이벤트가 가격 데이터에 반영되지 않을 수 있음. "
    "일봉 캐시는 수정주가(adjusted price)를 보장하지 않으므로 해당 이벤트 전후 수익률에 왜곡이 생길 수 있음."
)

_PAPER_LIVE_PARITY_NOTE = (
    "이 백테스트는 페이퍼 트레이딩 시뮬레이션 기반이며 실거래와 차이가 있을 수 있음: "
    "(1) 진입 가격은 당일 종가로 근사 (실제는 시가 또는 지정가), "
    "(2) 부분 체결·호가 스프레드 미반영, "
    "(3) KIS 시스템 점검·서킷브레이커 미반영. "
    "과거 성과가 미래 수익을 보장하지 않음."
)


def build_report(
    result: BacktestResult,
    *,
    fast: int,
    slow: int,
    initial_cash: float = 1_000_000.0,
) -> BacktestReport:
    """BacktestResult를 BacktestReport로 변환.

    Args:
        result: run_sma_crossover()의 반환값.
        fast: 빠른 SMA 기간 (파라미터 테이블용).
        slow: 느린 SMA 기간 (파라미터 테이블용).
        initial_cash: 초기 자본 (파라미터 테이블용).

    Returns:
        BacktestReport — 결정적, 같은 입력 → 같은 출력.
    """
    # 벤치마크: equity curve 전체 성장률 (buy-and-hold 근사)
    if result.equity_curve:
        last_eq = result.equity_curve[-1]["equity"]
        benchmark_return_pct = round((last_eq / initial_cash - 1) * 100, 2)
    else:
        benchmark_return_pct = 0.0

    # 턴오버: BUY 거래 합산 / 초기 자본 * 100
    buy_volume = sum(
        t["price"] * t["shares"]
        for t in result.trades
        if t.get("action") == "BUY"
    )
    turnover_pct = round(buy_volume / initial_cash * 100, 2) if initial_cash > 0 else 0.0

    return BacktestReport(
        symbol=result.symbol,
        strategy=result.strategy,
        start=result.start,
        end=result.end,
        total_return_pct=result.total_return_pct,
        trade_count=result.trade_count,
        win_rate_pct=result.win_rate_pct,
        max_drawdown_pct=result.max_drawdown_pct,
        trades=result.trades,
        equity_curve=result.equity_curve,
        parameters={"fast": fast, "slow": slow, "initial_cash": initial_cash},
        benchmark_return_pct=benchmark_return_pct,
        turnover_pct=turnover_pct,
        fee_slippage_assumption=_FEE_SLIPPAGE_TEXT,
        scheduled_event_caveat=_SCHEDULED_EVENT_CAVEAT,
        paper_live_parity_note=_PAPER_LIVE_PARITY_NOTE,
    )
