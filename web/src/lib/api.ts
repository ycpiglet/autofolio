/**
 * api.ts — typed fetch wrapper for Autofolio Next.js frontend
 *
 * All requests hit same-origin `/api/...` which is transparently
 * rewritten to http://127.0.0.1:8000/api/... via next.config.ts rewrites.
 *
 * Design principles:
 * - credentials: "include" so session cookies are sent automatically
 * - Non-2xx responses throw ApiError — no silent fallbacks
 * - All state-changing requests must include the CSRF header
 */

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
 * HTTP POST with JSON body.
 * Includes X-Requested-With header as CSRF guard for state-changing endpoints.
 */
export function apiPost<T>(path: string, data?: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    body: data !== undefined ? JSON.stringify(data) : undefined,
    headers: { "X-Requested-With": "XMLHttpRequest" },
  });
}

/** Convenience: fetch a TableResponse endpoint */
export function apiTable<TRow extends Record<string, unknown>>(
  path: string,
): Promise<TableResponse<TRow>> {
  return apiGet<TableResponse<TRow>>(path);
}
