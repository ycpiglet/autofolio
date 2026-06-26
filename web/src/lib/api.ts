/**
 * api.ts — typed fetch wrapper for Autofolio Next.js frontend
 *
 * All requests hit same-origin `/api/...` which is transparently
 * rewritten to http://127.0.0.1:8000/api/... via next.config.ts rewrites.
 *
 * Design principles:
 * - credentials: "include" so session cookies are sent automatically
 * - Non-2xx responses throw ApiError — no silent fallbacks
 * - All state-changing requests (POST/PUT) include X-CSRF-Token header
 *   fetched from /api/auth/me (see csrf.ts)
 * - 409 Conflict is thrown as ApiError with status=409; callers can inspect
 *   body to distinguish run-once-busy from needs_acknowledgement
 */

import { getCsrfToken } from "./csrf";

// ── Types ──────────────────────────────────────────────────────────────────

/** Generic tabular response from FastAPI df_records() serializer */
export interface TableResponse<
  TRow extends Record<string, unknown> = Record<string, unknown>,
> {
  columns: string[];
  rows: TRow[];
  /** True when the server returned a synthetic demo curve (non-prod + sparse history). */
  is_demo?: boolean;
}

/** Structured API error */
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly body: unknown,
    message?: string,
  ) {
    super(message ?? `API error ${status}`);
    this.name = "ApiError";
  }
}

// ── Domain types ──────────────────────────────────────────────────────────

export interface ConditionPayload {
  symbol: string;
  side: "BUY" | "SELL";
  target_price: number;
  quantity: number;
  ack_token?: string;
  actor_type?: "USER" | "AGENT" | "SCHEDULER";
  source_surface?: string;
  trigger_reason?: string;
  live_ack_id?: number;
}

export interface ConditionResponse {
  id: number;
  symbol: string;
  side: string;
  target_price: number;
  quantity: number;
  status: string;
  created_at: string;
}

/** Returned by POST /api/trade/conditions with status 409 */
export interface NeedsAckResponse {
  detail: string;
  verdict: string;
  ack_token: string;
}

export interface RiskLimitsPayload {
  max_position_pct?: number;
  max_daily_loss_pct?: number;
  max_drawdown_pct?: number;
  [key: string]: number | undefined;
}

export interface InvestorProfileResponse {
  username: string;
  survey_version: string;
  completed: boolean;
  risk_type: string;
  knowledge_level: string;
  scores: Record<string, number>;
  recommended_max_equity_pct: number;
  recommended_autonomy_level: string;
  needs_advanced_survey: boolean;
  satisfaction_focus: string[];
  last_checkin_at: string | null;
  satisfaction_score: number | null;
  confidence_score: number | null;
  stress_score: number | null;
  updated_at: string | null;
  completed_at: string | null;
}

export interface SurveyOption {
  value: string;
  label: string;
  exclusive?: boolean;
}

export interface SurveyQuestion {
  id: string;
  title: string;
  kind: "single" | "multi" | "acknowledgement" | "signature";
  required: boolean;
  category: string;
  description?: string | null;
  options: SurveyOption[];
}

export interface SurveyCategory {
  key: string;
  title: string;
  description: string;
}

export interface SurveyDefinitionResponse {
  version: string;
  categories: SurveyCategory[];
  questions: SurveyQuestion[];
}

export interface SurveySubmitResponse {
  status: string;
  profile: InvestorProfileResponse;
}

export interface ProfileCheckinPayload {
  trigger_type: "monthly" | "drawdown" | "rebalance" | "override" | "manual";
  satisfaction_score: number;
  confidence_score: number;
  stress_score: number;
  automation_adjustment: "lower" | "same" | "raise";
  notes?: string;
}

export interface ProfileCheckinResponse {
  status: string;
  id: number;
  profile: InvestorProfileResponse;
}

export interface EngineHealthResponse {
  status: "ok" | "watch" | string;
  active_conditions: number;
  processing_conditions: number;
  stale_processing_conditions: number;
  duplicate_intent_keys: number;
  open_intents_over_5m: number;
  latest_run: Record<string, unknown> | null;
}

export interface ManualSummary {
  slug: string;
  title: string;
  description: string;
  audience: string;
  visibility: string;
  ui_section: string;
  risk_level: string;
  requires_ack: boolean;
  ack_kind: string | null;
  version: string;
  order: number;
}

export interface ManualDetail extends ManualSummary {
  content: string;
  metadata: Record<string, unknown>;
}

