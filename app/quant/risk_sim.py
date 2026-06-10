"""리스크 시뮬레이션 — 몬테카를로 VaR/MDD 추정. [Autofolio]

look-ahead bias 방어:
- 시뮬레이션 입력은 과거 수익률(as_of 이전)만 사용.
- 미래 예측이 아닌 *통계적 분포 추정*.
- 결과는 "X% 확률로 Y원 이상 손실" 형식으로 표현.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from datetime import date


@dataclass
class SimulationResult:
    total_value: float
    n_simulations: int
    horizon_days: int
    var_95: float      # 95% VaR (손실액, 양수)
    var_99: float      # 99% VaR
    cvar_95: float     # 95% CVaR (Expected Shortfall)
    max_drawdown_pct: float  # 시뮬레이션 중 최대낙폭
    percentiles: dict[int, float] = field(default_factory=dict)  # {5: loss, 1: loss}
    note: str = ""


def compute_var(
    portfolio_value: float,
    daily_returns: list[float],
    *,
    horizon_days: int = 10,
    n_simulations: int = 10_000,
    seed: int = 42,
) -> SimulationResult:
    """몬테카를로 시뮬레이션으로 VaR/CVaR/MDD를 추정.

    daily_returns: 과거 일별 수익률 리스트 (소수점, 예: 0.01 = +1%).
    Bootstrap sampling — 정규 분포 가정 없음.
    """
    if not daily_returns or portfolio_value <= 0:
        return SimulationResult(
            total_value=portfolio_value, n_simulations=0,
            horizon_days=horizon_days, var_95=0.0, var_99=0.0,
            cvar_95=0.0, max_drawdown_pct=0.0,
            note="수익률 데이터 없음",
        )

    rng = random.Random(seed)
    final_values: list[float] = []
    sim_mdds: list[float] = []

    for _ in range(n_simulations):
        # Bootstrap: horizon_days 동안 과거 수익률에서 무작위 추출
        sampled = [rng.choice(daily_returns) for _ in range(horizon_days)]
        val = portfolio_value
        peak = val
        mdd = 0.0
        for r in sampled:
            val *= (1 + r)
            if val > peak:
                peak = val
            dd = (peak - val) / peak
            if dd > mdd:
                mdd = dd
        final_values.append(val)
        sim_mdds.append(mdd)

    final_values.sort()
    losses = [portfolio_value - v for v in final_values]  # 양수 = 손실

    n = len(losses)
    idx_95 = int(n * 0.95)
    idx_99 = int(n * 0.99)

    var_95 = losses[idx_95] if idx_95 < n else losses[-1]
    var_99 = losses[idx_99] if idx_99 < n else losses[-1]
    cvar_95 = sum(losses[idx_95:]) / max(len(losses[idx_95:]), 1)
    avg_mdd = sum(sim_mdds) / len(sim_mdds) * 100

    percentiles = {
        1: losses[int(n * 0.01)],
        5: losses[int(n * 0.05)],
        10: losses[int(n * 0.10)],
        25: losses[int(n * 0.25)],
        50: losses[int(n * 0.50)],
    }

    return SimulationResult(
        total_value=portfolio_value,
        n_simulations=n_simulations,
        horizon_days=horizon_days,
        var_95=max(var_95, 0.0),
        var_99=max(var_99, 0.0),
        cvar_95=max(cvar_95, 0.0),
        max_drawdown_pct=round(avg_mdd, 2),
        percentiles={k: max(v, 0.0) for k, v in percentiles.items()},
        note=f"{n_simulations:,}회 시뮬레이션, {horizon_days}일 horizon",
    )


def simulate_portfolio_var(
    holdings_df,  # backend.holdings_df() 결과
    price_cache_fn=None,  # symbol → list[float] closes (optional)
    horizon_days: int = 10,
    n_simulations: int = 5_000,
) -> SimulationResult:
    """보유 포트폴리오 전체의 VaR를 시뮬레이션.

    price_cache_fn이 없으면 표준 분포(mu=0, sigma=0.015)로 대체(추정).
    """
    if holdings_df is None or holdings_df.empty:
        return SimulationResult(
            total_value=0.0, n_simulations=0,
            horizon_days=horizon_days, var_95=0.0, var_99=0.0,
            cvar_95=0.0, max_drawdown_pct=0.0, note="보유 종목 없음",
        )

    total_value = float(holdings_df["평가금액"].sum())

    # 포트폴리오 일별 수익률 추정
    if price_cache_fn is not None:
        portfolio_returns: list[float] = []
        weights = (holdings_df["비중"] / 100).tolist()
        symbols = holdings_df["티커"].tolist()
        sym_returns: list[list[float]] = []
        for sym in symbols:
            closes = price_cache_fn(sym)
            if closes and len(closes) > 1:
                rets = [(closes[i] / closes[i - 1] - 1) for i in range(1, len(closes))]
                sym_returns.append(rets)
            else:
                sym_returns.append([])

        # 가장 짧은 시계열 길이로 맞춤
        min_len = min((len(r) for r in sym_returns if r), default=0)
        if min_len > 0:
            for i in range(min_len):
                port_ret = sum(
                    w * r[-(min_len - i)] if len(r) >= min_len - i else 0.0
                    for w, r in zip(weights, sym_returns)
                )
                portfolio_returns.append(port_ret)
    else:
        # 데이터 없음 → 시장 평균 가정 (일 변동성 1.5%)
        rng = random.Random(42)
        portfolio_returns = [rng.gauss(0.0003, 0.015) for _ in range(252)]

    return compute_var(
        total_value, portfolio_returns,
        horizon_days=horizon_days,
        n_simulations=n_simulations,
    )
