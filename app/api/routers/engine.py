"""Engine router — /api/engine/*

Endpoints:
  GET /engine/status  — circuit breaker + flags + env (require_session)
"""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.deps import require_session
from app.api.schemas import CircuitBreakerInfo, EngineStatusResponse

router = APIRouter(prefix="/engine", tags=["engine"])


@router.get("/status", response_model=EngineStatusResponse)
def engine_status(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> EngineStatusResponse:
    """Return composite engine health (circuit breaker, flags, env)."""
    from app.ui import backend

    cb = backend.circuit_breaker_status()
    return EngineStatusResponse(
        env=backend.env(),
        auto_trading_enabled=backend.get_flag("auto_trading_enabled"),
        kill_switch_active=backend.get_flag("kill_switch_active"),
        circuit_breaker=CircuitBreakerInfo(
            triggered=cb["triggered"],
            threshold_pct=cb["threshold_pct"],
            consecutive_failures=cb["consecutive_failures"],
            today_pnl=cb["today_pnl"],
        ),
    )
