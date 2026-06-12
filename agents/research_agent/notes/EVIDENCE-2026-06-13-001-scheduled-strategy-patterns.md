---
type: evidence
id: EVIDENCE-2026-06-13-001
status: 완료
author: Quant Researcher + QA (Codex)
created: 2026-06-13
created_at: 2026-06-13T00:05:22+09:00
tags: [qa, strategy, scheduler, dca, pairs, volatility, rebalance]
scope: TASK-034 scheduled strategy mock/backtest harness
applies_to: [Autofolio host]
---

# EVIDENCE-2026-06-13-001 — Scheduled Strategy Patterns

## Work Performed

- Added `tests/integration/test_scheduled_strategy_patterns.py`.
- Added a test-local deterministic clock and persistent scheduler harness.
- Stabilized the existing daily-limit scenario fixture so synthetic prior orders
  use the same KST-local date basis as the daily amount limit assertion.
- Covered:
  - DCA scheduled event emission
  - persistent scheduled event replay once-only behavior
  - calendar rebalance buy/sell intents
  - pairs strategy market-neutral intents
  - volatility breakout trigger/wait behavior
  - end-of-day liquidation sell intents
  - strategy-to-condition prod-target refusal

## Verification

- `pytest tests/integration/test_scheduled_strategy_patterns.py -q` — 7 passed.
- `pytest tests/integration/test_quant_trading_scenario_catalog.py tests/integration/test_paper_scenario_matrix.py -q` — 119 passed.
- `python -m py_compile tests/integration/test_scheduled_strategy_patterns.py` — OK.
- `git diff --check` — OK.

## Local Fixture Issue (6W1H)

| Field | Record |
|-------|--------|
| Who | QA (Codex) |
| What | `test_daily_order_amount_limit_blocks_new_order` failed after midnight KST because the synthetic prior order used SQLite UTC `CURRENT_TIMESTAMP` while the assertion path compares against `DATE('now', 'localtime')`. |
| When | 2026-06-13T00:08:39+09:00 |
| Where | `tests/integration/test_paper_scenario_matrix.py` |
| Why | The test fixture intended a same-local-day prior order, but relied on SQLite default UTC timestamp. |
| How | Added a test helper that updates the synthetic prior order to `datetime('now', 'localtime')`. |
| Result | The scenario remains a test-only daily-limit check; production risk behavior was not changed. |

## Boundary

- No live scheduler daemon or production execution loop change.
- No KIS broker, live order, risk policy, schema/migration, secret, or prod surface change.
- Strategy intents are converted only to mock trade-condition fixtures with `auto_enabled=False`.
- `target_env="prod"` is rejected in the harness.
- The daily-limit stabilization is test-fixture only and does not alter safety policy.

## Result

TASK-034 is complete for mock/backtest-first scheduled strategy coverage.
