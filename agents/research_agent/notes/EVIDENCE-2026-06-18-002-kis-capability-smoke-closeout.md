---
type: evidence
id: EVIDENCE-2026-06-18-002
title: KIS capability smoke closeout
created_at: 2026-06-18T13:04:27+09:00
owner: QA
related_task: TASK-078
tags: [qa, kis, paper, prod-readonly, smoke]
status: pass
redaction: no raw KIS account number, token, secret, cash amount, or broker payload recorded
---

# KIS capability smoke closeout

## Request

Owner asked whether additional test results or improvements remain and whether
the KIS/KSI 기능 are broadly reflected and running well. Follow-up request was
to proceed with the remaining safe improvements and close out.

## Boundaries

- Production KIS was read-only only.
- Paper order lifecycle was allowed only against the KIS paper endpoint.
- No prod order, prod cancel/modify, prod auto-trading enablement, leverage,
  credit, derivatives, FX, overseas order, secret, account number, token body,
  cash amount, or raw broker payload was recorded.

## Work Performed

- Added `scripts/kis_capability_smoke.py`, a redacted one-command KIS read-only
  capability smoke for paper/prod.
- Added `--deep` coverage for slower optional read-only surfaces: KOSDAQ index,
  sector, disclosures, fundamentals, dividend, buying power shape, positions,
  cash shape, and 7-day order history.
- Tuned the smoke default to `request-timeout=10` and `max-retries=1` after a
  5-second paper endpoint timeout showed the mock server can be latency-sensitive.
- Strengthened `scripts/kis_paper_order_smoke.py` cancel confirmation by checking
  direct status plus same-ODNO today-orders open-like residue.
- Added focused regression tests for redaction, shape-only account summary,
  open-like order detection, ODNO normalization, and cancel confirmation.

## Live Results

| Area | Result | Evidence |
|------|--------|----------|
| KIS paper/prod core capability smoke | pass | `overall_status=pass`; paper and prod read-only token, current price, batch prices, intraday, history, KOSPI index, order book, account summary shape, and today orders passed |
| KIS paper/prod deep capability smoke | pass | `overall_status=pass`; deep read-only checks passed for paper and prod |
| Paper order lifecycle | pass | Paper endpoint guard active, account masked, below-market limit order accepted, cancel response returned canceled, `matching_rows=1`, `open_like=0`, `confirmed=True` |
| Prod asset-impacting boundary | pass | Capability smoke reports `order_actions=not-run` and `prod_boundary=read-only`; no prod order/cancel/modify/auto-trading was called |
| Redaction boundary | pass | Outputs record token length, counts, shapes, and booleans only; no token body/account/cash amount/raw payload recorded |

## Verification Commands

| Command | Result |
|---------|--------|
| `.venv\Scripts\python.exe -m pytest tests\unit\test_kis_paper_order_smoke.py tests\unit\test_kis_capability_smoke.py -q` | 10 passed |
| `.venv\Scripts\python.exe -m py_compile scripts\kis_capability_smoke.py scripts\kis_paper_order_smoke.py` | pass |
| `.venv\Scripts\python.exe scripts\kis_capability_smoke.py --env both --json --request-timeout 10 --max-retries 1` | pass |
| `.venv\Scripts\python.exe scripts\kis_capability_smoke.py --env both --deep --json --request-timeout 10 --max-retries 1` | pass |
| `.venv\Scripts\python.exe scripts\kis_paper_order_smoke.py --symbol 005930 --qty 1 --cancel-poll-attempts 3 --cancel-poll-sleep 1` | pass |

## Watch

- A stricter `request-timeout=5` run failed on several paper read-only calls
  before later passing with `request-timeout=10` and one retry. This looks like
  KIS paper endpoint latency rather than a missing feature, but future smoke
  runs should use the script defaults or higher during market-hour congestion.
- The paper cancel direct status can still lag as `PENDING` immediately after
  the cancel response. The strengthened confirmation treats the cancel as pass
  only when today-orders shows no open-like residue for the same ODNO.

## Changed Files

- `README.md`
- `scripts/kis_capability_smoke.py`
- `scripts/kis_paper_order_smoke.py`
- `tests/unit/test_kis_capability_smoke.py`
- `tests/unit/test_kis_paper_order_smoke.py`
- `agents/lead_engineer/tasks/TASK-078-kis-capability-smoke-closeout.md`
- `agents/research_agent/notes/EVIDENCE-2026-06-18-002-kis-capability-smoke-closeout.md`

## Result

TASK-078 passed. The broad KIS read-only surface is now repeatable through a
redacted smoke command, and the paper order cancel watch from TASK-075 is closed
with an explicit open-like residue confirmation.
