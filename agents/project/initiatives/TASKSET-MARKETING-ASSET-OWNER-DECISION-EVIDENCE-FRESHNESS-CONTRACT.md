---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-FRESHNESS-CONTRACT
work_uid: 927914c5-f49e-4269-ba2f-9b6bb3c4190f
kind: taskset
parent_id: INIT-MARKETING-GROWTH
status: completed
owner: Doc Steward
created_at: 2026-06-20T02:22:06+09:00
updated_at: 2026-06-20T02:38:25+09:00
completed_at: 2026-06-20T02:38:25+09:00
resolution: done
verification_status: passed
origin_type: owner_goal_continuation
origin_ref: AUDIT-2026-06-20-018
created_by: lead_engineer
title: Marketing Asset Owner Decision Evidence Freshness Contract
summary: Local no-Owner taskset for converting stale-evidence trigger coverage into refresh rules and expiry states. It does not collect approval evidence, record approvals, publish assets, export final files, contact customers, activate CRM/payment, handle secrets, or perform external account actions.
tags: [marketing, compliance, claims, review, owner-decision-evidence, freshness]
priority: P2
---

# TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-FRESHNESS-CONTRACT

## Parent Initiative

`INIT-MARKETING-GROWTH`

## Tasks

| work_id | Description | Owner | Status | Gate |
|---------|-------------|-------|--------|------|
| TASK-142 | Promotion Asset Owner Decision Evidence Freshness Contract | Doc Steward | 완료 | local evidence freshness contract only; no actual approval evidence collection |

## Sequence

```text
TASK-142
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
- approving any decision record, checklist item, or freshness state for public use;
- customer messaging, CRM/payment/billing setup, paid ads, or live channel
  action;
- reliance on legal/tax/securities wording.

## Completion Criteria

- [x] TASK-142 is complete.
- [x] Local evidence freshness contract exists as JSON/Markdown.
- [x] Contract maps stale-evidence triggers to refresh states, expiry/invalidating
  events, accountable role, review role, and archive/rollback action.
- [x] Gate rejects approval evidence collection, approval records, public approval,
  final export, external publication, customer contact, CRM/payment activation,
  secret/customer keys, final-advice fields, and live-action fields.
- [x] Generated task/report/work-item views are current after closure.

## Completion Record

Completed at: 2026-06-20T02:38:25+09:00

Result:

- `PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-FRESHNESS-CONTRACT.json` and `.md` define local freshness states for all 9 Owner decision evidence surfaces.
- The contract maps stale trigger groups to refresh states, invalidating events, role ownership, and archive/rollback actions without collecting approval evidence or permitting action.
- `scripts/promotion_asset_owner_decision_evidence_freshness_contract_gate.py` and focused tests validate source hash, freshness state coverage, trigger map coverage, invalidating event coverage, blocked action flags, forbidden key drift, and live-action drift.

Next:

- `TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-FRESHNESS-AUDIT-PREVIEW` / `TASK-143` is registered for a local freshness audit/readiness preview only.
