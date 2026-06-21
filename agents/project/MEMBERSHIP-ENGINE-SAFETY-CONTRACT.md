# Autofolio Membership Engine Safety Contract

Status: draft contract, not applied to runtime
Updated: 2026-06-19T19:46:50+09:00
Related: TASK-087, TASK-108, TASK-109, TASK-113, TASK-114

## Purpose

This contract defines what must become user-scoped before external members can
use engine or live-readiness features. It is intentionally not an engine,
OrderFlow, SafetyChecker, KIS broker, risk policy, database migration, or deploy
change.

The machine-readable source is
`agents/project/MEMBERSHIP-ENGINE-SAFETY-CONTRACT.json`. The local gate is:

```powershell
python scripts/membership_engine_safety_gate.py --check
```

## Current Risk

The current local implementation is owner-oriented and uses global surfaces:

- `system_state` flags such as `auto_trading_enabled`, `kill_switch_active`,
  `global_mode`, and `consecutive_order_failures`;
- `risk_limits` with `scope = GLOBAL`;
- `trade_conditions`, `order_logs`, and `execution_logs` without production
  `user_id` isolation;
- one process-level engine run and condition claim path.

That is acceptable for the local Owner prototype, but it is not production
multi-user safety.

## Required Per-User Surfaces

Before external members can use live-readiness features, these surfaces must be
tenant-owned:

- engine state;
- engine run queue;
- trade conditions;
- safety flags;
- risk limits;
- circuit breakers;
- append-only order intents;
- order logs;
- execution logs;
- notifications.

Each production row or worker item must carry `user_id`, and worker execution
must receive explicit user context before reading flags, risk limits, KIS
credentials, order intents, or logs.

## Invariants

- Members do not share a global auto-trading flag.
- Kill switch is per user; a global emergency stop can only add a broader stop.
- Risk limits and circuit breakers are per user.
- Queue claims include `user_id`.
- Order intents are append-only and are created before any broker order call.
- OrderFlow and SafetyChecker require user context for production execution.
- KIS credential context must belong to the same user as the order intent.
- Owner/admin overrides are server-side and audited.
- This contract does not authorize live execution.

## Launch Gates

Production remains blocked until schema user fields, queue isolation tests,
member cross-user denial tests, per-user kill switch tests, risk-limit isolation
tests, append-only order-intent tests, user-scoped KIS credential tests, explicit
R3 live-execution approval, and staging dry-run smoke evidence all exist.

This contract intentionally lets readiness distinguish policy/contract evidence
from actual implementation. The `per_user_engine_safety` blocker remains until
implementation and staging evidence exist.
