"""Engine router — /api/engine/*

Endpoints:
  GET  /engine/status       — circuit breaker + flags + env (require_app_user)
  POST /engine/kill-switch  — set kill_switch_active flag (require_owner_csrf)
  POST /engine/auto-trading — set auto_trading_enabled flag (require_owner_csrf)
  POST /engine/run-once     — single-flight engine run (require_owner_csrf)
"""
from __future__ import annotations

import threading
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_app_user, require_owner_csrf
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

# Multitenant Phase 3: per-user single-flight locks (flag-ON only). When the
# multi-tenant flag is OFF, the global _run_once_lock above is used exactly as
# before — one global run-once is single-flighted process-wide (byte-identical
# to today). When ON, each user gets an independent lock so one user's run does
# not 409-block another user's run.
_user_run_locks_lock = threading.Lock()
_user_run_locks: dict[str, threading.Lock] = {}


def _run_lock_for(user_id: str) -> threading.Lock:
    """Return (creating on first use) the per-user single-flight run lock."""
    with _user_run_locks_lock:
        lock = _user_run_locks.get(user_id)
        if lock is None:
            lock = threading.Lock()
            _user_run_locks[user_id] = lock
        return lock


@router.get("/status", response_model=EngineStatusResponse)
def engine_status(
    _session: Annotated[dict[str, Any], Depends(require_app_user)],
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
    from app.services import flags as _flags

    if body.enabled and not _flags.auto_exec_enabled():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "status": "auto_exec_locked",
                "message": "자동실행이 잠겨 있습니다: AUTOFOLIO_AUTO_EXEC_ENABLED 환경 변수를 설정하지 않으면 켤 수 없습니다.",
            },
        )

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
    from app.services import flags as _flags

    username = username_from_session(session)
    if not investor_profile_completed(username):
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail={
                "status": "profile_required",
                "message": "투자 프로필 설문 완료 후 엔진을 실행할 수 있습니다.",
            },
        )

    # Phase 3: per-user single-flight + per-user engine run (flag-gated).
    # FLAG-OFF: run_uid is None → global _run_once_lock + global run_engine_once(),
    # byte-identical to the pre-Phase-3 path.
    run_uid = username if (_flags.multi_tenant_enabled() and username) else None
    run_lock = _run_lock_for(run_uid) if run_uid is not None else _run_once_lock

    acquired = run_lock.acquire(blocking=False)
    if not acquired:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 실행 중",
        )
    try:
        results = (
            backend.run_engine_once(user_id=run_uid)
            if run_uid is not None
            else backend.run_engine_once()
        )
        return RunOnceResponse(results=results or [])
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"엔진 실행 오류: {exc}",
        ) from exc
    finally:
        run_lock.release()
