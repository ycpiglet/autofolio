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
  /** True while the initial /api/auth/me request is in-flight. */
  isPending: boolean;
  /** True when /api/auth/me returned 401 (or another error). */
  isAuthError: boolean;
  /** The raw auth error, if any. */
  authError: Error | null;
  /** Session payload, available once authenticated. */
  session: SessionResponse | undefined;
}

export function useAuthSession(): AuthSession {
  const {
    data: session,
    isPending,
    isError: isAuthError,
    error: authError,
  } = useQuery<SessionResponse>({
    queryKey: ["auth-me"],
    queryFn: () => apiGet<SessionResponse>("/api/auth/me"),
    retry: false,
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
  };
}

/**
 * Returns true iff the current session is 401-unauthenticated.
 * Useful for deciding whether to redirect to /login.
 */
export function isUnauthorized(authError: Error | null): boolean {
  return authError instanceof ApiError && authError.status === 401;
}
