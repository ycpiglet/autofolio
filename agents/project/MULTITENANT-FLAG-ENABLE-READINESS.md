# MULTITENANT FLAG-ENABLE READINESS

**Generated:** 2026-06-27T15:05:48+09:00
**Last updated:** 2026-06-27T18:13:55+09:00
**Branch:** `feat/multitenant-phase4` → merged; PG-readiness closeout on `chore/pg-readiness-closeout`
**Flag:** `AUTOFOLIO_MULTI_TENANT_ENABLED`

---

## Gate Statement

> **The flag `AUTOFOLIO_MULTI_TENANT_ENABLED` MUST remain `OFF` (default) in all environments — including staging — until ALL four items below are completed AND the Owner explicitly approves flag enablement.**

No individual engineer may set this flag to `1` in any shared or staging environment without Owner sign-off. Local/unit-test usage with the flag on is permitted for development purposes only.

---

## What Phase 4 Proved

Phase 4 (this branch) established two independent test gates:

1. **Cross-user isolation e2e** (`tests/integration/test_multitenant_isolation_e2e.py`, 14 tests, 6 layers): With the flag ON, every isolation layer (conditions, order/exec logs, daily aggregates, engine run, circuit-breaker, engine state / kill-switch) maintains strict per-user scoping. No cross-user data leak was found in any layer.

2. **Flag-OFF characterization** (`tests/integration/test_multitenant_flagoff_characterization.py`, 9 tests, 7 invariants): With the flag OFF, every tenant-aware code path produces byte-identical behavior to the original single-owner system. Flipping the flag is the **only** behavior change.

**Conclusion:** The Phases 1-3 implementation is correct. Flipping `AUTOFOLIO_MULTI_TENANT_ENABLED=1` is the sole behavioral gate — everything else is gated on the four items below.

---

## Required Prerequisites Before Flag Enable

### Checklist

- [x] **(a) Per-user re-enable / status / toggle endpoints** — COMPLETE (PR #134)
- [x] **(b) `_user_ctx` / `_user_run_locks` TTL/LRU eviction** — COMPLETE (PR #134)
- [ ] **(c) Per-user broker / KIS credentials** — REMAINING (Owner secrets required)
- [x] **(d) SQLite → Supabase Postgres backend swap** — COMPLETE (PRs #132/#133/#135, live-verified vs `autofolio-staging`)

---

### (a) Per-user re-enable / status / toggle endpoints

**Current state:** COMPLETE — PR #134 (2026-06-27T18:13:55+09:00).

Owner-only per-user endpoints implemented and flag-gated:
- `GET /api/engine/users/{user_id}/status` — per-user auto-trading state and circuit-breaker status
- `POST /api/engine/users/{user_id}/auto-trading` — per-user auto-trading enable/disable
- `POST /api/engine/users/{user_id}/kill-switch` — per-user kill-switch toggle

All endpoints are owner-only and no-op when `AUTOFOLIO_MULTI_TENANT_ENABLED=0`.

**Reference:** `app/api/routers/engine.py`

---

### (b) `_user_ctx` / `_user_run_locks` TTL/LRU eviction

**Current state:** COMPLETE — PR #134 (2026-06-27T18:13:55+09:00).

- `_user_ctx` in `app/services/backend.py` replaced with LRU eviction (bounded cap).
- `_user_run_locks` in `app/api/routers/engine.py` replaced with TTL-bounded structure.
- Ghost-lock TOCTOU (checkout refcount) race fixed.
- Eviction is no-op when `AUTOFOLIO_MULTI_TENANT_ENABLED=0` (single-owner path unchanged).

---

### (c) Per-user broker / KIS credentials

**Current state:** NOT implemented — single shared broker account.

**Why it gates:**
`_ctx_for_user` in `app/services/backend.py` creates a per-user `BacktestContext` but **copies the singleton's broker instance** (same KIS app-key, same KIS account number, same SQLite DB connection) into it. The per-user context only scopes the **data queries** (conditions, logs, aggregates); the actual **brokerage account** remains shared.

Under multi-tenant trading this means:
- User A's buy order executes against User B's brokerage account.
- Daily-loss and buying-power limits are evaluated against a single shared account balance.
- KIS imposes per-app-key rate limits — all users share one quota.

True multi-tenant trading requires per-user KIS app-key + secret-key + account number stored (securely) per user, resolved by `_ctx_for_user` at run time. Until then, enabling the flag provides DB-level isolation only, not brokerage-account isolation.

**Reference:** `app/services/backend.py::_ctx_for_user`

**Deliverables needed:**
- Secure per-user credential store (encrypted at rest; Supabase row-level-security recommended).
- `_ctx_for_user` reads and injects per-user KIS credentials.
- Per-user broker client instantiation (not a copy of the singleton's client).
- Fallback / onboarding flow if a user has no credentials yet.

---

### (d) SQLite → Supabase Postgres backend swap

**Current state:** COMPLETE — PRs #132 / #133 / #135 (live-verified 2026-06-27T18:13:55+09:00).

- PR #132: `app/database/pg_db.py` config-gated adapter (`DATABASE_URL`; default SQLite byte-identical; psycopg optional via `requirements-postgres.txt`).
- PR #133: SQL dialect portability — boolean, KST-date, ON CONFLICT portable; `supabase/migrations/0004_aux_tables.sql`. LIVE-verified via MCP against `autofolio-staging` (whitelist + system_state-global + boolean upserts confirmed working on real PG).
- PR #135: `investor_profile.py` PG-readiness (skip SQLite table-init on PG). LIVE-verified via MCP (investor_profiles upsert + checkin RETURNING on real PG).

**Remaining (not code — Owner-gated):**
- Live psycopg connection to `autofolio-staging` requires the DB password (Owner secret, set at deploy time via `DATABASE_URL`).
- Railway/Render backend host requires external account access (Owner/R3 gate).

**Reference:** `app/database/pg_db.py`, `app/database/sqlite_db.py`

---

## Summary

| Item | Owner | Current State | Blocks |
|------|-------|---------------|--------|
| (a) Per-user control endpoints | Backend Engineer | **DONE** — PR #134 | ~~Operator recovery from breaker trip~~ |
| (b) `_user_ctx` / `_user_run_locks` eviction | Backend Engineer | **DONE** — PR #134 | ~~Memory leak under N users~~ |
| (c) Per-user KIS credentials | Backend Engineer + KIS API Engineer | **REMAINING** — needs Owner real KIS keys per user | Brokerage account isolation |
| (d) SQLite → Postgres backend swap | Data Engineer + Backend Engineer | **DONE** — PRs #132/#133/#135, live-verified | ~~Concurrent writes, RLS, Supabase staging~~ |

**Items (a), (b), (d) are code-complete. Item (c) requires Owner-provided per-user KIS credentials (real secrets). Owner explicit approval is also required before `AUTOFOLIO_MULTI_TENANT_ENABLED=1` is set in any shared environment.**
