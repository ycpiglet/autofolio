import { defineConfig } from "vitest/config";

// Unit-test runner for the web/ package.
//
// Pure helpers (e.g. src/lib/format.ts) need no DOM, so the `node` environment
// is sufficient and fastest. `globals` is intentionally left OFF: tests import
// { describe, it, expect } from "vitest" explicitly, which keeps tsc clean
// (no ambient global test types leaking into the project type-check).
//
// Playwright E2E specs live under tests/ and are run separately via
// `npm run test:e2e`; the `include` glob below scopes vitest to unit tests only.
export default defineConfig({
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
});
