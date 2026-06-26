---
schema_version: agent-runtime-work-item/v1
work_id: INIT-MULTITENANT-ENGINE
work_uid: a9c4e712-58b3-4d7f-b081-3e6d2f1a0c95
kind: initiative
status: planned
owner: Lead Engineer
created_at: 2026-06-27T03:40:18+09:00
updated_at: 2026-06-27T03:40:18+09:00
origin_type: task_split
origin_ref: TASK-087
created_by: lead_engineer
title: Multi-Tenant Engine Isolation
summary: Per-user isolation of the trading engine, repository queries, risk context, and circuit-breaker state. Split from TASK-087 A8 as a safety-critical, flag-gated, sequenced initiative. Default OFF (AUTOFOLIO_MULTI_TENANT_ENABLED). Must not be partially rolled out.
tags: [multitenant, engine, safety, isolation, membership, backend]
priority: P1
---

# INIT-MULTITENANT-ENGINE

## Purpose

The trading engine is currently single-tenant: schema trading tables, unscoped
`repositories.py` queries, `_ctx()` lru_cache singleton, process
`_run_once_lock`, global `system_state`/`risk_limits`, and a circuit breaker on
global PnL. A partial rollout is **safety-critical**: one user could see or act
on another's positions, or one user's loss could disable the entire engine for
all users.

This initiative implements full per-user isolation behind a single
`AUTOFOLIO_MULTI_TENANT_ENABLED` flag (already reserved in `flags.py` A1,
default OFF). The flag-OFF path must be byte-identical to today's single-owner
behavior and must be covered by characterization tests **before the flag is ever
turned on in staging**.

Estimated scope: ~44 files, 1200–1500 LOC.

## Included Tasksets

| ID | Description | Status |
|----|-------------|--------|
| TASKSET-MULTITENANT-ENGINE | Four-phase isolation sequence | planned |

## Phase Sequence

All four phases must be completed in order. Skipping or partially applying any
phase while the flag is ON in a shared environment is forbidden.

### Phase 1 — Repository query-scoping

Add `WHERE user_id = <uid>` across ~25 query and aggregate methods in
`repositories.py`. The `nullable user_id` columns are already present via
TASK-087 A4 migrations (not yet applied to production). Unscoped queries on
tenant-owned tables become errors when the flag is ON.

### Phase 2 — Per-user risk context

Replace shared `risk_limits` and the global circuit-breaker PnL accumulator
with per-user structures in `safety_checker.py` / `today_realized_pnl()`. One
user's loss does not trigger another user's circuit breaker.

### Phase 3 — Per-user engine pool / queue

Replace the `_ctx()` singleton and process `_run_once_lock` with a per-user
engine instance pool and per-user task queue. Users are isolated at the
asyncio/process boundary.

### Phase 4 — Cross-user isolation tests + flag-OFF characterization

- Confirm member A cannot read, write, or act on member B's positions or risk state.
- Confirm engine state for A is unaffected by B's circuit-breaker trigger.
- Prove flag-OFF path is byte-identical to today's single-owner behavior
  (snapshot/characterization tests executed **before** the flag is turned ON in
  staging for the first time).

## Boundary

This initiative does not:

- Apply Supabase migrations (Owner/R3 gate — see TASK-087 BUCKET B).
- Activate production deploy or real user data.
- Change the kill-switch, order approval flow, or risk-gate policy values.
- Merge with TASK-087 BUCKET B/C scope.

## Activation Gate

`AUTOFOLIO_MULTI_TENANT_ENABLED` must remain `0`/unset in all environments
until Phase 4 characterization tests pass and the Owner explicitly approves
staging activation.
