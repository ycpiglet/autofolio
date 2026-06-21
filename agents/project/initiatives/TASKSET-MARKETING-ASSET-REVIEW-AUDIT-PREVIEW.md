---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-MARKETING-ASSET-REVIEW-AUDIT-PREVIEW
work_uid: 737408ab-d9f6-404e-b4ea-308f71229a72
kind: taskset
parent_id: INIT-MARKETING-GROWTH
status: completed
owner: QA
created_at: 2026-06-20T00:40:56+09:00
updated_at: 2026-06-20T00:54:44+09:00
completed_at: 2026-06-20T00:54:44+09:00
resolution: done
verification_status: passed
origin_type: owner_goal_continuation
origin_ref: AUDIT-2026-06-20-006
created_by: lead_engineer
title: Marketing Asset Review Audit Preview
summary: Local no-Owner taskset for generating an audit preview from the promotion asset review queue contract. It does not approve publication, export final assets, contact customers, activate CRM/payment, handle secrets, or perform external account actions.
tags: [marketing, compliance, claims, review, audit, preview]
priority: P2
---

# TASKSET-MARKETING-ASSET-REVIEW-AUDIT-PREVIEW

## Parent Initiative

`INIT-MARKETING-GROWTH`

## Tasks

| work_id | Description | Owner | Status | Gate |
|---------|-------------|-------|--------|------|
| TASK-136 | Promotion Asset Review Queue Audit Preview | QA | 완료 | local audit preview only; no publication approval |

## Sequence

```text
TASK-136
```

## Safety Boundary

Forbidden:

- publication approval or public claim clearance;
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

- public use of any claim or asset;
- final asset export or publication;
- professional reliance on legal/tax/securities wording;
- customer messaging, CRM/payment/billing setup, paid ads, or live channel
  action.

## Completion Criteria

- [x] TASK-136 is complete or explicitly deferred.
- [x] Audit preview exists as local JSON/Markdown.
- [x] Gate rejects public approval, final export, external publication, customer
  contact, CRM/payment activation, secret/customer keys, final-advice fields,
  and live-action fields.
- [x] Generated task/report/work-item views are current.

## Completion Record

Completed at: 2026-06-20T00:54:44+09:00

Result:

- `PROMOTION-ASSET-REVIEW-QUEUE-AUDIT-PREVIEW.json` and `.md` summarize the
  queue item states, assigned roles, blocker/evidence counts, and blocked
  public/export/live/customer/payment/secret/final-advice surfaces.
- Gate and focused tests validate source hash, queue item coverage, summary
  counts, blocked-action scan coverage, and forbidden key names.
- Public use, final legal/tax/securities reliance, final PDF/PPTX export,
  public landing publication, SNS upload, customer contact, CRM/payment, paid
  ads, external account action, secrets, platform API calls, OAuth, and
  KIS/order/risk/prod/deploy remain Owner/R3.