export interface ManualsListResponse {
  manuals: ManualSummary[];
}

export interface AcknowledgementStatusResponse {
  username: string;
  live_trading_acknowledged: boolean;
  live_trading_acknowledged_at: string | null;
  latest_live_trading_ack_id: number | null;
  totp_recommended: boolean;
  totp_enabled: boolean;
  message: string;
}

export interface AcknowledgementResponse {
  id: number;
  status: string;
  method: string;
  created_at: string;
}

export type IntegrationKind = "llm" | "sns" | "broker" | "other";

export interface IntegrationProviderInfo {
  id: string;
  label: string;
  kind: IntegrationKind;
  auth_type: string;
  secret_label: string;
  account_label_hint: string;
  description: string;
}

export interface IntegrationCredentialResponse {
  provider_id: string;
  label: string;
  kind: IntegrationKind;
  auth_type: string;
  configured: boolean;
  enabled: boolean;
  account_label: string | null;
  scopes: string[];
  secret_set: boolean;
  secret_hint: string | null;
  created_at: string | null;
  updated_at: string | null;
  last_checked_at: string | null;
  status: "not_configured" | "configured" | "disabled";
  message: string;
}

export interface IntegrationSettingsResponse {
  providers: IntegrationProviderInfo[];
  integrations: IntegrationCredentialResponse[];
}

export interface IntegrationCredentialPayload {
  secret_value?: string;
  account_label?: string;
  scopes?: string[];
  enabled?: boolean;
  note?: string;
}

export interface PortfolioHoldingRow extends Record<string, unknown> {
  종목: string;
  티커: string;
  자산군: string;
  지역: string;
  섹터?: string;
  전략?: string;
  그룹?: string;
  수량: number;
  평단: number;
  현재가: number;
  평가금액: number;
  평가손익: number;
  손익률: number;
  비중: number;
  예상연배당?: number;
  배당수익률?: number;
  위험버킷?: string;
  data_quality?: Record<string, unknown>;
}

export interface PortfolioGroup {
  group_id: string;
  name: string;
  description: string;
  color: string;
  sort_order: number;
  symbols: string[];
  members?: Record<string, unknown>[];
  summary?: Record<string, unknown>;
  rows?: PortfolioHoldingRow[];
}

export interface PortfolioGroupPayload {
  name: string;
  symbols: string[];
  description?: string;
  color?: string;
  sort_order?: number;
}

export interface PortfolioOverviewResponse {
  kpis: Record<string, number | string | null>;
  holdings: TableResponse<PortfolioHoldingRow>;
  groups: {
    automatic: Array<{ id: string; title: string; rows: Record<string, unknown>[] }>;
    manual: PortfolioGroup[];
    saved: PortfolioGroup[];
  };
  diagnostics: Array<Record<string, unknown>>;
  top_movers: Record<string, PortfolioHoldingRow[]>;
  concentration: Record<string, number>;
  allocation_gap: TableResponse;
  data_quality: Record<string, unknown>;
}

// ── Internal helpers ───────────────────────────────────────────────────────

async function parseResponse(res: Response): Promise<unknown> {
  const contentType = res.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return res.json();
  }
  return res.text();
}

async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const url = path.startsWith("/") ? path : `/${path}`;

  const res = await fetch(url, {
    ...init,
    credentials: "include",
    headers: {
      // Only declare a JSON body type when a body is actually sent; bodyless
      // GET/DELETE requests should not carry Content-Type.
      ...(init.body != null ? { "Content-Type": "application/json" } : {}),
      ...init.headers,
    },
  });

  const body = await parseResponse(res);

  if (!res.ok) {
    throw new ApiError(res.status, body, `${res.status} ${res.statusText}`);
  }

  return body as T;
}

// ── Public API ─────────────────────────────────────────────────────────────

/** HTTP GET — throws ApiError on non-2xx */
export function apiGet<T>(path: string): Promise<T> {
  return request<T>(path, { method: "GET" });
}

/**
 * Paths that establish or destroy the session — the server does not require
 * CSRF protection on these because no session exists yet (login) or is being
 * torn down (logout).  Fetching a CSRF token here would cause a chicken-and-egg
 * failure: /api/auth/me returns 401 before login, so getCsrfToken() would throw
 * and the login POST would never fire.
 */
