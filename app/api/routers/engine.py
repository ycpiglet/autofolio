"""Engine router — /api/engine/*

Endpoints:
  GET  /engine/status       — circuit breaker + flags + env (require_session)
  POST /engine/kill-switch  — set kill_switch_active flag (require_owner_csrf)
  POST /engine/auto-trading — set auto_trading_enabled flag (require_owner_csrf)
  POST /engine/run-once     — single-flight engine run (require_owner_csrf)
"""
from __future__ import annotations

import threading
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_owner_csrf, require_session
from app.api.schemas import (
    AutoTradingRequest,
    AutoTradingResponse,
    CircuitBreakerInfo,
    EngineStatusResponse,
    KillSwitchRequest,
    KillSwitchResponse,
    RunOnceResponse,
)
from app.services.investor_profile import investor_profile_completed, username_from_session

router = APIRouter(prefix="/engine", tags=["engine"])

# Single-flight lock for run-once — module-level, process-scoped.
# TestClient is synchronous and single-threaded so tests can acquire
# this lock externally to simulate a concurrent run-once in progress.
_run_once_lock = threading.Lock()


@router.get("/status", response_model=EngineStatusResponse)
def engine_status(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> EngineStatusResponse:
    """Return composite engine health (circuit breaker, flags, env)."""
    from app.services import backend

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


@router.post("/kill-switch", response_model=KillSwitchResponse)
def kill_switch(
    body: KillSwitchRequest,
    _session: Annotated[dict[str, Any], Depends(require_owner_csrf)],
) -> KillSwitchResponse:
    """Set kill_switch_active flag in DB (DB-backed, reflected to engine + Streamlit)."""
    from app.services import backend

    backend.set_flag("kill_switch_active", body.active)
    return KillSwitchResponse(kill_switch_active=backend.get_flag("kill_switch_active"))


@router.post("/auto-trading", response_model=AutoTradingResponse)
def auto_trading(
    body: AutoTradingRequest,
    session: Annotated[dict[str, Any], Depends(require_owner_csrf)],
) -> AutoTradingResponse:
    """Set auto_trading_enabled flag in DB (DB-backed, reflected to engine + Streamlit)."""
    from app.services import backend

    if body.enabled and not investor_profile_completed(username_from_session(session)):
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail={
                "status": "profile_required",
                "message": "투자 프로필 설문 완료 후 자동매매를 켤 수 있습니다.",
            },
        )

    backend.set_flag("auto_trading_enabled", body.enabled)
    return AutoTradingResponse(auto_trading_enabled=backend.get_flag("auto_trading_enabled"))


@router.post("/run-once", response_model=RunOnceResponse)
def run_once(
    session: Annotated[dict[str, Any], Depends(require_owner_csrf)],
) -> RunOnceResponse:
    """Run the trading engine once (single-flight — 409 if already running).

    SAFETY: executes against the configured broker (mock by default).
    Does NOT change KIS_ENV or broker configuration.
    """
    from app.services import backend

    if not investor_profile_completed(username_from_session(session)):
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail={
                "status": "profile_required",
                "message": "투자 프로필 설문 완료 후 엔진을 실행할 수 있습니다.",
            },
        )

    acquired = _run_once_lock.acquire(blocking=False)
    if not acquired:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 실행 중",
        )
    try:
        results = backend.run_engine_once()
        return RunOnceResponse(results=results or [])
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"엔진 실행 오류: {exc}",
        ) from exc
    finally:
        _run_once_lock.release()
