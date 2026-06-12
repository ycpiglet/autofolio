---
type: evidence
id: EVIDENCE-2026-06-12-008
status: 완료
author: Backend Engineer + QA (Codex)
created: 2026-06-12
created_at: 2026-06-12T23:51:57+09:00
tags: [qa, order-lifecycle, partial-fill, fix, mock]
scope: TASK-029 FIX-style order lifecycle mock/test harness
applies_to: [Autofolio host]
---

# EVIDENCE-2026-06-12-008 — Order Lifecycle

## Work Performed

- Added `tests/integration/test_order_lifecycle.py`.
- Added a test-local scripted broker for pending-limit lifecycle states.
- Added a `PartialFillLedger` harness to verify cumulative execution logs:
  - filled quantity
  - remaining quantity
  - weighted average execution price
- Covered:
  - partial fill sequence
  - pending limit filled before cancel
  - cancel reject disables auto trading
  - too-late-to-cancel late fill record

## Verification

- `pytest tests/integration -k order_lifecycle -q` — 8 passed.
- `pytest tests/integration/test_paper_scenario_matrix.py -q` — 16 passed.
- `python -m py_compile tests/integration/test_order_lifecycle.py` — OK.
- `git diff --check` — OK.

## Boundary

- No `app/engine/order_flow.py` production behavior change.
- No KIS broker, live order, risk policy, schema/migration, or secret surface change.
- Production partial-fill persistence and cancel-replace semantics remain R3/order-flow follow-up work.

## Result

TASK-029 is complete for mock/test-harness first coverage.