const CSRF_EXEMPT_PATHS = new Set([
  "/api/auth/login",
  "/api/auth/logout",
  "/api/membership/requests",
  "/api/membership/requests/status",
]);

/**
 * HTTP POST with JSON body.
 * Fetches (cached) CSRF token from /api/auth/me and attaches it as
 * X-CSRF-Token — except for auth entry-points (login/logout) which are
 * CSRF-exempt on the server and must work before a session exists.
 */
export async function apiPost<T>(path: string, data?: unknown): Promise<T> {
  const extraHeaders: Record<string, string> = {
    "X-Requested-With": "XMLHttpRequest",
  };
  if (!CSRF_EXEMPT_PATHS.has(path)) {
    extraHeaders["X-CSRF-Token"] = await getCsrfToken();
  }
  return request<T>(path, {
    method: "POST",
    body: data !== undefined ? JSON.stringify(data) : undefined,
    headers: extraHeaders,
  });
}

/**
 * HTTP PUT with JSON body.
 * Fetches (cached) CSRF token from /api/auth/me and sends it as X-CSRF-Token.
 */
export async function apiPut<T>(path: string, data?: unknown): Promise<T> {
  const csrfToken = await getCsrfToken();
  return request<T>(path, {
    method: "PUT",
    body: data !== undefined ? JSON.stringify(data) : undefined,
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRF-Token": csrfToken,
    },
  });
}

/**
 * HTTP DELETE.
 * Fetches (cached) CSRF token from /api/auth/me and sends it as X-CSRF-Token.
 */
export async function apiDelete<T>(path: string): Promise<T> {
  const csrfToken = await getCsrfToken();
  return request<T>(path, {
    method: "DELETE",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRF-Token": csrfToken,
    },
  });
}

/** Convenience: fetch a TableResponse endpoint */
export function apiTable<TRow extends Record<string, unknown>>(
  path: string,
): Promise<TableResponse<TRow>> {
  return apiGet<TableResponse<TRow>>(path);
}

// ── Typed endpoint helpers ─────────────────────────────────────────────────

/** POST /api/engine/kill-switch — activates kill switch */
export function postKillSwitch(active: boolean): Promise<unknown> {
  return apiPost("/api/engine/kill-switch", { active });
}

/** POST /api/engine/auto-trading — enables or disables auto trading */
export function postAutoTrading(enabled: boolean): Promise<unknown> {
  return apiPost("/api/engine/auto-trading", { enabled });
}

/**
 * POST /api/engine/run-once — triggers one engine cycle.
 * Throws ApiError(409) if engine is already running.
 */
export function postRunOnce(): Promise<unknown> {
  return apiPost("/api/engine/run-once");
}

/** GET /api/engine/health — scheduler/queue/order-intent diagnostics */
export function getEngineHealth(): Promise<EngineHealthResponse> {
  return apiGet<EngineHealthResponse>("/api/engine/health");
}

/** GET /api/portfolio/overview — portfolio diagnosis dashboard payload */
export function getPortfolioOverview(): Promise<PortfolioOverviewResponse> {
  return apiGet<PortfolioOverviewResponse>("/api/portfolio/overview");
}

/** POST /api/portfolio/groups — create manual portfolio group */
export function postPortfolioGroup(payload: PortfolioGroupPayload): Promise<PortfolioGroup> {
  return apiPost<PortfolioGroup>("/api/portfolio/groups", payload);
}

/** PUT /api/portfolio/groups/{id} — update manual portfolio group */
export function putPortfolioGroup(
  groupId: string,
  payload: PortfolioGroupPayload,
): Promise<PortfolioGroup> {
  return apiPut<PortfolioGroup>(`/api/portfolio/groups/${encodeURIComponent(groupId)}`, payload);
}

/** DELETE /api/portfolio/groups/{id} */
export function deletePortfolioGroup(groupId: string): Promise<{ status: string }> {
  return apiDelete<{ status: string }>(`/api/portfolio/groups/${encodeURIComponent(groupId)}`);
}

/**
 * POST /api/trade/conditions — create a trade condition.
 * Possible throws:
 *   ApiError(409) — needs_acknowledgement; body is NeedsAckResponse
 *   ApiError(422) — disclosure-block or rejected
 *   ApiError(500) — server error
 */
export function postCondition(payload: ConditionPayload): Promise<ConditionResponse> {
  return apiPost<ConditionResponse>("/api/trade/conditions", payload);
}

