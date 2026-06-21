---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-MARKETING-ASSET-OWNER-DECISION-QUEUE
work_uid: a5bd1fd1-9036-4958-9b2f-6b9563f27a41
kind: taskset
parent_id: INIT-MARKETING-GROWTH
status: completed
owner: Compliance Officer
created_at: 2026-06-20T01:12:59+09:00
updated_at: 2026-06-20T01:36:54+09:00
completed_at: 2026-06-20T01:36:54+09:00
resolution: done
verification_status: passed
origin_type: owner_goal_continuation
origin_ref: AUDIT-2026-06-20-010
created_by: lead_engineer
title: Marketing Asset Owner Decision Queue
summary: Local no-Owner taskset for defining how future Owner decisions for promotion assets are recorded and validated. It does not record actual approvals, publish assets, export final files, contact customers, activate CRM/payment, handle secrets, or perform external account actions.
tags: [marketing, compliance, claims, review, owner-decision-queue]
priority: P2
---

# TASKSET-MARKETING-ASSET-OWNER-DECISION-QUEUE

## Parent Initiative

`INIT-MARKETING-GROWTH`

## Tasks

| work_id | Description | Owner | Status | Gate |
|---------|-------------|-------|--------|------|
| TASK-138 | Promotion Asset Owner Decision Queue Contract | Compliance Officer | 완료 | local decision queue contract only; no actual approval recording |

## Sequence

```text
TASK-138
```

## Safety Boundary

Forbidden:

- actual Owner approval records or public claim clearance;
- legal, tax, securities, or regulatory final advice;
- final PDF/PPTX export or generated public asset output;
- public URL publication, SNS upload, paid ads, live publishing, OAuth, or
  platform API action;
- customer contact, customer/private data, CRM/customer records, payment
  requests, billing, support execution, or retention operations;
- external account action, secret/token handling, provider API call, or browser
  automation against a live channel;
- KIS/order/risk/prod/deploy changes.

Owner/R3 required:

- approving a specific claim or asset for public use;
- recording a real Owner approval that triggers export or publication;
- customer messaging, CRM/payment/billing setup, paid ads, or live channel
  action;
- reliance on legal/tax/securities wording.

## Completion Criteria

- [x] TASK-138 is complete.
- [x] Local decision queue contract exists as JSON/Markdown.
- [x] Contract defines allowed local states without recording actual approvals.
- [x] Gate rejects public approval, final export, external publication, customer
  contact, CRM/payment activation, secret/customer keys, final-advice fields,
  and live-action fields.
- [x] Generated task/report/work-item views are current after closure.

## Completion Record

Completed at: 2026-06-20T01:36:54+09:00

Result:

- `PROMOTION-ASSET-OWNER-DECISION-QUEUE-CONTRACT.json` and `.md` define a local queue contract for future Owner/R3 decisions.
- The contract lists required fields, allowed states, decision types, seed decision records, forbidden fields, forbidden outputs, and handoff boundaries without recording actual approval.
- `scripts/promotion_asset_owner_decision_queue_contract_gate.py` and focused tests validate source hash, decision coverage, blocked action flags, forbidden key drift, and live-action drift.

Next:

- `TASKSET-MARKETING-ASSET-OWNER-DECISION-AUDIT-PREVIEW` / `TASK-139` is registered for a local audit/readiness preview only.
