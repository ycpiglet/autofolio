---
title: Autofolio Manual Hub
description: Product manual asset registry for in-app help and operator workflows.
audience: all
visibility: public
ui_section: manuals
risk_level: low
requires_ack: false
order: 10
version: manuals-v1
---

# Autofolio Manual Hub

Autofolio manual files are product assets. The app renders these files in the
help/manual screen, and maintainers update the same files when product behavior
or safety rules change.

## Reading Order

1. `USER-GUIDE.md` - public product guide.
2. `KIS-CONNECTION-MANUAL.md` - Korea Investment Open API setup checklist.
3. `TRADING-MANUAL.md` - mock, paper, and minimal live trading workflows.
4. `SAFETY-AND-RISK.md` - risk warning, responsibility, and live-trading consent.
5. `OWNER-OPERATIONS-MANUAL.md` - private operator runbook.
6. `TROUBLESHOOTING.md` - failures, queue issues, scheduler drift, and recovery.

## Rules

- Do not put secrets, account numbers, raw order IDs, cash balances, or private
  payloads in these documents.
- Keep public user guidance separate from Owner-only operational procedures.
- Any screen that enables live trading must show the relevant risk manual and
  record an acknowledgement before execution.
