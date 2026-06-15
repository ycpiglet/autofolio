/**
 * csrf.ts — fetch and cache the CSRF token from /api/auth/me.
 *
 * The backend issues a csrf_token field in the /api/auth/me JSON response.
 * The session cookie is httpOnly so the token must come from the JSON body.
 * We cache it in a module-level variable; it is reset to null on 401 so that
 * a re-login automatically refreshes the token.
 */

interface MeResponse {
  role: string;
  username: string | null;
  data_source: string;
  csrf_token?: string;
}

let cached: string | null = null;

/** Fetch (or return cached) CSRF token. Returns empty string on failure. */
export async function getCsrfToken(): Promise<string> {
  if (cached !== null) return cached;
  try {
    const res = await fetch("/api/auth/me", {
      method: "GET",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) {
      return "";
    }
    const data: MeResponse = await res.json();
    cached = data.csrf_token ?? "";
    return cached;
  } catch {
    return "";
  }
}

/** Call after logout / 401 to force a fresh fetch next time. */
export function clearCsrfCache(): void {
  cached = null;
}
