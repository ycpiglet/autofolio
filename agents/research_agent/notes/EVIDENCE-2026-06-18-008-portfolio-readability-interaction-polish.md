---
type: evidence
id: EVIDENCE-2026-06-18-008
title: Portfolio readability and interaction polish
created_at: 2026-06-18T21:53:43+09:00
owner: QA
related_task: TASK-084
tags: [portfolio, ui, readability, interaction, qa]
status: pass
redaction: no raw account number, token, secret, cash source payload, or broker order payload recorded
official_sources: []
---

# Portfolio readability and interaction polish

## What Changed

Added:

- Clickable portfolio KPI cards with detail breakdown.
- `?` hover/focus explanation hints for KPI and section headings.
- Portfolio-local PnL color rule: positive blue, negative red.
- Mail-like top mover lists with sort controls and full-list expansion.
- Opt-in holdings emphasis via `HoldingsTable.emphasizeValues`.

Updated:

- Portfolio titles use larger, bolder visual hierarchy.
- Portfolio numbers, symbols, and names are bolded.
- Holdings numeric cells use a consistent tabular monospace style when portfolio emphasis is enabled.
- UI spec records the portfolio readability/interaction rule.

## Safety Contract

| Contract | State |
|----------|-------|
| Portfolio tab only | pass |
| No live order executed | pass |
| No order/risk gate change | pass |
| No secret/account mutation | pass |
| No production DB apply | pass |
| Shared table change opt-in only | pass |

## Verification

| Command | Result |
|---------|--------|
| `npm run lint` | pass |
| `npm run build` | pass, `/portfolio` route generated |
| Local browser smoke on web 3002 | KPI detail, help tooltip, holdings, movers pass |
| `$env:E2E_PORT='3101'; npm run test:e2e -- e2e/demo-walkthrough.spec.ts --reporter=line` | 1 passed |

## Watch

The portfolio-local `+ blue / - red` rule intentionally differs from the global
KR PnL convention toggle. If this becomes product-wide policy later, move the
rule into the design token layer instead of duplicating it per page.
