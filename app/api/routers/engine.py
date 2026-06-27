"""Engine router — /api/engine/*

Endpoints:
  GET  /engine/status       — circuit breaker + flags + env (require_app_user)
  POST /engine/kill-switch  — set kill_switch_active flag (require_owner_csrf)
  POST /engine/auto-trading — set auto_trading_enabled flag (require_owner_csrf)
  POST /engine/run-once     — single-flight engine run (require_owner_csrf)
"""
from __future__ import annotations

import collections as _collections
import threading
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_app_user, require_owner, require_owner_csrf
from app.api.schemas import (
    AutoTradingRequest,
    AutoTradingResponse,
    CircuitBreakerInfo,
    EngineStatusResponse,
    KillSwitchRequest,
    KillSwitchResponse,
    RunOnceResponse,
    UserEngineStateResponse,
    UserReenableResponse,
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
_USER_LOCKS_MAX: int = 1024  # max per-user run locks in memory
_user_run_locks_lock = threading.Lock()
_user_run_locks: "_collections.OrderedDict[str, threading.Lock]" = _collections.OrderedDict()
# Checkout refcount: incremented by _run_lock_for, decremented by _release_run_lock.
# While count > 0 the entry is shielded from eviction (closes the TOCTOU window
# between _run_lock_for returning and the caller calling acquire()).
_user_run_lock_checkouts: "dict[str, int]" = {}


def _run_lock_for(user_id: str) -> threading.Lock:
    """Return (creating on first use) the per-user single-flight run lock.

    Atomically increments a checkout refcount for *user_id* so the returned
    lock is protected from eviction until _release_run_lock(user_id) is
    called.  This closes the TOCTOU window where a lock handed out but not
    yet acquired could be evicted by a concurrent eviction scan, causing two
    runs for the same user to proceed in parallel.

    Maintains an LRU-bounded pool of size _USER_LOCKS_MAX.  Eviction skips
    any entry whose checkout count > 0 (in addition to the existing held-lock
    acquire probe for defense-in-depth).  _release_run_lock MUST be called on
    ALL exit paths of the caller (including the 409 path where acquire returns
    False).
    """
    with _user_run_locks_lock:
        if user_id in _user_run_locks:
            _user_run_locks.move_to_end(user_id)
        else:
            _user_run_locks[user_id] = threading.Lock()
        # Increment checkout BEFORE eviction so our own entry is shielded.
        _user_run_lock_checkouts[user_id] = _user_run_lock_checkouts.get(user_id, 0) + 1
        lock = _user_run_locks[user_id]
        # Evict oldest idle locks when over capacity
        while len(_user_run_locks) > _USER_LOCKS_MAX:
            evicted = False
            for uid_to_evict, lock_to_evict in list(_user_run_locks.items()):
                if uid_to_evict == user_id:
                    continue  # never evict the lock we are about to return
                if _user_run_lock_checkouts.get(uid_to_evict, 0) > 0:
                    continue  # checked out — caller has not released yet, do not evict
                if lock_to_evict.acquire(blocking=False):
                    lock_to_evict.release()   # immediately release; was idle
                    del _user_run_locks[uid_to_evict]
                    _user_run_lock_checkouts.pop(uid_to_evict, None)
                    evicted = True
                    break
            if not evicted:
                break  # all candidates are held or checked out; stop eviction
        return lock


def _release_run_lock(user_id: str) -> None:
    """Decrement the checkout refcount for *user_id*.

    Must be called on ALL exit paths of the run_once caller — including the
    409 path where acquire() returned False — to mirror every _run_lock_for
    increment.
    """
    with _user_run_locks_lock:
        count = _user_run_lock_checkouts.get(user_id, 0)
        if count > 1:
            _user_run_lock_checkouts[user_id] = count - 1
        else:
            _user_run_lock_checkouts.pop(user_id, None)


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
    run_uid = username if (_flags.multi_tenant_enabled() and username) else None

    if run_uid is not None:
        # Flag ON: per-user lock with checkout refcount to close the pre-acquire
        # TOCTOU window.  _release_run_lock must be called on ALL exit paths.
        run_lock = _run_lock_for(run_uid)  # checkout++ (atomic, under dict lock)
        acquired = run_lock.acquire(blocking=False)
        if not acquired:
            _release_run_lock(run_uid)  # checkout-- on 409 path
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 실행 중",
            )
        try:
            results = backend.run_engine_once(user_id=run_uid)
            return RunOnceResponse(results=results or [])
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"엔진 실행 오류: {exc}",
            ) from exc
        finally:
            run_lock.release()
            _release_run_lock(run_uid)  # checkout-- on all post-acquire exit paths
    else:
        # FLAG-OFF: global _run_once_lock, byte-identical to pre-Phase-3 path.
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


_MULTITENANT_DISABLED_RESPONSE = {
    "status": "multitenant_disabled",
    "detail": "AUTOFOLIO_MULTI_TENANT_ENABLED is not enabled",
}


@router.get("/users/{user_id}/state", response_model=UserEngineStateResponse)
def user_engine_state(
    user_id: str,
    _session: Annotated[dict[str, Any], Depends(require_owner)],
) -> UserEngineStateResponse:
    """Read per-user engine state (auto_trading_enabled, consecutive_failures).

    Flag-gate: returns 409 when AUTOFOLIO_MULTI_TENANT_ENABLED is not set.
    """
    from app.services import backend
    from app.services import flags as _flags

    if not _flags.multi_tenant_enabled():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_MULTITENANT_DISABLED_RESPONSE,
        )
    repo, *_ = backend._ctx()
    auto_trading_enabled = (
        repo.get_engine_state("auto_trading_enabled", "false", user_id=user_id) == "true"
    )
    consecutive_failures = repo.get_consecutive_failures(user_id=user_id)
    return UserEngineStateResponse(
        user_id=user_id,
        auto_trading_enabled=auto_trading_enabled,
        consecutive_failures=consecutive_failures,
    )


@router.post("/users/{user_id}/reenable", response_model=UserReenableResponse)
def user_reenable(
    user_id: str,
    _session: Annotated[dict[str, Any], Depends(require_owner_csrf)],
) -> UserReenableResponse:
    """Re-enable a user's auto-trading and reset their circuit-breaker failures.

    Flag-gate: returns 409 when AUTOFOLIO_MULTI_TENANT_ENABLED is not set.
    Does NOT mutate any state (global or per-user) when the flag is OFF.
    """
    from app.services import backend
    from app.services import flags as _flags

    if not _flags.multi_tenant_enabled():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_MULTITENANT_DISABLED_RESPONSE,
        )
    repo, *_ = backend._ctx()
    repo.set_engine_state("auto_trading_enabled", "true", user_id=user_id)
    repo.reset_consecutive_failures(user_id=user_id)
    auto_trading_enabled = (
        repo.get_engine_state("auto_trading_enabled", "false", user_id=user_id) == "true"
    )
    consecutive_failures = repo.get_consecutive_failures(user_id=user_id)
    return UserReenableResponse(
        user_id=user_id,
        auto_trading_enabled=auto_trading_enabled,
        consecutive_failures=consecutive_failures,
        status="reenabled",
    )
