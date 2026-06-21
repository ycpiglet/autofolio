# Sales/Revenue Lane Decision

Status: role deferred, not active
Owner: Business Planner
Last updated: 2026-06-19T23:32:08+09:00
Related tasks: TASK-093, TASK-095, TASK-096, TASK-097
Related taskset: TASKSET-MARKETING-GROWTH

This packet closes the current marketing-growth question about whether Sales/
Revenue should be a separate agent lane now.

Decision: do not create or activate a Sales/Revenue role yet.

## Reason

- Business Plan v1 has a selected subscription direction and low-price pilot
  hypothesis, but support/refund and exact customer-record operations are not
  decided.
- The current early-user flow is verified signup request and Owner-approved
  account activation, not outbound sales or broad paid conversion.
- Marketing Growth may keep drafting education, positioning, and campaign
  source material.
- Marketing Growth should not own pricing, customer contracting, payment
  collection, CRM, conversion pipeline operations, support handoff, or retention.
- Recommendation, paid signal, model portfolio, and personalized advice claims
  remain blocked until Compliance Officer and professional/regulator review.

## Current Ownership

Marketing Growth keeps:

- positioning;
- claim bank and banned-claim list;
- campaign briefs;
- landing copy draft source;
- PDF/PPTX source drafts;
- SNS draft bundles;
- support FAQ and disclaimer drafts;
- no-contact educational material.

Future Sales/Revenue may own, after activation:

- pricing packaging;
- lead qualification;
- demo request handling;
- CRM or customer-record workflow;
- conversion handoff;
- payment and receipt coordination;
- support and refund handoff;
- retention and renewal workflow.

## Activation Triggers

Sales/Revenue may be proposed again only after these inputs exist:

- Owner approves Sales/Revenue role activation.
- Support/refund policy is defined.
- Privacy and customer-record policy is defined.
- Payment collection and receipt policy is defined.
- CRM or no-CRM decision is defined.
- Compliance Officer sales-claim review is complete.
- Customer-contact workflow is Owner-approved.
- Business registration or admin posture is recorded for the paid offer.

## Boundary

This decision does not create a role, customer list, CRM account, payment flow,
outbound message, sales copy approval, paid ad, external account action, token,
or public sales campaign.

## Verification

```powershell
python scripts/sales_revenue_lane_decision_gate.py --check
python -m pytest tests/unit/test_sales_revenue_lane_decision_gate.py -q
```
