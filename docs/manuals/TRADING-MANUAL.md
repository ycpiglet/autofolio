---
title: Trading Manual
description: Mock, paper, and minimal live trading procedures.
audience: owner
visibility: private
ui_section: trading
risk_level: high
requires_ack: false
order: 40
version: manuals-v1
---

# Trading Manual

Autofolio must progress in this order:

1. Mock read/write tests.
2. Paper read-only checks.
3. Paper order lifecycle.
4. Prod read-only checks.
5. Prod minimal live smoke.
6. Supervised automation only after explicit Owner approval.

## Mock

Mock mode is the default. Use it for UI, strategy, scheduling, queue, and audit
tests.

## Paper

Paper mode must pass token, balance, quote, order, cancel, transaction, and UI
sync checks before live tests.

Recommended commands:

- `python scripts/kis_capability_smoke.py --env paper --json`
- `python scripts/kis_paper_minimal_live_smoke.py --execute`

## Prod Minimal Smoke

Prod minimal smoke is not automatic. It requires same-day paper pass evidence
and an explicit live-order flag.

Recommended command:

- `python scripts/kis_prod_minimal_live_smoke.py --execute --i-understand-this-places-real-orders`

## Order Source Labels

Every order path must record one of these sources:

- `USER`: a person clicked or confirmed the action.
- `AGENT`: an agent produced the decision or proposal.
- `SCHEDULER`: a scheduled engine cycle submitted the order.

The UI must show the source before execution and the history screen must retain
the source after execution.
