# Finance Accounting Roadmap

Status: local planning-support contract, not financial/accounting/tax advice.
Owner: Finance Accounting
Last updated: 2026-06-21T17:06:02+09:00
Related tasks: TASK-087, TASK-093, TASK-111, TASK-117, TASK-171, TASK-172

## Purpose

This roadmap defines the finance/accounting support lane for Autofolio. The lane
is broader than realized PnL tracking: it compares planned return, expected
outcome, portfolio gaps, payment/cash evidence posture, and operating readiness
so the Owner can decide what needs review next.

It does not recommend trades, execute orders, provide final accounting/tax
advice, request customer payments, or turn scenario output into guaranteed
returns.

## Planning Question

How should Autofolio answer questions like this without crossing advice or
execution boundaries?

> Initial expected return was 5 percent, but a current scenario suggests around
> 10 percent. What is missing, which allocation or profit-taking candidates need
> review, how should the portfolio roadmap change, and what timeline evidence is
> required?

That example is a required product scenario, not a statement about the current
portfolio. The lane must make the distinction explicit in every output.

## Scope

Allowed:

- plan-vs-expected comparison;
- gap matrix;
- scenario assumptions and confidence;
- data-quality watch list;
- cash/payment/receipt/refund/tax readiness watch list;
- Owner decision list;
- portfolio review candidates marked as candidates only;
- timeline candidates that name required evidence before any action.

Blocked:

- trade recommendation, order placement, profit-taking instruction, additional
  investment instruction, or rebalancing instruction;
- deposit/withdrawal instruction;
- customer payment request, receipt issuance, refund execution, or tax filing;
- bank, PG, Open Banking, KIS, broker, or production API action;
- raw statement, customer payment record, private identifier, secret, or token
  storage in repo files;
- public performance, profit, safety, or regulatory-clearance claim.

## Source Surface

| Source | Use |
|--------|-----|
| `BUSINESS-PLAN.md` | target product, pricing hypothesis, business milestones |
| `MEMBERSHIP-ACCESS-PLAN.md` | membership/payment operating context |
| `MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.md` | minimal payment evidence boundary |
| `MEMBERSHIP-PAYMENT-RECOGNITION-DECISION-PACKET.md` | payment recognition path and blocked upgrades |
| `app/api/routers/portfolio.py` | read-only portfolio overview source |
| `app/services/investor_profile.py` | risk tolerance and profile constraints |
| `SALES-HANDOFF-READINESS-CHECKLIST.md` | customer/payment/CRM boundaries |
| `FINANCE-SCENARIO-INPUT-CONTRACT.json` | synthetic plan-vs-expected fixture for TASK-173 |

## Contract

Every finance/accounting roadmap packet must separate:

| Bucket | Meaning |
|--------|---------|
| observed | values already available from read-only product surfaces |
| planned | Owner or business-plan targets |
| expected | scenario output with assumptions and confidence |
| missing | evidence required before action |
| blocked | action that remains Owner/R3/professional-review gated |

Required metrics:

- `planned_return_pct`
- `expected_return_range_pct`
- `gap_to_plan_pct_points`
- `allocation_drift`
- `cash_and_payment_readiness`
- `timeline_candidate`

Required outputs:

- scenario summary;
- portfolio review candidates;
- operations-support gaps;
- timeline plan.

## Roadmap

| Task | Purpose | Boundary |
|------|---------|----------|
| TASK-171 | Create this lane, role, packet contract, gate, and taskset | local planning support only |
| TASK-172 | Add a scenario input contract and sample fixture | complete; no real customer/payment data |
| TASK-173 | Add a read-only portfolio goal-gap model | no order path or trade advice |
| TASK-174 | Add a finance roadmap UI preview | no recommendation wording |

## TASK-172 Scenario Fixture

`FINANCE-SCENARIO-INPUT-CONTRACT.json` is the stable synthetic input for the
next read-model task. It fixes a 5.0 percent planned target, an 8.0 to 10.0
percent expected fixture range, the 3.0 to 5.0 percentage-point gap, required
missing evidence, candidate-only allocation/cash/timeline fields, and the
`TASK-173` handoff path.

The fixture is not a current portfolio fact and does not approve any trade,
payment, filing, external account, secret, production, or professional-advice
action.

## Review Model

- Finance Accounting owns plan-vs-expected framing and gap matrix.
- Business Planner checks business-plan alignment and pricing/pilot assumptions.
- Regulatory Admin checks payment, receipt, refund, tax, and filing boundaries.
- Compliance Officer checks return, recommendation, paid signal, and
  rebalancing language.
- QA verifies that local gates reject advice, secret, customer payment, and
  order-execution drift.
- Doc Steward keeps the taskset and source links fresh.
- Scribe may compress/archive noisy status detail only after Lead Engineer
  confirms canonical state.

## Verification

```powershell
python scripts\finance_accounting_roadmap_gate.py --check
python -m pytest tests\unit\test_finance_accounting_roadmap_gate.py -q
python scripts\finance_scenario_input_contract_gate.py --check
python -m pytest tests\unit\test_finance_scenario_input_contract_gate.py -q
```
