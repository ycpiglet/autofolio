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


# ── Membership approval ──────────────────────────────────────────────────────

MembershipStatus = Literal[
    "requested",
    "verification_pending",
    "deposit_pending",
    "active",
    "rejected",
    "expired",
]


class MembershipRequestCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=80)
    contact: str = Field(min_length=3, max_length=160)
    plan: str = Field(default="pilot_monthly", max_length=80)
    referral_source: str | None = Field(default=None, max_length=120)
    note: str | None = Field(default=None, max_length=500)


class MembershipRequestStatusLookup(BaseModel):
    request_id: str = Field(min_length=1, max_length=80)
    contact: str = Field(min_length=3, max_length=160)


class DepositInstructionResponse(BaseModel):
    price_krw: int
    currency: str
    deposit_code: str
    bank_name: str | None = None
    account_holder: str | None = None
    account_number: str | None = None
    account_configured: bool
    due_at: str | None = None


class ApprovalEventResponse(BaseModel):
    actor: str
    action: str
    previous_status: str | None = None
    next_status: str
    evidence_type: str | None = None
    note: str | None = None
    created_at: str


class MembershipAccountGrantResponse(BaseModel):
    username: str
    role: str
    created_at: str
    password_set: bool


class SubscriptionGrantResponse(BaseModel):
    plan: str
    starts_at: str
    ends_at: str | None = None
    source_event: str


class MembershipRequestResponse(BaseModel):
    request_id: str
    status: MembershipStatus
    display_name: str
    contact: str
    plan: str
    price_krw: int
    requested_at: str
    updated_at: str
    verified_at: str | None = None
    activated_at: str | None = None
    grant_expires_at: str | None = None
    deposit_instruction: DepositInstructionResponse | None = None
    account_grant: MembershipAccountGrantResponse | None = None
    subscription_grant: SubscriptionGrantResponse | None = None
    events: list[ApprovalEventResponse] = []
    message: str


class MembershipRequestListResponse(BaseModel):
    requests: list[MembershipRequestResponse]


class MembershipTransitionRequest(BaseModel):
    status: MembershipStatus
    evidence_type: str | None = Field(default=None, max_length=80)
    note: str | None = Field(default=None, max_length=500)
    grant_days: int | None = Field(default=None, ge=1, le=366)
    login_username: str | None = Field(default=None, max_length=160)
    initial_password: str | None = Field(default=None, min_length=8, max_length=128)


class MembershipDepositRecognitionRequest(BaseModel):
    source_text: str = Field(min_length=1, max_length=20000)
    min_confidence: int = Field(default=50, ge=0, le=100)


class MembershipDepositMatchResponse(BaseModel):
    request_id: str
    display_name: str
    contact: str
    status: MembershipStatus
    deposit_code: str
    expected_amount_krw: int
    matched_amount_krw: int | None = None
    confidence: int
    reasons: list[str]
    matched_text_excerpt: str
    suggested_evidence_type: str


class MembershipDepositRecognitionResponse(BaseModel):
    matches: list[MembershipDepositMatchResponse]
    scanned_lines: int
    candidate_requests: int
    min_confidence: int


class MembershipReadinessItem(BaseModel):
    id: str
    label: str
    state: Literal["pass", "watch", "block"]
    detail: str
    evidence: str
    gate: str


class MembershipReadinessResponse(BaseModel):
    can_launch: bool
    mode: str
    score: int
    summary: str
    items: list[MembershipReadinessItem]
    required_owner_actions: list[str]
    environment_flags: dict[str, bool]


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


# ── Manuals and acknowledgements ─────────────────────────────────────────────

class ManualSummary(BaseModel):
    slug: str
    title: str
    description: str
    audience: str
    visibility: str
    ui_section: str
    risk_level: str
    requires_ack: bool
    ack_kind: str | None = None
    version: str
    order: int


class ManualsListResponse(BaseModel):
    manuals: list[ManualSummary]


