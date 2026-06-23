---
title: Troubleshooting
description: Common KIS, scheduler, queue, and UI failure modes.
audience: owner
visibility: private
ui_section: troubleshooting
risk_level: high
requires_ack: false
order: 70
version: manuals-v1
---

# Troubleshooting

## KIS Timeout

Paper endpoints can be slower or unstable during busy market windows. Retry
read-only checks first. Do not move to prod execution if same-day paper evidence
is missing.

## Token Or Credential Error

Check app key, app secret, account number, product code, and environment name.
Do not paste raw values into logs or reports.

## Queue Or Scheduler Buildup

Symptoms:

- Many pending engine runs.
- `PROCESSING` conditions remain for several minutes.
- Actual run count exceeds expected schedule count.
- Duplicate idempotency keys appear.

Immediate action:

1. Activate kill switch.
2. Disable auto trading.
3. Inspect engine health.
4. Inspect order audit events.
5. Check broker open orders separately.

## Unknown Order Source

An order without `USER`, `AGENT`, or `SCHEDULER` source is not acceptable for
live automation. Treat it as an incident until classified.

## UI Looks Stale

Refresh the page, restart the local server if needed, and compare UI state with
API responses and broker read-only checks.
