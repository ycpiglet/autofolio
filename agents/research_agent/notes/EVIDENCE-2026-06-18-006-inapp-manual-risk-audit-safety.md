---
type: evidence
id: EVIDENCE-2026-06-18-006
title: In-app manual risk acknowledgement and order audit safety
created_at: 2026-06-18T18:17:43+09:00
owner: QA
related_task: TASK-082
tags: [manuals, safety, audit, ui, order-flow, r3]
status: pass
redaction: no raw account number, token, secret, cash amount, full order id, or broker payload recorded
official_sources:
  - https://apiportal.koreainvestment.com/about-howto
  - https://apiportal.koreainvestment.com/apiservice
  - https://github.com/koreainvestment/open-trading-api
---

# In-app manual risk acknowledgement and order audit safety

## What Changed

Added:

- `docs/manuals/` manual asset set.
- `/api/manuals`, `/api/acknowledgements/status`, `/api/acknowledgements`.
- `/api/engine/health` and `/api/trade/audit-events`.
- `user_acknowledgements`, `order_intents`, `order_audit_events`, `engine_run_logs`.
- `/manuals` Next route, trade safety panel, history audit event table, settings safety summary.

Updated:

- `OrderFlow` records intent/audit events before and after broker submission.
- `LiveTradingEngine` records run health.
- `ConditionRequest` accepts actor/source metadata.
- Prod mode critical paths require live risk acknowledgement.

## Safety Contract

| Contract | State |
|----------|-------|
| No direct order endpoint added | pass |
| Order execution still goes through OrderFlow/SafetyChecker | pass |
| Intent idempotency blocks duplicate broker submission | pass |
| Live risk acknowledgement required for prod critical UI/API actions | pass |
| Owner-only manuals hidden from guest sessions | pass |
| Raw KIS secrets/account/cash/order payloads excluded | pass |
| TOTP enforcement not claimed | pass |

## Official Reference Notes

The KIS setup manual links to official KIS Developers sources. The official
portal describes Open API service application and app key/secret/token usage.
The official sample repository separates paper and prod key preparation and is
used only as setup guidance here. No live official API calls were made for this
task.

## Verification

| Command | Result |
|---------|--------|
| py_compile focused backend files | pass |
| `pytest tests\api\test_manuals_acknowledgements.py tests\unit\test_order_intent_audit.py tests\unit\test_services_shim.py -q` | 20 passed |
| `pytest tests\api\test_phase3_state.py tests\api\test_trade.py tests\api\test_trade_phase2.py tests\api\test_engine.py tests\unit\test_condition_toctou_cas.py tests\unit\test_engine_market_fallback.py tests\unit\test_order_flow_and_notification_failures.py -q` | 93 passed |
| `npm run lint` | pass |
| `npm run build` | pass, `/manuals` route generated |

## Watch

TOTP Authenticator is recommended and represented in UI/status, but real TOTP
enforcement is not implemented in this task. Treat it as a security-hardening
follow-up before unattended live automation.