class ManualDetail(ManualSummary):
    content: str
    metadata: dict[str, Any]


class AcknowledgementRequest(BaseModel):
    kind: str
    document_slug: str
    document_version: str
    acknowledgement_text: str
    current_password: str | None = None


class AcknowledgementResponse(BaseModel):
    id: int
    status: str
    method: str
    created_at: str


class AcknowledgementStatusResponse(BaseModel):
    username: str
    live_trading_acknowledged: bool
    live_trading_acknowledged_at: str | None = None
    latest_live_trading_ack_id: int | None = None
    totp_recommended: bool
    totp_enabled: bool
    message: str


# ── User-owned integrations ─────────────────────────────────────────────────

IntegrationKind = Literal["llm", "sns", "broker", "other"]


class IntegrationProviderInfo(BaseModel):
    id: str
    label: str
    kind: IntegrationKind
    auth_type: str
    secret_label: str
    account_label_hint: str
    description: str


class IntegrationCredentialResponse(BaseModel):
    provider_id: str
    label: str
    kind: IntegrationKind
    auth_type: str
    configured: bool
    enabled: bool
    account_label: str | None = None
    scopes: list[str] = []
    secret_set: bool
    secret_hint: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    last_checked_at: str | None = None
    status: Literal["not_configured", "configured", "disabled"]
    message: str


class IntegrationSettingsResponse(BaseModel):
    providers: list[IntegrationProviderInfo]
    integrations: list[IntegrationCredentialResponse]


class IntegrationCredentialUpsertRequest(BaseModel):
    secret_value: str | None = Field(default=None, max_length=4000)
    account_label: str | None = Field(default=None, max_length=160)
    scopes: list[str] = []
    enabled: bool = True
    note: str | None = Field(default=None, max_length=500)


class IntegrationDeleteResponse(BaseModel):
    status: str
    integration: IntegrationCredentialResponse


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


# ── Investor profile / survey ────────────────────────────────────────────────

class SurveyOption(BaseModel):
    value: str
    label: str
    exclusive: bool = False


class SurveyQuestion(BaseModel):
    id: str
    title: str
    kind: Literal["single", "multi", "acknowledgement", "signature"]
    required: bool = True
    category: str
    description: str | None = None
    options: list[SurveyOption]


class SurveyCategory(BaseModel):
    key: str
    title: str
    description: str


class SurveyDefinitionResponse(BaseModel):
    version: str
    categories: list[SurveyCategory]
    questions: list[SurveyQuestion]


class InvestorProfileResponse(BaseModel):
    username: str
    survey_version: str
    completed: bool
    risk_type: str
    knowledge_level: str
    scores: dict[str, float]
    recommended_max_equity_pct: int
    recommended_autonomy_level: str
    needs_advanced_survey: bool
    satisfaction_focus: list[str]
    last_checkin_at: str | None = None
    satisfaction_score: int | None = None
    confidence_score: int | None = None
    stress_score: int | None = None
    updated_at: str | None = None
    completed_at: str | None = None


class SurveySubmitRequest(BaseModel):
    answers: dict[str, Any]


class SurveySubmitResponse(BaseModel):
    status: str
    profile: InvestorProfileResponse


class OverrideAckRequest(BaseModel):
    action: str
    reason: str
    acknowledgement_text: str
    symbol: str | None = None


class OverrideAckResponse(BaseModel):
    id: int
    status: str


class ProfileCheckinRequest(BaseModel):
    trigger_type: Literal["monthly", "drawdown", "rebalance", "override", "manual"] = "manual"
    satisfaction_score: int = Field(..., ge=1, le=5)
    confidence_score: int = Field(..., ge=1, le=5)
    stress_score: int = Field(..., ge=1, le=5)
    automation_adjustment: Literal["lower", "same", "raise"] = "same"
    notes: str | None = None


class ProfileCheckinResponse(BaseModel):
    id: int
    status: str
    profile: InvestorProfileResponse


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
