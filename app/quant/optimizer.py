"""포트폴리오 최적화 — 균등비중 / 역변동성 비중. [Autofolio]

복잡한 MVO(평균-분산) 대신 robust하고 단순한 전략을 제공한다:
1. 균등비중 (Equal Weight) — 모든 자산에 동일 비중
2. 역변동성 (Inverse Volatility) — 변동성이 낮을수록 더 많은 비중
3. 모멘텀 가중 (Momentum) — 최근 수익률이 높을수록 더 많은 비중

look-ahead bias: 최적화는 as_of 날짜까지의 데이터만 사용.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date


@dataclass
class OptimizationResult:
    strategy: str
    weights: dict[str, float]  # symbol → weight (합계 ≈ 1.0)
    note: str = ""


def equal_weight(symbols: list[str]) -> OptimizationResult:
    """균등 비중."""
    n = len(symbols)
    if n == 0:
        return OptimizationResult("equal_weight", {})
    w = round(1.0 / n, 4)
    return OptimizationResult(
        "equal_weight",
        {s: w for s in symbols},
        f"{n}개 종목 균등 비중 ({w*100:.1f}%씩)",
    )


def inverse_volatility(
    prices_by_symbol: dict[str, list[float]],
    lookback: int = 20,
) -> OptimizationResult:
    """역변동성 비중 — 변동성이 낮을수록 더 많은 비중.

    prices_by_symbol: {symbol: [close prices, 최신 순서로]}
    """
    vols: dict[str, float] = {}
    for sym, closes in prices_by_symbol.items():
        if len(closes) < lookback + 1:
            vols[sym] = 1e-6  # 데이터 부족 → 매우 낮은 비중
            continue
        rets = [(closes[i] / closes[i - 1] - 1) for i in range(-lookback, 0)]
        mean_r = sum(rets) / len(rets)
        variance = sum((r - mean_r) ** 2 for r in rets) / len(rets)
        vols[sym] = math.sqrt(variance) if variance > 0 else 1e-6

    inv_vols = {s: 1.0 / v for s, v in vols.items()}
    total = sum(inv_vols.values())
    if total == 0:
        return equal_weight(list(prices_by_symbol.keys()))
    weights = {s: round(iv / total, 4) for s, iv in inv_vols.items()}
    return OptimizationResult(
        "inverse_volatility",
        weights,
        f"역변동성 비중 (lookback={lookback}일)",
    )


def momentum_weight(
    prices_by_symbol: dict[str, list[float]],
    lookback: int = 60,
) -> OptimizationResult:
    """모멘텀 가중 비중 — 최근 수익률이 높을수록 더 많은 비중.

    음수 모멘텀 종목은 비중 0(포함 제외).
    """
    moms: dict[str, float] = {}
    for sym, closes in prices_by_symbol.items():
        if len(closes) < lookback:
            moms[sym] = 0.0
            continue
        ret = closes[-1] / closes[-lookback] - 1
        moms[sym] = max(ret, 0.0)

    total = sum(moms.values())
    if total <= 0:
        return equal_weight(list(prices_by_symbol.keys()))

    weights = {s: round(m / total, 4) for s, m in moms.items()}
    return OptimizationResult(
        "momentum",
        {s: w for s, w in weights.items() if w > 0},
        f"모멘텀 가중 (lookback={lookback}일, 음수 모멘텀 제외)",
    )


def suggest_rebalancing(
    current_weights: dict[str, float],
    target_weights: dict[str, float],
    total_value: float,
    threshold_pct: float = 2.0,
) -> list[dict]:
    """목표 비중 대비 현재 비중 차이가 threshold 이상인 종목의 리밸런싱 제안.

    반환: [{symbol, current_pct, target_pct, gap_pct, action, estimated_amount}]
    """
    suggestions = []
    all_symbols = set(current_weights) | set(target_weights)
    for sym in sorted(all_symbols):
        cur = current_weights.get(sym, 0.0) * 100
        tgt = target_weights.get(sym, 0.0) * 100
        gap = tgt - cur
        if abs(gap) >= threshold_pct:
            action = "매수" if gap > 0 else "매도"
            amount = abs(gap / 100 * total_value)
            suggestions.append({
                "symbol": sym,
                "current_pct": round(cur, 1),
                "target_pct": round(tgt, 1),
                "gap_pct": round(gap, 1),
                "action": action,
                "estimated_amount": round(amount),
            })
    return sorted(suggestions, key=lambda x: abs(x["gap_pct"]), reverse=True)
