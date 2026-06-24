/**
 * Unit tests for auth-gate resilience logic.
 *
 * Tests the retry predicate and isUnauthorized guard that prevent the
 * blank-spinner + auth-me refetch loop when the backend is unreachable:
 * - 401 → never retry (immediate login redirect)
 * - non-401 (500/network) → retry up to 2 times, then show "연결 오류" UI
 *
 * NOTE: useAuthSession.ts has `"use client"` + react-query imports, so
 * the hook itself cannot be imported here (vitest runs in `node` env with
 * no DOM). We test the pure isUnauthorized + retryPredicate logic in
 * isolation by importing only ApiError and implementing the predicate
 * inline (must stay in sync with useAuthSession.ts).
 */

import { describe, it, expect } from "vitest";
import { ApiError } from "../lib/api";

/**
 * isUnauthorized — copy of the exported pure function from useAuthSession.ts.
 * Kept here to allow pure-node unit testing without React/react-query deps.
 */
function isUnauthorized(authError: Error | null): boolean {
  return authError instanceof ApiError && authError.status === 401;
}

/**
 * retryPredicate — mirrors the `retry` option in useAuthSession's useQuery call.
 * If this changes in useAuthSession.ts, update here too.
 */
function retryPredicate(failureCount: number, err: unknown): boolean {
  const normalizedErr = err instanceof Error ? err : null;
  return !isUnauthorized(normalizedErr) && failureCount < 2;
}

describe("isUnauthorized (auth-gate resilience)", () => {
  it("returns true for ApiError with status 401", () => {
    expect(isUnauthorized(new ApiError(401, {}))).toBe(true);
  });

  it("returns false for ApiError with status 500", () => {
    expect(isUnauthorized(new ApiError(500, {}))).toBe(false);
  });

  it("returns false for a generic Error (network failure etc.)", () => {
    expect(isUnauthorized(new Error("fetch failed"))).toBe(false);
  });

  it("returns false for null", () => {
    expect(isUnauthorized(null)).toBe(false);
  });
});

describe("auth-me retry predicate (auth-gate resilience)", () => {
  it("never retries a 401 error — ensures immediate redirect, no loop", () => {
    const err = new ApiError(401, {});
    expect(retryPredicate(0, err)).toBe(false);
    expect(retryPredicate(1, err)).toBe(false);
    expect(retryPredicate(2, err)).toBe(false);
  });

  it("retries a 500 error up to 2 times then stops", () => {
    const err = new ApiError(500, {});
    expect(retryPredicate(0, err)).toBe(true);  // 1st retry ok
    expect(retryPredicate(1, err)).toBe(true);  // 2nd retry ok
    expect(retryPredicate(2, err)).toBe(false); // stop — show error UI
  });

  it("retries a network error (non-ApiError) up to 2 times then stops", () => {
    const err = new Error("Failed to fetch");
    expect(retryPredicate(0, err)).toBe(true);
    expect(retryPredicate(1, err)).toBe(true);
    expect(retryPredicate(2, err)).toBe(false);
  });

  it("does not retry at failureCount >= 2 for any transient error", () => {
    const err503 = new ApiError(503, {});
    expect(retryPredicate(2, err503)).toBe(false);
    expect(retryPredicate(5, err503)).toBe(false);
  });
});
