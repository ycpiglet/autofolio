---
type: evidence
id: EVIDENCE-2026-06-12-004
status: 완료
author: QA + Lead Engineer (Codex)
created: 2026-06-12
created_at: 2026-06-12T12:27:28+09:00
tags: [qa, tests, task-registration, paper, quant]
scope: generated quant test execution and unexecutable gap task registration
applies_to: [Autofolio host]
---

# EVIDENCE-2026-06-12-004 — Generated Tests And Gap Tasks

## Executable Generated Tests

Command:

- `pytest tests/integration/test_quant_trading_scenario_catalog.py tests/integration/test_paper_scenario_matrix.py -q`

Result:

- 119 passed

Interpretation:

- 현재 구현된 기능만 기준으로 generated executable test cases are green.
- Scope is mock/paper-safe only. No prod and no live KIS order.

## Existing Tasks Covering Catalog-Only Gaps

| Gap | Existing Task |
|-----|---------------|
| after-hours order/session path | TASK-014 |
| margin/short order path | TASK-021 |
| overseas stock order path | TASK-022 |

## Newly Registered Gap Tasks

| Gap | Task |
|-----|------|
| direct KRX alternative products: direct bond/REIT/ELW/product-specific ETN | TASK-026 |
| KRX derivatives: futures/options/FX futures | TASK-027 |
| advanced order types: stop/stop-limit/trailing/MOO/MOC/IOC/FOK | TASK-028 |
| FIX-style partial fill/pending cancel/too-late lifecycle | TASK-029 |
| actual block/basket execution model | TASK-030 |
| halt/VI/disclosure engine risk gates | TASK-031 |
| stale/invalid data, holiday, corporate action gates | TASK-032 |
| cash/fee/slippage/concentration portfolio reality model | TASK-033 |
| scheduled strategy patterns: DCA/pairs/volatility/calendar/EOD | TASK-034 |

## Verification

- `pytest tests/integration/test_quant_trading_scenario_catalog.py tests/integration/test_paper_scenario_matrix.py -q` — 119 passed
- `python scripts/generate_views.py --check` — OK: 33 TASK views up-to-date
- `python scripts/validate_task_schema.py` — OK
- `python scripts/check_upstream_issues.py --warn` — OK
- `python scripts/check_agent_docs.py` — OK: 0 errors, 74 existing warnings
- `python scripts/doc_health_report.py` — Status G
- `python scripts/query_reports.py --kind BRIEF` — BRIEF-2026-06-12-004 indexed
- `git diff --check` — no whitespace errors; CRLF warnings only

## 판단

- Generated executable cases all pass for currently implemented functionality.
- Unexecutable catalog gaps are now represented by existing TASK-014/021/022 plus new TASK-026 through TASK-034.
