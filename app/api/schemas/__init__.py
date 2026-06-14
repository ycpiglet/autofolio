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