/** PUT /api/settings/risk-limits — update risk limit settings */
export function putRiskLimits(payload: RiskLimitsPayload): Promise<unknown> {
  return apiPut("/api/settings/risk-limits", payload);
}

/** GET /api/profile/investor — current investor profile/personalization state */
export function getInvestorProfile(): Promise<InvestorProfileResponse> {
  return apiGet<InvestorProfileResponse>("/api/profile/investor");
}

/** GET /api/profile/survey — active onboarding survey definition */
export function getInvestorSurvey(): Promise<SurveyDefinitionResponse> {
  return apiGet<SurveyDefinitionResponse>("/api/profile/survey");
}

/** POST /api/profile/survey — save survey answers and derive profile */
export function postInvestorSurvey(
  answers: Record<string, unknown>,
): Promise<SurveySubmitResponse> {
  return apiPost<SurveySubmitResponse>("/api/profile/survey", { answers });
}

/** POST /api/profile/checkin — monthly/event satisfaction feedback */
export function postProfileCheckin(
  payload: ProfileCheckinPayload,
): Promise<ProfileCheckinResponse> {
  return apiPost<ProfileCheckinResponse>("/api/profile/checkin", payload);
}

/** GET /api/manuals — manuals visible to current session */
export function getManuals(): Promise<ManualsListResponse> {
  return apiGet<ManualsListResponse>("/api/manuals");
}

/** GET /api/manuals/{slug} */
export function getManual(slug: string): Promise<ManualDetail> {
  return apiGet<ManualDetail>(`/api/manuals/${encodeURIComponent(slug)}`);
}

/** GET /api/acknowledgements/status */
export function getAcknowledgementStatus(): Promise<AcknowledgementStatusResponse> {
  return apiGet<AcknowledgementStatusResponse>("/api/acknowledgements/status");
}

/** POST /api/acknowledgements — record risk/manual acknowledgement */
export function postAcknowledgement(payload: {
  kind: string;
  document_slug: string;
  document_version: string;
  acknowledgement_text: string;
  current_password?: string;
}): Promise<AcknowledgementResponse> {
  return apiPost<AcknowledgementResponse>("/api/acknowledgements", payload);
}

/** GET /api/integrations — current user's redacted integration status. */
export function getIntegrations(): Promise<IntegrationSettingsResponse> {
  return apiGet<IntegrationSettingsResponse>("/api/integrations");
}

/** PUT /api/integrations/{provider_id} — write-only token/settings upsert. */
export function putIntegrationCredential(
  providerId: string,
  payload: IntegrationCredentialPayload,
): Promise<IntegrationCredentialResponse> {
  return apiPut<IntegrationCredentialResponse>(
    `/api/integrations/${encodeURIComponent(providerId)}`,
    payload,
  );
}

/** DELETE /api/integrations/{provider_id} — remove current user's provider token. */
export function deleteIntegrationCredential(
  providerId: string,
): Promise<{ status: string; integration: IntegrationCredentialResponse }> {
  return apiDelete<{ status: string; integration: IntegrationCredentialResponse }>(
    `/api/integrations/${encodeURIComponent(providerId)}`,
  );
}

// ── Account (local account management) ──────────────────────────────────────

/** Read-only account profile — never contains a secret. */
export interface AccountResponse {
  username: string | null;
  role: string;
  data_source: string;
  is_owner: boolean;
}

// ── Membership approval ────────────────────────────────────────────────────

export type MembershipStatus =
  | "requested"
  | "verification_pending"
  | "deposit_pending"
  | "active"
  | "rejected"
  | "expired";

export interface DepositInstructionResponse {
  price_krw: number;
  currency: string;
  deposit_code: string;
  bank_name: string | null;
  account_holder: string | null;
  account_number: string | null;
  account_configured: boolean;
  due_at: string | null;
}

export interface ApprovalEventResponse {
  actor: string;
  action: string;
  previous_status: string | null;
  next_status: string;
  evidence_type: string | null;
  note: string | null;
  created_at: string;
}

export interface MembershipAccountGrantResponse {
  username: string;
  role: string;
  created_at: string;
  password_set: boolean;
}

export interface SubscriptionGrantResponse {
  plan: string;
  starts_at: string;
  ends_at: string | null;
  source_event: string;
}

