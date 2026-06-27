---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-MULTITENANT-ENGINE
work_uid: c7f2a391-8de4-4b6c-9a15-7f0e3d9b2e48
kind: taskset
parent_id: INIT-MULTITENANT-ENGINE
status: completed
owner: Lead Engineer
created_at: 2026-06-27T03:40:18+09:00
updated_at: 2026-06-27T15:28:04+09:00
completed_at: 2026-06-27T15:28:04+09:00
resolution: done
verification_status: passed
origin_type: task_split
origin_ref: TASK-087
created_by: lead_engineer
title: Multi-Tenant Engine Isolation — Four-Phase Sequence
summary: >
  Sequenced tasks for per-user repository scoping, risk context isolation,
  engine pool/queue, and cross-user characterization tests. All behind
  AUTOFOLIO_MULTI_TENANT_ENABLED (default OFF). Partial rollout is forbidden.
  ALL FOUR PHASES COMPLETE (PRs #127-#130, merged 2026-06-27). Full pytest
  1766 passed / 0 failed. FLAG STAYS OFF in all environments until
  MULTITENANT-FLAG-ENABLE-READINESS.md items + Owner approval.
tags: [multitenant, engine, safety, isolation, membership, backend]
priority: P1
task_set_id: TASKSET-MULTITENANT-ENGINE
---

# TASKSET-MULTITENANT-ENGINE

## Purpose

Implement full per-user engine isolation in four sequenced phases behind a
single `AUTOFOLIO_MULTI_TENANT_ENABLED` feature flag. Each phase must be
reviewed and merged before the next phase begins. The flag stays OFF in all
environments until Phase 4 characterization tests pass and the Owner approves
staging activation.

## Source Plan

- `agents/project/initiatives/INIT-MULTITENANT-ENGINE.md`
- `app/services/flags.py` — `multi_tenant_enabled()` (reserved, default OFF)
- `app/repositories.py` — unscoped query methods
- `app/services/safety_checker.py` — global PnL / circuit breaker
- Engine context: `_ctx()` lru_cache singleton + `_run_once_lock`
- `supabase/migrations/*.sql` — nullable `user_id` columns (A4, unapplied)

## Included Tasks

| work_id | Phase | Description | Owner | Status | Gate | PR |
|---------|-------|-------------|-------|--------|------|----|
| PHASE1-PR127 | 1 | Repository query-scoping: 14 methods `WHERE user_id`; flag-guard unscoped paths | Backend Engineer | 완료 | flag OFF; unit tests pass | #127 |
| PHASE2-PR128 | 2 | Per-user risk context: per-user `risk_limits` + per-user circuit-breaker PnL in `safety_checker.py` | Backend Engineer | 완료 | flag OFF; Phase 1 merged | #128 |
| PHASE3-PR129 | 3 | Per-user engine pool/queue: per-user context pool + per-user run lock + per-user engine_state (auto_trading/kill-switch/both circuit-breakers; consecutive-failures cross-user hole closed) | Backend Engineer | 완료 | flag OFF; Phase 2 merged | #129 |
| PHASE4-PR130 | 4 | Cross-user e2e isolation tests (6 layers) + flag-OFF characterization (byte-identical proven) + `MULTITENANT-FLAG-ENABLE-READINESS.md` | QA / Backend Engineer | 완료 | pytest 1766 passed; Owner approval before flag ON in staging | #130 |

**All four phases are complete. FLAG STAYS OFF** in all environments until the
readiness items in `agents/project/MULTITENANT-FLAG-ENABLE-READINESS.md` are
satisfied and the Owner explicitly approves staging activation.

## Dependency Map

```text
Phase 1 (repo scoping)
  -> Phase 2 (per-user risk context)
       -> Phase 3 (per-user engine pool)
            -> Phase 4 (cross-user tests + characterization)
                  -> Owner approval -> staging flag ON
```

## Boundaries

Allowed:

- Code changes behind the `AUTOFOLIO_MULTI_TENANT_ENABLED` flag only.
- Unit and integration tests (flag OFF path byte-identical to current behavior).
- Cross-user isolation assertions (flag ON path in test environment only).

Blocked until Phase 4 + Owner approval:

- Setting `AUTOFOLIO_MULTI_TENANT_ENABLED=1` in any shared/staging/production environment.
- Applying Supabase migrations (Owner/R3 gate — TASK-087 BUCKET B).
- Changing kill-switch, order approval flow, or risk-gate policy values.
- Live execution or real user data exposure.

## Safety Rationale

A partial rollout (any phase ON without all prior phases complete) can result in:

- Cross-user data read (unscoped queries returning another user's rows).
- Cross-user circuit-breaker contamination (one user's loss disabling another's engine).
- Singleton engine state mutations surfacing to multiple users.

These are not performance issues — they are correctness and safety failures.
