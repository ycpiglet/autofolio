---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT
work_uid: 9c6ed16d-b308-4a45-ae25-763f93a24fb4
kind: taskset
parent_id: INIT-MARKETING-GROWTH
status: completed
owner: Doc Steward
created_at: 2026-06-20T03:34:53+09:00
updated_at: 2026-06-20T03:56:06+09:00
completed_at: 2026-06-20T03:56:06+09:00
resolution: done
verification_status: passed
origin_type: owner_goal_continuation
origin_ref: AUDIT-2026-06-20-026
created_by: lead_engineer
title: Marketing Asset Owner Decision Evidence Refresh Work-order Contract
summary: Local no-Owner taskset for defining future evidence refresh work orders from the refresh queue audit preview. It does not execute refresh work, collect approval evidence, record approvals, approve public use, publish assets, export final files, contact customers, activate CRM/payment, handle secrets, call platform APIs, or perform external account actions.
tags: [marketing, compliance, claims, review, owner-decision-evidence, freshness, refresh-queue, work-order]
priority: P2
---

# TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT

## Parent Initiative

`INIT-MARKETING-GROWTH`

## Tasks

| work_id | Description | Owner | Status | Gate |
|---------|-------------|-------|--------|------|
| TASK-146 | Promotion Asset Owner Decision Evidence Refresh Work-order Contract | Doc Steward | 완료 | local refresh work-order contract only; no actual evidence refresh execution or approval evidence collection |

## Sequence

```text
TASK-146
```

## Safety Boundary

Forbidden:

- actual Owner approval records, signatures, or approval evidence collection;
- actual evidence refresh execution or external-source collection;
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

- executing any real refresh work that touches external accounts, private data,
  customer data, paid services, or professional/legal/tax/securities reliance;
- collecting or recording real Owner approval evidence;
- approving any work order, refresh queue audit item, refresh queue record, or
  future Owner/R3 packet for public use;
- customer messaging, CRM/payment/billing setup, paid ads, or live channel
  action;
- reliance on legal/tax/securities wording.

## Completion Criteria

- TASK-146 is complete or explicitly deferred.
- Local refresh work-order contract exists as JSON/Markdown.
- Contract maps the 9 refresh queue records to future local work orders,
  accountable/review roles, preconditions, proof requirements, expiry triggers,
  and blocked action flags.
- Gate rejects actual refresh execution, approval evidence collection, approval
  records, public approval, final export, external publication, customer
  contact, CRM/payment activation, secret/customer keys, final-advice fields,
  and live-action fields.
- Generated task/report/work-item views are current.

## Completion Record

- Completed at: 2026-06-20T03:56:06+09:00
- Completed task: `TASK-146`
- Evidence:
  - `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT.json`
  - `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT.md`
  - `scripts/promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py`
  - `tests/unit/test_promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py`
- Verification:
  - `python -m json.tool agents\project\PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT.json`
  - `python scripts\promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py --check`
  - `python -m pytest tests\unit\test_promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py -q`
  - `python -m py_compile scripts\promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py`
  - `python scripts\promotion_asset_owner_decision_evidence_refresh_queue_audit_preview_gate.py --check`

## Next Local Slice

- `TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-AUDIT-PREVIEW`
- `TASK-147`