export interface MembershipRequestResponse {
  request_id: string;
  status: MembershipStatus;
  display_name: string;
  contact: string;
  plan: string;
  price_krw: number;
  requested_at: string;
  updated_at: string;
  verified_at: string | null;
  activated_at: string | null;
  grant_expires_at: string | null;
  deposit_instruction: DepositInstructionResponse | null;
  account_grant: MembershipAccountGrantResponse | null;
  subscription_grant: SubscriptionGrantResponse | null;
  events: ApprovalEventResponse[];
  message: string;
}

export interface MembershipRequestListResponse {
  requests: MembershipRequestResponse[];
}

export interface MembershipRequestPayload {
  display_name: string;
  contact: string;
  plan?: string;
  referral_source?: string;
  note?: string;
}

export interface MembershipRequestStatusLookupPayload {
  request_id: string;
  contact: string;
}

export interface MembershipTransitionPayload {
  status: MembershipStatus;
  evidence_type?: string;
  note?: string;
  grant_days?: number;
  login_username?: string;
  initial_password?: string;
}

export interface MembershipDepositRecognitionPayload {
  source_text: string;
  min_confidence?: number;
}

export interface MembershipDepositMatchResponse {
  request_id: string;
  display_name: string;
  contact: string;
  status: MembershipStatus;
  deposit_code: string;
  expected_amount_krw: number;
  matched_amount_krw: number | null;
  confidence: number;
  reasons: string[];
  matched_text_excerpt: string;
  suggested_evidence_type: string;
}

export interface MembershipDepositRecognitionResponse {
  matches: MembershipDepositMatchResponse[];
  scanned_lines: number;
  candidate_requests: number;
  min_confidence: number;
}

export interface MembershipReadinessItem {
  id: string;
  label: string;
  state: "pass" | "watch" | "block";
  detail: string;
  evidence: string;
  gate: string;
}

export interface MembershipReadinessResponse {
  can_launch: boolean;
  mode: string;
  score: number;
  summary: string;
  items: MembershipReadinessItem[];
  required_owner_actions: string[];
  environment_flags: Record<string, boolean>;
}

/** POST /api/membership/requests — public request intake; does not create a session. */
export function postMembershipRequest(
  payload: MembershipRequestPayload,
): Promise<MembershipRequestResponse> {
  return apiPost<MembershipRequestResponse>("/api/membership/requests", payload);
}

/** POST /api/membership/requests/status — public applicant status lookup. */
export function postMembershipRequestStatus(
  payload: MembershipRequestStatusLookupPayload,
): Promise<MembershipRequestResponse> {
  return apiPost<MembershipRequestResponse>("/api/membership/requests/status", payload);
}

/** GET /api/membership/requests — Owner review queue. */
export function getMembershipRequests(
  status?: MembershipStatus,
): Promise<MembershipRequestListResponse> {
  const suffix = status ? `?status=${encodeURIComponent(status)}` : "";
  return apiGet<MembershipRequestListResponse>(`/api/membership/requests${suffix}`);
}

/** POST /api/membership/requests/{id}/transition — Owner approval action. */
export function postMembershipTransition(
  requestId: string,
  payload: MembershipTransitionPayload,
): Promise<MembershipRequestResponse> {
  return apiPost<MembershipRequestResponse>(
    `/api/membership/requests/${encodeURIComponent(requestId)}/transition`,
    payload,
  );
}

/** POST /api/membership/deposits/recognize — Owner-only pasted statement matcher. */
export function postMembershipDepositRecognition(
  payload: MembershipDepositRecognitionPayload,
): Promise<MembershipDepositRecognitionResponse> {
  return apiPost<MembershipDepositRecognitionResponse>(
    "/api/membership/deposits/recognize",
    payload,
  );
}

/** GET /api/membership/readiness — Owner-only production readiness checklist. */
export function getMembershipReadiness(): Promise<MembershipReadinessResponse> {
  return apiGet<MembershipReadinessResponse>("/api/membership/readiness");
}

// ── SSO / SNS login ────────────────────────────────────────────────────────

export interface SsoProviderInfo {
  id: string;
  label: string;
  kind: "oidc" | "sns" | string;
  enabled: boolean;
}

export interface SsoProvidersResponse {
  providers: SsoProviderInfo[];
}

/** GET /api/auth/sso/providers — public provider availability, no secrets */
export function getSsoProviders(): Promise<SsoProvidersResponse> {
  return apiGet<SsoProvidersResponse>("/api/auth/sso/providers");
}

/** GET /api/account — current account profile (no secrets) */
export function getAccount(): Promise<AccountResponse> {
  return apiGet<AccountResponse>("/api/account");
}

