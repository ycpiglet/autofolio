# Sales Handoff Readiness Checklist

Status: local checklist, not Sales/Revenue activation.
Owner: Business Planner
Created: 2026-06-20T11:20:58+09:00
Related task: TASK-170
Related taskset: TASKSET-MARKETING-TEAM-OPERATING-SYSTEM
Canonical JSON: `agents/project/SALES-HANDOFF-READINESS-CHECKLIST.json`

## Purpose

This checklist separates what Marketing Growth may keep doing from what belongs
to a future Sales/Revenue lane. It does not create or activate a Sales/Revenue
role, customer list, CRM, payment flow, billing setup, customer-contact process,
public sales claim, external account action, or provider/API integration.

## Activation Preconditions

Sales/Revenue remains inactive until all of these exist:

- Owner approves Sales/Revenue role activation.
- Support/refund policy is defined.
- Privacy and customer-record policy is defined.
- Payment collection and receipt policy is defined.
- CRM or no-CRM decision is defined.
- Compliance review for sales claims is complete.
- Customer-contact workflow is Owner-approved.
- Business registration or admin posture is recorded for the paid offer.

## Current Readiness

| Area | State | Blocks Activation |
|------|-------|-------------------|
| Pricing/package policy | internal hypothesis only | yes |
| Pilot intake flow | verified signup request draft only | yes |
| Support/refund policy | missing Owner decision | yes |
| Privacy/customer record policy | missing policy | yes |
| CRM/no-CRM decision | not defined | yes |
| Payment/receipt policy | manual Owner approval only | yes |
| Customer-contact workflow | not approved | yes |
| Compliance sales-claim review | required before paid/public sales claims | yes |
| Business/admin posture | not recorded for paid offer | yes |

## Ownership Split

Marketing Growth keeps:

- no-contact educational material;
- campaign backlog;
- landing draft source;
- FAQ and disclaimer drafts;
- SNS draft bundle;
- PDF/PPTX source text before final export.

Future Sales/Revenue may own only after activation:

- public pricing or package commitments;
- lead or demo intake;
- CRM/customer-record workflow;
- payment, receipt, billing, refund, or support handoff;
- retention and renewal workflow.

## Blocked Actions

Customer contact, CRM/customer records, payment requests, billing setup, public
sales claims, paid ads, OAuth, platform API calls, external account actions,
secrets, legal/tax/securities final advice, and KIS/order/risk/prod/deploy work
remain Owner/R3 boundaries.

## Next Handoff

- TASK-168: asset generator implementation readiness map.
- TASK-169: SNS publishing automation readiness backlog.

Recommended next no-Owner slice: TASK-168.

## Verification

```powershell
python -m json.tool agents\project\SALES-HANDOFF-READINESS-CHECKLIST.json
python -m py_compile scripts\sales_handoff_readiness_checklist_gate.py
python scripts\sales_handoff_readiness_checklist_gate.py --check
python -m pytest tests\unit\test_sales_handoff_readiness_checklist_gate.py -q
```
