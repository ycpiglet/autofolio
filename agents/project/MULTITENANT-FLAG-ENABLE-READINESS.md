# MULTITENANT FLAG-ENABLE READINESS

**Generated:** 2026-06-27T15:05:48+09:00
**Branch:** `feat/multitenant-phase4`
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

- [ ] **(a) Per-user re-enable / status / toggle endpoints**
- [ ] **(b) `_user_ctx` / `_user_run_locks` TTL/LRU eviction**
- [ ] **(c) Per-user broker / KIS credentials**
- [ ] **(d) SQLite → Supabase Postgres backend swap**

---

### (a) Per-user re-enable / status / toggle endpoints

**Current state:** NOT implemented.

**Why it gates:**
The engine control endpoints (`/api/engine/auto-trading`, `/api/engine/kill-switch`, `/api/engine/status`) are currently **global** — they act as a fleet master and are fail-closed. When a per-user circuit-breaker (daily-loss or consecutive-failures) trips, it writes a per-user disable row (`engine_state` keyed on `auto_trading_enabled:user_<id>`). However, there is **no per-user endpoint** to re-enable, query status, or toggle a single user's auto-trading.

Until these endpoints exist, a tripped user can only be recovered by the **global master** kill-switch — which affects every user simultaneously. This is operationally unacceptable in a multi-user environment: recovering one user's breaker would inadvertently re-enable all users, or operators would be forced to directly manipulate the database.

**Reference:** `app/api/routers/engine.py`

**Deliverables needed:**
- `GET /api/engine/users/{user_id}/status` — query per-user auto-trading state and circuit-breaker status
- `POST /api/engine/users/{user_id}/auto-trading` — enable/disable per-user auto-trading
- `POST /api/engine/users/{user_id}/kill-switch` — per-user kill-switch toggle
- Appropriate auth guard (admin-only or self-only)

---

### (b) `_user_ctx` / `_user_run_locks` TTL/LRU eviction

**Current state:** NOT implemented — both dicts are unbounded.

**Why it gates:**
- `_user_ctx` in `app/services/backend.py` is an in-process dict that caches a full engine `BacktestContext` per `user_id`. It is populated on first access and **never evicted**.
- `_user_run_locks` in `app/api/routers/engine.py` is an `asyncio.Lock` per `user_id`, also held in an unbounded dict forever.

Under single-owner operation (flag OFF) this is harmless — there is exactly one entry. Under multi-user load, each distinct `user_id` that ever hits the engine adds a permanent entry. With hundreds or thousands of users, this is a **memory leak** and an unbounded growth vector.

**Deliverables needed:**
- Replace `_user_ctx` with an LRU cache (e.g., `cachetools.LRUCache` with a reasonable cap) or add a TTL-based eviction background task.
- Replace `_user_run_locks` with a similarly bounded structure (e.g., `cachetools.TTLCache` with lock creation on demand).
- Confirm eviction policy does not race with an in-flight engine run (lock must outlive the run).

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

**Current state:** NOT implemented — DB layer is SQLite-only.

**Why it gates:**
The tenant scoping implemented in Phases 1-3 is **backend-agnostic SQL** (standard `WHERE user_id = ?` clauses). However, the connection layer (`app/database/sqlite_db.py`) is SQLite-specific: file-based, single-writer, no row-level security, no network access.

Enabling the flag does **not** move any data to Supabase Postgres. The app will continue writing to a local SQLite file regardless of the flag value. For the `autofolio-staging` (and eventually `autofolio-prod`) Supabase Postgres project to be used, a **separate migration** is required:

1. Replace `sqlite_db.py` connection layer with a Postgres/asyncpg or psycopg2 adapter.
2. Run schema migration (all existing tables + new `user_id` columns from Phases 1-3).
3. Configure Supabase Row-Level Security policies for tenant isolation at the DB layer.
4. Update `DATABASE_URL` env var and remove SQLite-specific pragmas.

This is a prerequisite because multi-tenant production load against a single SQLite file will immediately bottleneck (single-writer lock) and cannot scale to even two concurrent users safely.

**Reference:** `app/database/sqlite_db.py`

---

## Summary

| Item | Owner | Current State | Blocks |
|------|-------|---------------|--------|
| (a) Per-user control endpoints | Backend Engineer | Not built | Operator recovery from breaker trip |
| (b) `_user_ctx` / `_user_run_locks` eviction | Backend Engineer | Unbounded dicts | Memory leak under N users |
| (c) Per-user KIS credentials | Backend Engineer + KIS API Engineer | Shared singleton | Brokerage account isolation |
| (d) SQLite → Postgres backend swap | Data Engineer + Backend Engineer | SQLite only | Concurrent writes, RLS, Supabase staging |

**All four must be DONE and Owner-approved before `AUTOFOLIO_MULTI_TENANT_ENABLED=1` is set in any shared environment.**
