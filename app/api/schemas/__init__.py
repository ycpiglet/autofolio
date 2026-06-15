"""Pydantic request / response schemas for Autofolio API."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str | None = None
    password: str | None = None
    guest: bool = False


class SessionResponse(BaseModel):
    role: str
    username: str | None = None
    data_source: str
    csrf_token: str | None = None  # only present when authenticated


# ── Shared ────────────────────────────────────────────────────────────────────

class TableResponse(BaseModel):
    columns: list[str]
    rows: list[dict[str, Any]]


# ── Engine ────────────────────────────────────────────────────────────────────

class CircuitBreakerInfo(BaseModel):
    triggered: bool
    threshold_pct: float
    consecutive_failures: int
    today_pnl: float


class EngineStatusResponse(BaseModel):
    env: str
    auto_trading_enabled: bool
    kill_switch_active: bool
    circuit_breaker: CircuitBreakerInfo


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str


# ── Engine state-changing (Phase 3) ──────────────────────────────────────────

class KillSwitchRequest(BaseModel):
    active: bool


class KillSwitchResponse(BaseModel):
    kill_switch_active: bool


class AutoTradingRequest(BaseModel):
    enabled: bool


class AutoTradingResponse(BaseModel):
    auto_trading_enabled: bool


class RunOnceResponse(BaseModel):
    results: list[str]


# ── Trade conditions POST (Phase 3) ──────────────────────────────────────────

class ConditionRequest(BaseModel):
    symbol: str
    side: str          # "BUY" or "SELL"
    target_price: float
    quantity: int
    auto: bool = False
    ack_token: str | None = None   # present only on re-submit after needs_acknowledgement


class ConditionSavedResponse(BaseModel):
    status: str        # "saved"
    message: str
    condition_id: int | None = None


class ConditionAckResponse(BaseModel):
    status: str        # "needs_acknowledgement"
    verdict: str
    ack_token: str


class ConditionBlockedResponse(BaseModel):
    status: str        # "blocked_disclosure" or "rejected"
    message: str


# ── Settings (Phase 3) ───────────────────────────────────────────────────────

class RiskLimitsRequest(BaseModel):
    max_order_amount: float | None = None
    max_daily_amount: float | None = None


class RiskLimitsResponse(BaseModel):
    status: str        # "saved"
