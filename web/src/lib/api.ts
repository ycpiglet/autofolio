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
      "Content-Type": "application/json",
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
const CSRF_EXEMPT_PATHS = new Set(["/api/auth/login", "/api/auth/logout"]);

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

// ── Account (local account management) ──────────────────────────────────────

/** Read-only account profile — never contains a secret. */
export interface AccountResponse {
  username: string | null;
  role: string;
  data_source: string;
  is_owner: boolean;
}

/** GET /api/account — current account profile (no secrets) */
export function getAccount(): Promise<AccountResponse> {
  return apiGet<AccountResponse>("/api/account");
}

/**
 * POST /api/account/password — change the SESSION's own password.
 * The server derives the username from the session, never the body.
 * Throws ApiError(401) on wrong current password, ApiError(400) on a
 * weak/invalid new password, ApiError(403) for guests.
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
  description?: string;
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

/** GET /api/agents/research?symbol=&days= — READ-ONLY per-symbol briefing */
export function apiAgentResearch(
  symbol: string,
  days = 7,
): Promise<AgentResearchResponse> {
  const q = new URLSearchParams({ symbol, days: String(days) });
  return apiGet<AgentResearchResponse>(`/api/agents/research?${q}`);
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
