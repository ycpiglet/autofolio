---
type: evidence
id: EVIDENCE-2026-06-12-007
status: 완료
author: Performance Analyst + Backend Engineer + QA (Codex)
created: 2026-06-12
created_at: 2026-06-12T23:44:23+09:00
tags: [qa, portfolio, cash, fees, slippage, concentration]
scope: TASK-033 mock portfolio reality model and UI execution-log consistency
applies_to: [Autofolio host]
---

# EVIDENCE-2026-06-12-007 — Portfolio Reality Model

## Question

Can the currently mock-safe Autofolio stack test cash shortage, fees, slippage,
concentration rejection, and UI execution-log consistency without touching live
KIS order paths or risk policy?

## Work Performed

- Added optional portfolio ledger behavior to `MockBrokerClient`:
  - `cash_balance`
  - `fee_rate`
  - `slippage_bps`
  - `max_position_weight`
- Kept default mock behavior unchanged when those options are not set.
- Added read-only execution aggregation to `Repository.list_order_logs()`.
- Updated `backend.recent_fills()` so MARKET fills display execution log
  `filled_price`/`filled_quantity` instead of blank `order_price`.
- Added unit/integration tests for:
  - cash ledger accounting
  - fee/slippage accounting
  - insufficient cash rejection
  - concentration rejection
  - UI KPI/recent-fills consistency with execution logs

## Verification

- `pytest tests/unit/test_mock_portfolio_ledger.py tests/integration/test_portfolio_reality_model.py -q` — 9 passed.
- `pytest tests/unit/test_backend_kpis.py tests/unit/test_backend_holdings.py tests/integration/test_paper_scenario_matrix.py::test_ui_backend_reflects_filled_scenario -q` — 19 passed.
- `pytest tests/integration/test_quant_trading_scenario_catalog.py tests/integration/test_paper_scenario_matrix.py -q` — 119 passed.
- `pytest tests/unit/test_engine_market_fallback.py tests/integration/test_mock_order_flow.py -q` — 7 passed.
- `python -m py_compile app/brokers/mock/mock_client.py app/database/repositories.py app/ui/backend.py tests/unit/test_mock_portfolio_ledger.py tests/integration/test_portfolio_reality_model.py` — OK.
- `git diff --check` — OK, CRLF warnings only.

## Boundaries

- No KIS paper/prod order command was run.
- No `.env`, `KIS_*`, account, or secret surface was read or changed.
- No `app/brokers/kis/**`, `app/risk/**`, DB schema/migration, or CI workflow
  file was changed.
- Real broker buying-power or production risk-budget enforcement remains an R3
  follow-up.

## Result

TASK-033 is complete for mock-safe portfolio reality coverage. Tax modeling
remains a policy/data-source placeholder and should not be inferred from this
mock ledger.
