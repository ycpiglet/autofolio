---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-FRESHNESS-AUDIT-PREVIEW
work_uid: 7deddb97-f7cc-4079-9beb-d92cbba11c30
kind: taskset
parent_id: INIT-MARKETING-GROWTH
status: completed
owner: QA
created_at: 2026-06-20T02:38:25+09:00
updated_at: 2026-06-20T02:55:33+09:00
completed_at: 2026-06-20T02:55:33+09:00
resolution: done
verification_status: passed
origin_type: owner_goal_continuation
origin_ref: AUDIT-2026-06-20-020
created_by: lead_engineer
title: Marketing Asset Owner Decision Evidence Freshness Audit Preview
summary: Local no-Owner taskset for auditing the freshness contract and previewing stale-trigger readiness before any future Owner/R3 packet. It does not collect approval evidence, record approvals, publish assets, export final files, contact customers, activate CRM/payment, handle secrets, or perform external account actions.
tags: [marketing, compliance, claims, review, owner-decision-evidence, freshness, audit]
priority: P2
---

# TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-FRESHNESS-AUDIT-PREVIEW

## Parent Initiative

`INIT-MARKETING-GROWTH`

## Tasks

| work_id | Description | Owner | Status | Gate |
|---------|-------------|-------|--------|------|
| TASK-143 | Promotion Asset Owner Decision Evidence Freshness Audit Preview | QA | 완료 | local freshness audit/readiness preview only; no actual approval evidence collection |

## Sequence

```text
TASK-143
```

## Safety Boundary

Forbidden:

- actual Owner approval records, signatures, or approval evidence collection;
- public claim clearance, publication approval, or final asset approval;
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

- collecting or recording real Owner approval evidence;
- approving any freshness record, state, or future Owner/R3 packet for public use;
- customer messaging, CRM/payment/billing setup, paid ads, or live channel
  action;
- reliance on legal/tax/securities wording.

## Completion Criteria

- [x] TASK-143 is complete.
- [x] Local freshness audit/readiness preview exists as JSON/Markdown.
- [x] Preview summarizes freshness record coverage, stale-trigger map coverage,
  invalidating event coverage, state safety, and blocked action flags.
- [x] Gate rejects approval evidence collection, approval records, public approval,
  final export, external publication, customer contact, CRM/payment activation,
  secret/customer keys, final-advice fields, and live-action fields.
- [x] Generated task/report/work-item views are current after closure.

## Completion Record

Completed at: 2026-06-20T02:55:33+09:00

Result:

- `PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-FRESHNESS-AUDIT-PREVIEW.json` and `.md` audit the local freshness contract without collecting approval evidence or permitting action.
- The preview covers 9 freshness records, 5 freshness states, 8 refresh triggers, stale-trigger maps, invalidating events, archive/rollback coverage, and blocked action scans.
- `scripts/promotion_asset_owner_decision_evidence_freshness_audit_preview_gate.py` and focused tests validate source hash, record coverage, state safety, trigger coverage, invalidating event coverage, blocked action flags, forbidden key drift, and live-action drift.

Next:

- `TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-QUEUE` / `TASK-144` is registered for a local refresh queue contract only.
