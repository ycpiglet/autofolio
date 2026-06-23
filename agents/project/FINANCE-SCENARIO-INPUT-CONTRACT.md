# Finance Scenario Input Contract

Status: local synthetic fixture, not financial/accounting/tax advice.
Owner: Finance Accounting
Last updated: 2026-06-21T17:06:02+09:00
Related tasks: TASK-171, TASK-172, TASK-173, TASK-174

## Purpose

This contract gives TASK-173 a stable local input for plan-vs-expected finance
planning. It turns the TASK-171 roadmap question into a deterministic fixture:
planned return is 5 percent and the synthetic expected range reaches around 10
percent.

The example is not a current portfolio fact. It is not a recommendation, order
instruction, final accounting/tax/legal/securities advice, customer payment
request, or production action.

## Required Buckets

Every scenario input must keep these buckets separate.

| Bucket | Use |
|--------|-----|
| observed | read-only snapshot references and diagnostics |
| planned | Owner or business-plan targets |
| expected | scenario range, assumptions, confidence, and freshness |
| missing | evidence required before any Owner decision |
| blocked | actions this lane cannot perform |

## Required Metrics

- `planned_return_pct`
- `expected_return_range_pct`
- `gap_to_plan_pct_points`
- `allocation_drift`
- `cash_and_payment_readiness`
- `timeline_candidate`

## Sample Fixture

`synthetic_plan_5_expected_around_10` is the canonical TASK-172 sample.

| Field | Value |
|-------|-------|
| synthetic | true |
| current portfolio fact | false |
| real customer/payment data | false |
| planned return | 5.0 percent |
| expected range | 8.0 to 10.0 percent |
| result | diagnostic gap only |

## Candidate Outputs

- Portfolio review candidates are Owner-review candidates only and must include
  `no_trade_instruction`.
- Timeline candidates require evidence and must keep `action_permitted_now`
  false.
- Cash/payment readiness is evidence posture only. It is not a customer payment,
  bank, PG, receipt, refund, or tax action.

## Handoff

TASK-173 may read `FINANCE-SCENARIO-INPUT-CONTRACT.json` as a stable fixture
source for a read-only derived model. TASK-173 must not add order paths, trade
recommendation wording, private payment data, customer records, secrets, KIS
order/risk/prod changes, or deployment changes.

## Verification

```powershell
python scripts\finance_scenario_input_contract_gate.py --check
python -m pytest tests\unit\test_finance_scenario_input_contract_gate.py -q
```
