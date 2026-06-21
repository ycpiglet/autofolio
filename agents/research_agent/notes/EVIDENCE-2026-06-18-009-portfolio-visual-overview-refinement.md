---
type: evidence
id: EVIDENCE-2026-06-18-009
title: Portfolio visual overview refinement
created_at: 2026-06-18T22:48:23+09:00
owner: QA
related_task: TASK-085
tags: [portfolio, ui, visualization, api, qa]
status: pass
redaction: no raw account number, token, secret, cash source payload, or broker order payload recorded
official_sources:
  - https://www.morningstar.com/help-center/portfolio/xray
  - https://www.fidelity.com/planning/investment/content/portanalyze.shtml
  - https://www.fidelity.com/learning-center/trading-investing/asset-allocation
---

# Portfolio visual overview refinement

## What Changed

- Rebuilt `/portfolio` around `PortfolioDashboard`.
- Added read-only `/api/portfolio/overview` to provide normalized KPI, holdings, groups, diagnostics, top movers, concentration, allocation gap, and data-quality payloads.
- Added Owner+CSRF-gated `/api/portfolio/groups` create/update/delete endpoints backed by `system_state` JSON metadata.
- Added default symbol aliases and sector metadata for current paper basket symbols so holdings do not show only numeric codes.
- Added visual overview cards: asset trend, target allocation donut/gap, asset-class exposure, sector exposure, concentration, contributors, detractors.
- Fixed tooltip clipping with viewport fixed positioning.
- Replaced mono numeric styling in portfolio surfaces with Pretendard + `tabular-nums`.
- Removed generic uppercase token highlighting that made only `SK` bold in `SK하이닉스`.
- Added cached/empty-schema fallback for live KIS read-only holdings failures so portfolio overview degrades instead of surfacing a 500.

## Research Basis

| Source | Used For |
|--------|----------|
| Morningstar Portfolio X-Ray | Asset class, region/style/sector breakdown and holding-level contribution |
| Fidelity Portfolio Analyzer | Graphical + holdings view, asset allocation, domestic/foreign exposure, industry weights, historical performance |
| Fidelity asset allocation guide | Stocks/bonds/cash as big-picture portfolio mix and performance/risk driver |

## Safety Contract

| Contract | State |
|----------|-------|
| Portfolio tab only for UI restructuring | pass |
| Read-only overview API | pass |
| Manual group mutation owner+CSRF gated | pass |
| No live order executed | pass |
| No order/risk gate changed | pass |
| No secret/account mutation | pass |
| No DB schema/migration | pass |

## Verification

| Command | Result |
|---------|--------|
| `.venv\Scripts\python.exe -m pytest tests/unit/test_backend_holdings.py tests/unit/test_backend_kpis.py tests/unit/test_backend_allocation_gap.py tests/unit/test_portfolio_groups.py tests/api/test_portfolio.py -q` | 50 passed, 1 warning |
| `npm run lint` | pass |
| `npm run build` | pass, `/portfolio` generated; final local production build used `API_INTERNAL_URL=http://127.0.0.1:8002` |
| `API_INTERNAL_URL=http://127.0.0.1:8002 npm run test:e2e -- e2e/demo-walkthrough.spec.ts --reporter=line` | 1 passed |
| Local browser smoke `http://127.0.0.1:3002/portfolio` | pass: proxied overview 200, asset-curve 200, no portfolio load error, `SK하이닉스`, visual cards, KPI tab switch, tooltip visible, console errors 0 |

## Watch

- Default symbol aliases should later be replaced or supplemented by KIS product-name lookup and user-maintained aliases.
- The asset curve still depends on available execution/portfolio history. The card now explains the current data, but richer time-weighted performance needs daily snapshot storage.
- Next production rewrites are build-time sensitive to `API_INTERNAL_URL`; local verification should rebuild with the intended API target or use the default 8000 API after it has been restarted with current code.
