---
title: Owner Operations Manual
description: Private operator runbook for live readiness and incident response.
audience: owner
visibility: private
ui_section: operations
risk_level: critical
requires_ack: false
order: 60
version: manuals-v1
---

# Owner Operations Manual

## Daily Preflight

1. Confirm market date and trading window.
2. Confirm `KIS_ENV`.
3. Confirm auto trading is OFF unless intentionally testing.
4. Confirm kill switch state.
5. Confirm engine health has no stale `PROCESSING` conditions.
6. Confirm recent audit events match expected orders.
7. Run paper checks before prod order tests.

## Live Trading Readiness

Live trading is ready only when these are all true:

- Paper order lifecycle passed today.
- Prod read-only checks passed.
- Risk acknowledgement is current.
- Order intent/audit events are visible.
- Queue and scheduler health are clean.
- There is a rollback path: turn auto trading OFF and activate kill switch.

## Incident Response

If unexpected orders, duplicated runs, queue growth, or stale conditions appear:

1. Activate kill switch.
2. Turn auto trading OFF.
3. Check KIS open orders in broker UI.
4. Check Autofolio history and audit events.
5. Record the incident before changing code.
6. Resume only after root cause is classified.
