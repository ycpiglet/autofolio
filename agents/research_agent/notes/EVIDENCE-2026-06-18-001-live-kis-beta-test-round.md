---
type: evidence
id: EVIDENCE-2026-06-18-001
title: Live KIS beta test round
created_at: 2026-06-18T10:29:10+09:00
owner: QA
related_task: TASK-075
tags: [qa, beta, kis, paper, prod-readonly, ui, market-hours]
status: pass
redaction: no raw KIS account number, token, secret, or cash balance recorded
---

# Live KIS beta test round

## Request

Owner requested a regular-session KIS/KSI beta-style verification round:
many test cases and edge cases, paper account first, production account only
for safe/no-asset-impact functions, and no leverage.

## Boundaries

- Paper KIS order tests were allowed by the Owner request.
- Production KIS was read-only only.
- Excluded from production: order placement, cancel/modify, overseas order,
  auto-trading enablement, leverage, credit, derivatives, FX, and any asset-
  impacting action.
- No raw account number, token, secret, or cash balance is recorded here.

## KIS Results

| Area | Result | Evidence |
|------|--------|----------|
| Paper token | pass | token acquired; token body not recorded |
| Prod token | pass | token acquired; token body not recorded |
| Paper read-only | pass | 17/17 checks passed: price, batch price, intraday, history, index, sector, order book, disclosures, fundamentals, dividend, buying power, positions, redacted cash/account summary, today orders, 7-day order history |
| Prod read-only | pass | 16/16 checks passed across the same non-mutating surfaces; positions/order counts only recorded |
| Paper order lifecycle | pass/watch | below-market limit buy accepted, cancel response returned canceled, post-check open-like count was 0; direct status reread still showed pending |
| Paper transaction soak | pass | market buy/sell and two limit-cancel cases completed; post open-like count 0 |
| Paper transaction analysis | pass | paper-only true, KIS available true, UI order/fill readers true, no open-like orders |
| Paper engine dry-run | pass | processed 2, executed 0, kill switch blocked both |
| Paper engine once | pass | processed 2, executed 0, no live asset-impacting action triggered |
| Paper WebSocket | pass | current price/order-book read-only subscription returned system, quote, and trade events |

## Regression Results

| Command | Result |
|---------|--------|
| `.venv\Scripts\python.exe -m pytest tests/unit/test_kis_client.py tests/unit/test_kis_client_cash.py tests/unit/test_kis_auth_cache.py tests/unit/test_kis_buying_power.py tests/unit/test_kis_failure_modes.py tests/unit/test_kis_client_failure_modes.py tests/unit/test_kis_r3_order_paths.py tests/unit/test_kis_paper_order_smoke.py tests/unit/test_kis_paper_transaction_soak.py tests/unit/test_kis_paper_transaction_loop.py tests/unit/test_kis_paper_hold_basket.py tests/unit/test_reconcile_paper_fills.py -q` | 83 passed |
| `.venv\Scripts\python.exe -m pytest tests/api/test_health.py tests/api/test_portfolio.py tests/api/test_trade.py tests/api/test_trade_phase2.py tests/api/test_engine.py tests/api/test_analysis.py tests/api/test_profile_survey.py tests/api/test_auth.py tests/api/test_auth_sso.py tests/api/test_account.py -q` | 124 passed, 11 warnings |
| `.venv\Scripts\python.exe -m pytest tests/integration/test_paper_scenario_matrix.py tests/integration/test_quant_trading_scenario_catalog.py tests/integration/test_order_lifecycle.py tests/integration/test_portfolio_reality_model.py tests/integration/test_engine_e2e.py -q --durations=10` | 138 passed, 1 Windows temp SQLite cleanup warning |
| `npm run lint` | pass |
| `npm run build` | pass |
| `npm run test:e2e -- e2e/login.spec.ts e2e/demo-walkthrough.spec.ts e2e/dashboard.spec.ts e2e/settings-account.spec.ts e2e/investor-profile.spec.ts e2e/phase3.spec.ts e2e/phase4.spec.ts e2e/analysis.spec.ts --reporter=line` | 42 passed |

## Live UI Results

Local stack:

- FastAPI: `http://127.0.0.1:8000/api/health` returned ok.
- Next production server: `http://127.0.0.1:3000/login` returned 200.

Live browser probe against the real local API:

| Case | Result |
|------|--------|
| Unknown local owner login | rejected with 401 and inline error |
| Guest login | reached `/home` |
| SSO provider shells | 4 buttons visible: Google, Kakao, Naver, Mock SSO |
| Desktop primary pages | `/home`, `/portfolio`, `/trade`, `/history`, `/analysis`, `/agents`, `/alerts`, `/settings` all showed expected visible text |
| Mobile guest flow | guest reached `/home`; navigation text visible |

## Findings And Fixes

| ID | State | Finding | Action |
|----|-------|---------|--------|
| F-075-001 | fixed | Unknown local username/password created an owner session during live beta probing. | `login_or_register` now fails closed by default; first-run auto-registration requires `AUTOFOLIO_LOCAL_AUTO_REGISTER=1`. Added API/service regression tests. |
| F-075-002 | fixed | Paper order/engine scripts printed the raw KIS account number in console output. | Script output now masks account/product code. Added unit regression for masking. |
| F-075-003 | watch | `kis_paper_order_smoke.py` cancel response was canceled, and open-like count became 0, but immediate status reread still showed pending. | Treat KIS direct status reread after cancel as eventually consistent; keep post-cancel open-like check in future paper order verification. |
| F-075-004 | watch | Next `dev` server probe served HTML/chunks but did not hydrate reliably in headless live probing, with HMR WebSocket 404/invalid response noise. | Switched final local UI verification to `npm run start` production server after successful build; production live probe passed. |
| F-075-005 | watch | Integration test run passed but emitted a Windows temp SQLite cleanup warning. | No behavior failure observed; keep as platform cleanup warning. |

## Changed Files

- `app/services/auth_service.py`
- `app/services/__init__.py`
- `app/ui/auth.py`
- `docs/UI_SPEC.md`
- `scripts/kis_paper_order_smoke.py`
- `scripts/run_paper_engine.py`
- `tests/api/test_auth.py`
- `tests/api/test_account.py`
- `tests/unit/test_kis_paper_order_smoke.py`
- `web/e2e/demo-walkthrough.spec.ts`
- TASK/STATUS/AUDIT/report/index/generated record files

## Result

TASK-075 passed with fixes. Paper KIS order paths were exercised only in the
paper environment. Production KIS was exercised only through read-only,
no-asset-impact paths. No leverage or prod order route was used.
