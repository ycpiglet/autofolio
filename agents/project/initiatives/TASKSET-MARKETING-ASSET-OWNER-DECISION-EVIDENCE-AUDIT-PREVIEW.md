---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-AUDIT-PREVIEW
work_uid: 8321f057-8e14-4898-8d1e-577f823dab52
kind: taskset
parent_id: INIT-MARKETING-GROWTH
status: completed
owner: QA
created_at: 2026-06-20T02:06:08+09:00
updated_at: 2026-06-20T02:22:06+09:00
completed_at: 2026-06-20T02:22:06+09:00
resolution: done
verification_status: passed
origin_type: owner_goal_continuation
origin_ref: AUDIT-2026-06-20-016
created_by: lead_engineer
title: Marketing Asset Owner Decision Evidence Audit Preview
summary: Local no-Owner taskset for auditing the evidence checklist contract and previewing readiness/staleness gaps. It does not collect approval evidence, record approvals, publish assets, export final files, contact customers, activate CRM/payment, handle secrets, or perform external account actions.
tags: [marketing, compliance, claims, review, owner-decision-evidence, audit]
priority: P2
---

# TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-AUDIT-PREVIEW

## Parent Initiative

`INIT-MARKETING-GROWTH`

## Tasks

| work_id | Description | Owner | Status | Gate |
|---------|-------------|-------|--------|------|
| TASK-141 | Promotion Asset Owner Decision Evidence Checklist Audit Preview | QA | 완료 | local evidence checklist audit/readiness preview only; no actual approval evidence collection |

## Sequence

```text
TASK-141
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
- approving any decision record or checklist item for public use or final export;
- customer messaging, CRM/payment/billing setup, paid ads, or live channel
  action;
- reliance on legal/tax/securities wording.

## Completion Criteria

- [x] TASK-141 is complete.
- [x] Local evidence checklist audit/readiness preview exists as JSON/Markdown.
- [x] Preview summarizes checklist item coverage, evidence count alignment,
  stale-evidence trigger coverage, and blocked action flags.
- [x] Gate rejects approval evidence collection, public approval, final export,
  external publication, customer contact, CRM/payment activation,
  secret/customer keys, final-advice fields, and live-action fields.
- [x] Generated task/report/work-item views are current after closure.

## Completion Record

Completed at: 2026-06-20T02:22:06+09:00

Result:

- `PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST-AUDIT-PREVIEW.json` and `.md` summarize all 9 checklist items from the local evidence checklist contract.
- The preview records checklist coverage, evidence count alignment, stale-evidence trigger coverage, and blocked action scans without collecting approval evidence or permitting action.
- `scripts/promotion_asset_owner_decision_evidence_checklist_audit_preview_gate.py` and focused tests validate source hash, checklist coverage, evidence count alignment, stale trigger coverage, blocked action flags, forbidden key drift, and live-action drift.

Next:

- `TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-FRESHNESS-CONTRACT` / `TASK-142` is registered for a local evidence freshness contract only.
