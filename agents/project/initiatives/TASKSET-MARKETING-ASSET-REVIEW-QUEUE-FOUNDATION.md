---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-MARKETING-ASSET-REVIEW-QUEUE-FOUNDATION
work_uid: 78fff739-2703-48cb-98ab-72110daf5756
kind: taskset
parent_id: INIT-MARKETING-GROWTH
status: completed
owner: Compliance Officer
created_at: 2026-06-20T00:25:10+09:00
updated_at: 2026-06-20T00:40:56+09:00
completed_at: 2026-06-20T00:40:56+09:00
resolution: done
verification_status: passed
origin_type: owner_goal_continuation
origin_ref: AUDIT-2026-06-20-004
created_by: lead_engineer
title: Marketing Asset Review Queue Foundation
summary: Local no-Owner taskset for defining a review queue contract for draft promotional assets and claims. It does not approve publication, export final assets, contact customers, activate CRM/payment, handle secrets, or perform external account actions.
tags: [marketing, compliance, claims, review, queue, assets]
priority: P2
---

# TASKSET-MARKETING-ASSET-REVIEW-QUEUE-FOUNDATION

## Parent Initiative

`INIT-MARKETING-GROWTH`

## Tasks

| work_id | Description | Owner | Status | Gate |
|---------|-------------|-------|--------|------|
| TASK-135 | Promotion Asset Review Queue Contract | Compliance Officer | 완료 | local queue schema only; no publication approval |

## Sequence

```text
TASK-135
```

## Safety Boundary

Forbidden:

- publication approval or public claim clearance;
- legal, tax, securities, or regulatory final advice;
- final PDF/PPTX export or generated public asset output;
- public URL publication, SNS upload, paid ads, or live publishing;
- customer contact, customer/private data, CRM/customer records, payment
  requests, billing, support execution, or retention operations;
- external account action, OAuth, secret/token handling, provider API call, or
  browser automation against a live channel;
- KIS/order/risk/prod/deploy changes.

Owner/R3 required:

- public use of any claim or asset;
- final asset export or publication;
- professional reliance on legal/tax/securities wording;
- customer messaging, CRM/payment/billing setup, paid ads, or live channel
  action.

## Completion Criteria

- [x] TASK-135 is complete or explicitly deferred.
- [x] Review queue contract exists as local JSON/Markdown.
- [x] Gate rejects public approval, final export, external publication, customer
  contact, CRM/payment activation, secret/customer keys, and final-advice
  fields.
- [x] Generated task/report/work-item views are current.

## Completion Record

Completed at: 2026-06-20T00:40:56+09:00

Result:

- `PROMOTION-ASSET-REVIEW-QUEUE-CONTRACT.json` and `.md` define local queue
  states, item fields, required evidence, blockers, and rollback/archive notes.
- Gate and focused tests validate source hashes, queue field coverage,
  live-action state prohibition, target coverage, blocked public use, and
  forbidden key names.
- Public use, final legal/tax/securities reliance, final PDF/PPTX export,
  public landing publication, SNS upload, customer contact, CRM/payment, paid
  ads, external account action, secrets, platform API calls, OAuth, and
  KIS/order/risk/prod/deploy remain Owner/R3.
