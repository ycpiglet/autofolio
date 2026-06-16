"""Pydantic request / response schemas for Autofolio API."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


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


class SsoProviderInfo(BaseModel):
    id: str
    label: str
    kind: str
    enabled: bool


class SsoProvidersResponse(BaseModel):
    providers: list[SsoProviderInfo]


# ── Account ────────────────────────────────────────────────────────────────────

class AccountResponse(BaseModel):
    """Read-only account profile. NEVER contains password/hash/salt/secret."""

    username: str | None = None
    role: str
    data_source: str
    is_owner: bool


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


class PasswordChangeResponse(BaseModel):
    status: str        # "changed"
    message: str


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
    side: Literal["BUY", "SELL"]
    target_price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=1)
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


# ── Agents (Phase 4) ─────────────────────────────────────────────────────────

class AgentInfo(BaseModel):
    name: str
    role: str | None = None
    category: str | None = None
    description: str | None = None
    expert: bool = False


class AgentsListResponse(BaseModel):
    available: bool
    message: str
    agents: list[AgentInfo]


class AskRequest(BaseModel):
    agent: str
    question: str
    context: str = ""


class AskResponse(BaseModel):
    answer: str


class IcRunRequest(BaseModel):
    topic: str
    panel: list[str] | None = None


class IcRunResponse(BaseModel):
    job_id: str


# ── Per-symbol expert briefing (READ-ONLY research) ──────────────────────────

class ResearchProposal(BaseModel):
    """Rule-based price-condition proposal. SUGGESTION ONLY — never persisted here."""

    symbol: str
    side: str
    target_price: float
    quantity: int
    order_type: str
    allow_market_fallback: bool
    rationale: str
    risk_note: str


class DisclosureGateInfo(BaseModel):
    symbol: str
    blocked: bool
    reason: str


class AgentResearchResponse(BaseModel):
    """종목 전문가 브리핑 — assembled from real read-only backend functions.

    NOTE: contains NO live-news data (no news API exists) and is produced only
    on manual trigger (no daemon/auto-scheduler). The proposal is a suggestion;
    it is NOT saved as a trade condition by this endpoint.
    """

    symbol: str
    name: str
    price: float
    fundamental: dict[str, Any]
    disclosures: TableResponse
    disclosure_gate: DisclosureGateInfo
    proposal: ResearchProposal


class PremarketSummaryResponse(BaseModel):
    date: str
    created_at: str
    file: str
    market_open_reference: str
    content: str
    highlights: list[str]
    agents: list[AgentInfo]
