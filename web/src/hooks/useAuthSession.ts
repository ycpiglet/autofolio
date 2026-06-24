"use client";

/**
 * useAuthSession — shared auth-state hook for all authenticated pages.
 *
 * All authenticated pages/components should gate their data queries on
 * `isAuthenticated` (or check `isPending`/`isAuthError`).
 * Using the shared query key ["auth-me"] means TanStack Query deduplicates
 * the /api/auth/me request across the component tree — one request regardless
 * of how many components call this hook in the same render cycle.
 */

import { useQuery } from "@tanstack/react-query";
import { apiGet, ApiError } from "@/lib/api";

interface SessionResponse {
  role: string;
  username: string | null;
  data_source: string;
}

export interface AuthSession {
  /** True once the session check completed successfully. */
  isAuthenticated: boolean;
  /** True while the initial /api/auth/me request is in-flight (including retries). */
  isPending: boolean;
  /** True when /api/auth/me returned 401 (or another error) after all retries. */
  isAuthError: boolean;
  /** The raw auth error, if any. */
  authError: Error | null;
  /** Session payload, available once authenticated. */
  session: SessionResponse | undefined;
  /** Manually retry the auth check (e.g. from an error recovery UI). */
  refetchAuth: () => void;
}

export function useAuthSession(): AuthSession {
  const {
    data: session,
    isPending,
    isError: isAuthError,
    error: authError,
    refetch,
  } = useQuery<SessionResponse>({
    queryKey: ["auth-me"],
    queryFn: () => apiGet<SessionResponse>("/api/auth/me"),
    // Retry transient (non-401) errors up to 2 times with backoff.
    // Never retry 401 — those mean "not logged in" and must redirect immediately.
    retry: (failureCount, err) =>
      !isUnauthorized(err instanceof Error ? err : null) && failureCount < 2,
    retryDelay: (attempt) => Math.min(1_000 * 2 ** attempt, 8_000),
    staleTime: 60_000,
  });

  const isAuthenticated =
    !isPending && !isAuthError && session !== undefined;

  return {
    isAuthenticated,
    isPending,
    isAuthError,
    authError: authError instanceof Error ? authError : null,
    session,
    refetchAuth: () => void refetch(),
  };
}

/**
 * Returns true iff the current session is 401-unauthenticated.
 * Useful for deciding whether to redirect to /login.
 */
export function isUnauthorized(authError: Error | null): boolean {
  return authError instanceof ApiError && authError.status === 401;
}