/**
 * POST /api/account/password — change the SESSION's own password.
 * The server derives the username from the session, never the body.
 * Throws ApiError(401) on wrong current password, ApiError(400) on a
 * weak/invalid new password, ApiError(403) for unapproved sessions.
 */
export function postPasswordChange(
  oldPassword: string,
  newPassword: string,
): Promise<{ status: string; message: string }> {
  return apiPost("/api/account/password", {
    old_password: oldPassword,
    new_password: newPassword,
  });
}

/** POST /api/auth/logout — clear the session cookie (CSRF-exempt). */
export function postLogout(): Promise<{ status: string }> {
  return apiPost("/api/auth/logout");
}

// ── Agent domain types ────────────────────────────────────────────────────

export interface AgentInfo {
  name: string;
  role?: string;
  category?: string;
  description?: string;
  expert?: boolean;
}

export interface AgentsListResponse {
  available: boolean;
  message?: string;
  agents: AgentInfo[];
}

export interface AgentAskResponse {
  answer: string;
}

export interface IcRunResponse {
  job_id: string;
}

export interface IcDecision {
  id?: number;
  topic: string;
  decision?: string;
  summary?: string;
  created_at?: string;
  [key: string]: unknown;
}

// ── Agent typed helpers ───────────────────────────────────────────────────

/** GET /api/agents/list */
export function apiAgentsList(): Promise<AgentsListResponse> {
  return apiGet<AgentsListResponse>("/api/agents/list");
}

/** POST /api/agents/ask */
export function apiAgentAsk(
  agent: string,
  question: string,
  context?: string,
): Promise<AgentAskResponse> {
  return apiPost<AgentAskResponse>("/api/agents/ask", {
    agent,
    question,
    ...(context ? { context } : {}),
  });
}

/** POST /api/agents/ic/run */
export function apiIcRun(
  topic: string,
  panel?: string[],
): Promise<IcRunResponse> {
  return apiPost<IcRunResponse>("/api/agents/ic/run", {
    topic,
    ...(panel ? { panel } : {}),
  });
}

/** GET /api/agents/ic/decisions?limit= */
export function apiIcDecisions(limit = 10): Promise<IcDecision[]> {
  return apiGet<IcDecision[]>(`/api/agents/ic/decisions?limit=${limit}`);
}

// ── Per-symbol research briefing ──────────────────────────────────────────

export interface ResearchProposal {
  symbol: string;
  side: string;
  target_price: number;
  quantity: number;
  order_type: string;
  allow_market_fallback: boolean;
  rationale: string;
  risk_note: string;
}

export interface DisclosureGateInfo {
  symbol: string;
  blocked: boolean;
  reason: string;
}

export interface AgentResearchResponse {
  symbol: string;
  name: string;
  price: number;
  fundamental: Record<string, unknown>;
  disclosures: TableResponse;
  disclosure_gate: DisclosureGateInfo;
  proposal: ResearchProposal;
}

export interface PremarketSummaryResponse {
  date: string;
  created_at: string;
  file: string;
  market_open_reference: string;
  content: string;
  highlights: string[];
  agents: AgentInfo[];
}

/** GET /api/agents/research?symbol=&days= — READ-ONLY per-symbol briefing */
export function apiAgentResearch(
  symbol: string,
  days = 7,
): Promise<AgentResearchResponse> {
  const q = new URLSearchParams({ symbol, days: String(days) });
  return apiGet<AgentResearchResponse>(`/api/agents/research?${q}`);
}

/** GET /api/agents/premarket/summary — latest or date-specific saved markdown */
export function apiPremarketSummary(date?: string): Promise<PremarketSummaryResponse> {
  const suffix = date ? `?${new URLSearchParams({ date })}` : "";
  return apiGet<PremarketSummaryResponse>(`/api/agents/premarket/summary${suffix}`);
}

// ── Analysis domain types ─────────────────────────────────────────────────

export interface BacktestResult {
  symbol: string;
  strategy: string;
  start: string;
  end: string;
  total_return_pct: number;
  trade_count: number;
  win_rate_pct: number;
  max_drawdown_pct: number;
}

export interface SimulationResult {
  total_value: number;
  n_simulations: number;
  horizon_days: number;
  var_95: number;
  var_99: number;
  cvar_95: number;
  max_drawdown_pct: number;
  note?: string;
}

