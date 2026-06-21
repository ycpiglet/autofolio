# Promotion Asset Owner Decision Evidence Checklist Contract

Status: local evidence checklist contract only, not actual Owner approval
Owner: Doc Steward
Last updated: 2026-06-20T02:00:20+09:00
Related tasks: TASK-139, TASK-140
Related taskset: TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST

This contract turns the TASK-139 audit/readiness preview into a local checklist
for future Owner/R3 review. It is not actual Owner approval and it is not actual
approval evidence; in gate wording, it is not actual approval evidence. It does not collect signatures, record approval files,
approve publication, provide legal/tax/securities final advice, export final
PDF/PPTX assets, publish URLs, upload to SNS, contact customers, create
CRM/payment records, handle secrets, call external platform APIs, or change
KIS/order/risk/prod/deploy surfaces.

## Source

- `PROMOTION-ASSET-OWNER-DECISION-QUEUE-AUDIT-PREVIEW.json`

The local gate recalculates the source hash before passing.

## Summary

| Metric | Value |
|--------|-------|
| Decision types | 9 |
| Checklist items | 9 |
| Required evidence entries | 25 |
| Actual approval records | 0 |
| Actual approval evidence records | 0 |
| Public use approvals | 0 |
| Final export approvals | 0 |
| External action approvals | 0 |
| Customer contact approvals | 0 |
| CRM/payment approvals | 0 |
| Secret material records | 0 |
| Final advice records | 0 |

## Decision Type Evidence Map

| Decision type | Accountable role | Required evidence count | Review roles |
|---------------|------------------|-------------------------|--------------|
| public landing use | Compliance Officer | 2 | Compliance Officer, Doc Steward |
| final PDF export | QA | 3 | QA, Doc Steward, Compliance Officer |
| final PPTX export | Doc Steward | 3 | QA, Doc Steward, Compliance Officer |
| SNS upload | Marketing Growth | 3 | Marketing Growth, Compliance Officer, Owner |
| customer contact | Compliance Officer | 3 | Compliance Officer, Business Planner |
| CRM/payment setup | Business Planner | 3 | Business Planner, Compliance Officer, Doc Steward |
| paid ads | Marketing Growth | 3 | Marketing Growth, Compliance Officer, Owner |
| external account action | Doc Steward | 3 | Doc Steward, Compliance Officer, Owner |
| legal/tax/securities reliance | Compliance Officer | 2 | Compliance Officer |

## Acceptance Criteria

Each checklist item must include source preview id/hash, required evidence,
accountable role, review roles, acceptance criteria, stale-evidence triggers,
forbidden fields, blocked-action flags, and rollback/archive instruction.

The checklist can pass only when every item keeps
`actual_approval_evidence_collected=false`, `actual_approval_recorded=false`,
and `action_permitted_now=false`, with public use, final export, external
action, customer contact, CRM/payment, secret material, final advice, and
KIS/order/risk/prod/deploy all blocked.

## Stale-Evidence Triggers

Evidence becomes stale when source hashes change, copy or claim wording changes,
channel or platform policy changes, compliance posture changes, business/admin
or paid-offer posture changes, customer/privacy/support/refund policy changes,
or any Owner/R3 boundary changes.

## Forbidden Fields

The checklist rejects approval signatures, approval evidence files, Owner
signature files, access tokens, refresh tokens, client secrets, API secrets,
customer emails, customer phones, bank account numbers, public URLs, external
upload ids, final PDF/PPTX paths, customer record ids, payment request ids, and
legal/tax/securities final-advice fields.

## Boundary

TASK-140 completes a local checklist contract only. Owner/R3 approval remains
required before actual Owner approval records, actual approval evidence
collection, public use, final PDF/PPTX export, public landing publication, SNS
upload, customer contact, CRM/customer-record activation, payment or paid ad
execution, external account action, OAuth, platform API calls, secret handling,
or legal/tax/securities reliance.

## Verification

```powershell
python -m json.tool agents\project\PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST-CONTRACT.json
python scripts\promotion_asset_owner_decision_evidence_checklist_gate.py --check
python -m pytest tests\unit\test_promotion_asset_owner_decision_evidence_checklist_gate.py -q
```
