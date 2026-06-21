---
type: evidence
id: EVIDENCE-2026-06-18-007
title: Portfolio diagnosis hub rebuild
created_at: 2026-06-18T19:18:46+09:00
owner: QA
related_task: TASK-083
tags: [portfolio, ui, api, analytics, kis, qa]
status: pass
redaction: no raw account number, token, secret, cash source payload, or broker order payload recorded
official_sources: []
---

# Portfolio diagnosis hub rebuild

## What Changed

Added:

- `/api/portfolio/overview`.
- `/api/portfolio/groups` GET/POST/PUT/DELETE.
- `portfolio_symbol_aliases`, `portfolio_groups`, `portfolio_group_members`.
- `web/src/components/domain/PortfolioDashboard.tsx`.
- `tests/unit/test_portfolio_groups.py`.
- `E2E_PORT` support in Playwright config.

Updated:

- KIS position parsing preserves product name, market value, unrealized PnL, return percent, and raw row.
- Portfolio backend now exposes KPI, enriched holdings, automatic/manual/saved groups, diagnostics, top movers, concentration, allocation gap, and data quality.
- `/portfolio` renders KPI, diagnosis, holdings, groups, and performance tabs.
- UI spec and demo E2E mocks include the overview payload.

## Safety Contract

| Contract | State |
|----------|-------|
| No live order executed | pass |
| No order/risk gate weakening | pass |
| No secret/account mutation | pass |
| No production DB migration apply | pass |
| Group mutation owner+CSRF gated | pass |
| Missing symbol names surfaced as data quality | pass |
| Existing stale E2E server not killed | pass |

## Verification

| Command | Result |
|---------|--------|
| py_compile focused backend files | pass |
| `pytest tests\unit\test_backend_holdings.py tests\unit\test_backend_kpis.py tests\unit\test_kis_client.py tests\unit\test_portfolio_groups.py tests\unit\test_services_shim.py tests\api\test_portfolio.py tests\api\test_gate.py -q` | 91 passed |
| `pytest tests\api\test_analysis.py tests\unit\test_perf_report.py tests\unit\test_backend_allocation_gap.py -q` | 62 passed |
| `npm run lint` | pass |
| `npm run build` | pass, `/portfolio` route generated |
| `$env:E2E_PORT='3101'; npm run test:e2e -- e2e/demo-walkthrough.spec.ts --reporter=line` | 1 passed |
| Local production smoke on API 8002 + web 3002 | `/api/health`, `/portfolio`, proxied `/api/portfolio/overview` all 200 |
| Browser smoke on web 3002 | `포트폴리오`, `총자산`, `진단`, `수동 그룹` visible |

## Observations

- A stale `node` listener already existed on port 3100 from an earlier run. The E2E config now accepts `E2E_PORT`, and the verification used 3101 instead of terminating the existing process.
- The first walkthrough retry exposed a selector ambiguity because `/portfolio` now has both sidebar navigation and portfolio-view navigation. E2E selectors were updated to target `aria-label="사이드바 내비게이션"`.

## Watch

The data-quality panel can identify holdings still falling back to ticker names,
but complete sector/strategy/risk metadata depends on KIS product names and the
local alias/group metadata maintained by the product.
