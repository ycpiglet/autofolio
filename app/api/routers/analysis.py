"""Analysis router — /api/analysis/*

Endpoints (all require_session; guest allowed):
  GET /analysis/attribution
  GET /analysis/retro
  GET /analysis/daily-pnl
  GET /analysis/backtest?symbol=&start=&end=&fast=5&slow=20
  GET /analysis/var?horizon_days=10&n_simulations=10000
  GET /analysis/scenario
  GET /analysis/whatif?symbol=&weight=

SAFETY: READ-ONLY. No state-changing endpoint is defined here.
        Errors propagate as non-200 responses (fail-loud, no silent empty 200).
"""
from __future__ import annotations

import dataclasses
from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import require_session
from app.api.schemas import TableResponse
from app.api.serializers import df_records

router = APIRouter(prefix="/analysis", tags=["analysis"])

_SYMBOL_MAX_LEN = 20
_N_SIM_MAX = 50_000


def _validate_symbol(symbol: str) -> str:
    s = symbol.strip()
    if not s or len(s) > _SYMBOL_MAX_LEN or not s.replace(".", "").isalnum():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid symbol: {symbol!r}",
        )
    return s


@router.get("/attribution", response_model=TableResponse)
def attribution(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> TableResponse:
    from app.ui import backend

    return df_records(backend.attribution_df())


@router.get("/retro")
def retro(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> dict[str, Any]:
    from app.ui import backend

    return backend.retro_metrics()


@router.get("/daily-pnl", response_model=TableResponse)
def daily_pnl(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> TableResponse:
    from app.ui import backend

    return df_records(backend.daily_pnl_series())


@router.get("/backtest")
def backtest(
    _session: Annotated[dict[str, Any], Depends(require_session)],
    symbol: Annotated[str, Query(description="종목 코드")] = "",
    start: Annotated[str, Query(description="시작일 YYYY-MM-DD")] = "",
    end: Annotated[str, Query(description="종료일 YYYY-MM-DD")] = "",
    fast: Annotated[int, Query(ge=1, le=200, description="빠른 SMA 기간")] = 5,
    slow: Annotated[int, Query(ge=1, le=500, description="느린 SMA 기간")] = 20,
) -> dict[str, Any]:
    """SMA 크로스오버 백테스트. READ-ONLY."""
    from app.quant.backtest import run_sma_crossover

    sym = _validate_symbol(symbol)

    try:
        start_date = date.fromisoformat(start)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid start date: {start!r}. Expected YYYY-MM-DD.",
        )
    try:
        end_date = date.fromisoformat(end)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid end date: {end!r}. Expected YYYY-MM-DD.",
        )
    if start_date >= end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start must be before end.",
        )
    if fast >= slow:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="fast must be less than slow.",
        )

    result = run_sma_crossover(sym, start_date, end_date, fast=fast, slow=slow)
    d = dataclasses.asdict(result)
    # Convert date objects to ISO strings for JSON serialization
    d["start"] = result.start.isoformat()
    d["end"] = result.end.isoformat()
    # Serialize date values inside trades/equity_curve lists
    for trade in d.get("trades", []):
        if hasattr(trade.get("date"), "isoformat"):
            trade["date"] = trade["date"].isoformat()
    for point in d.get("equity_curve", []):
        if hasattr(point.get("date"), "isoformat"):
            point["date"] = point["date"].isoformat()
    return d


@router.get("/var")
def portfolio_var(
    _session: Annotated[dict[str, Any], Depends(require_session)],
    horizon_days: Annotated[int, Query(ge=1, le=252, description="VaR 기간(일)")] = 10,
    n_simulations: Annotated[int, Query(ge=100, description="시뮬레이션 횟수")] = 10_000,
) -> dict[str, Any]:
    """포트폴리오 몬테카를로 VaR. READ-ONLY. n_simulations 상한 50,000."""
    from app.quant.risk_sim import compute_var
    from app.ui import backend

    # Cap simulations to prevent abuse
    n_sim = min(n_simulations, _N_SIM_MAX)

    # Derive daily returns from pnl series
    pnl_df = backend.daily_pnl_series()

    # Derive portfolio value from account_summary
    summary = backend.account_summary()
    portfolio_value = float(summary.get("tot_evlu_amt", 0.0))

    if pnl_df.empty or portfolio_value <= 0:
        # Return valid empty SimulationResult — explicit markers, not fabricated
        result = compute_var(portfolio_value, [], horizon_days=horizon_days, n_simulations=n_sim)
        return dataclasses.asdict(result)

    # Convert absolute pnl to daily returns (fraction)
    pnl_values = pnl_df["pnl"].tolist()
    daily_returns = [p / portfolio_value for p in pnl_values if portfolio_value > 0]

    result = compute_var(
        portfolio_value,
        daily_returns,
        horizon_days=horizon_days,
        n_simulations=n_sim,
    )
    return dataclasses.asdict(result)


@router.get("/scenario", response_model=TableResponse)
def scenario(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> TableResponse:
    """시나리오 분석 (Bull/Base/Bear). READ-ONLY."""
    from app.ui import backend

    return df_records(backend.scenario_analysis())


@router.get("/whatif")
def whatif(
    _session: Annotated[dict[str, Any], Depends(require_session)],
    symbol: Annotated[str, Query(description="종목 코드")] = "",
    weight: Annotated[float, Query(ge=0.0, le=100.0, description="목표 비중 (%)")] = 0.0,
) -> dict[str, Any]:
    """종목 비중 변경 시 포트폴리오 영향 계산. READ-ONLY."""
    from app.ui import backend

    sym = _validate_symbol(symbol)
    return backend.whatif_weight_change(sym, weight)