// ── Analysis typed helpers ────────────────────────────────────────────────

/** GET /api/market/intraday?symbol=&time_unit=&count= → TableResponse OHLC */
export function apiIntraday(
  symbol: string,
  time_unit = 1,
  count = 80,
): Promise<TableResponse> {
  const q = new URLSearchParams({
    symbol,
    time_unit: String(time_unit),
    count: String(count),
  });
  return apiGet<TableResponse>(`/api/market/intraday?${q}`);
}

/** GET /api/analysis/backtest?symbol=&start=&end=&fast=&slow= */
export function apiBacktest(params: {
  symbol: string;
  start: string;
  end: string;
  fast: number;
  slow: number;
}): Promise<BacktestResult> {
  const q = new URLSearchParams({
    symbol: params.symbol,
    start: params.start,
    end: params.end,
    fast: String(params.fast),
    slow: String(params.slow),
  });
  return apiGet<BacktestResult>(`/api/analysis/backtest?${q}`);
}

/** GET /api/analysis/var?horizon_days=&n_simulations= */
export function apiVar(params: {
  horizon_days: number;
  n_simulations: number;
}): Promise<SimulationResult> {
  const q = new URLSearchParams({
    horizon_days: String(params.horizon_days),
    n_simulations: String(params.n_simulations),
  });
  return apiGet<SimulationResult>(`/api/analysis/var?${q}`);
}

/** GET /api/analysis/scenario → TableResponse */
export function apiScenario(): Promise<TableResponse> {
  return apiGet<TableResponse>("/api/analysis/scenario");
}

/** GET /api/analysis/whatif?symbol=&weight= → dict */
export function apiWhatif(symbol: string, weight: number): Promise<Record<string, unknown>> {
  const q = new URLSearchParams({ symbol, weight: String(weight) });
  return apiGet<Record<string, unknown>>(`/api/analysis/whatif?${q}`);
}

/** GET /api/analysis/attribution → TableResponse */
export function apiAttribution(): Promise<TableResponse> {
  return apiGet<TableResponse>("/api/analysis/attribution");
}

// ── Finance Roadmap domain types (TASK-173/174) ───────────────────────────

export interface FinanceRoadmapGapRange {
  low_pct_points: number;
  high_pct_points: number;
}

export interface FinanceRoadmapPlanned {
  planned_return_pct: number;
  planning_horizon: string;
}

export interface FinanceRoadmapExpected {
  low_pct: number;
  high_pct: number;
  confidence: string;
  not_guaranteed: boolean;
}

export interface FinanceRoadmapMissingEvidence {
  id: string;
  owner_decision_required: boolean;
}

export interface FinanceRoadmapReviewCandidate {
  id: string;
  candidate_for_owner_review_only: true;
  action_permitted_now: false;
  no_trade_instruction: true;
  why_flagged: string;
  missing_evidence: string[];
}

export interface FinanceRoadmapTimelineCandidate {
  id: string;
  candidate_for_owner_review_only: true;
  action_permitted_now: false;
  horizon: string;
  trigger: string;
  required_evidence: string[];
}

export interface FinanceRoadmapBoundary {
  synthetic_fixture_only: true;
  read_only_planning_input_only: true;
  not_investment_recommendation: true;
  no_trade_instruction: true;
  no_order_execution: true;
  not_tax_accounting_final_advice: true;
}

/**
 * Read-only finance roadmap planning preview.
 * Returned by GET /api/finance-roadmap/goal-gap.
 * as_of is always "fixture_static" (synthetic, never a date string).
 */
export interface FinanceRoadmapResponse {
  preview_mode: true;
  preview_label: string;
  /** Always "fixture_static" for synthetic fixture data — render as label, not date. */
  as_of: string;
  fixture_id: string;
  planned: FinanceRoadmapPlanned;
  expected: FinanceRoadmapExpected;
  gap: FinanceRoadmapGapRange;
  allocation_drift: string;
  data_quality_flags: FinanceRoadmapMissingEvidence[];
  review_candidates: FinanceRoadmapReviewCandidate[];
  timeline_candidates: FinanceRoadmapTimelineCandidate[];
  boundary: FinanceRoadmapBoundary;
}

/** GET /api/finance-roadmap/goal-gap — read-only planning preview */
export function getFinanceRoadmap(): Promise<FinanceRoadmapResponse> {
  return apiGet<FinanceRoadmapResponse>("/api/finance-roadmap/goal-gap");
}
