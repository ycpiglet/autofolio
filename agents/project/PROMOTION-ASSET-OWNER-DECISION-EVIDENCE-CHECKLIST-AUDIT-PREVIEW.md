# Promotion Asset Owner Decision Evidence Checklist Audit Preview

Status: local audit/readiness preview only, not actual Owner approval
Owner: QA
Last updated: 2026-06-20T02:16:20+09:00
Related tasks: TASK-140, TASK-141
Related taskset: TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-AUDIT-PREVIEW

This preview audits the local Owner decision evidence checklist contract. It is
not actual Owner approval and it is not actual approval evidence. It does not
collect approval evidence, record approval files, approve publication, provide
legal/tax/securities final advice, export final PDF/PPTX assets, publish URLs,
upload to SNS, contact customers, create CRM/payment records, handle secrets,
call external platform APIs, or change KIS/order/risk/prod/deploy surfaces.

## Source

- `PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST-CONTRACT.json`

The local gate recalculates the source hash before passing.

## Summary

| Metric | Value |
|--------|-------|
| Checklist items | 9 |
| Decision types | 9 |
| Required evidence entries | 25 |
| Acceptance criteria entries | 27 |
| Stale-evidence trigger entries | 27 |
| Forbidden field entries | 36 |
| Actual approval records | 0 |
| Actual approval evidence records | 0 |
| Approval evidence collection states | 0 |
| Public use blocked | 9/9 |
| Final export blocked | 9/9 |
| External action blocked | 9/9 |
| Customer contact blocked | 9/9 |
| CRM/payment blocked | 9/9 |
| Secret material blocked | 9/9 |
| Final advice blocked | 9/9 |
| KIS/order/risk/prod/deploy blocked | 9/9 |

## Checklist Coverage

| Decision type | Evidence | Stale triggers | Audit |
|---------------|----------|----------------|-------|
| public landing use | 2 | 3 | pass |
| final PDF export | 3 | 3 | pass |
| final PPTX export | 3 | 3 | pass |
| SNS upload | 3 | 3 | pass |
| customer contact | 3 | 3 | pass |
| CRM/payment setup | 3 | 3 | pass |
| paid ads | 3 | 3 | pass |
| external account action | 3 | 3 | pass |
| legal/tax/securities reliance | 2 | 3 | pass |

## Stale-Evidence Trigger Scan

Every checklist item includes stale-evidence triggers. The preview checks that
source hash changes, copy or claim changes, compliance changes, channel or
platform policy changes, customer/privacy/support/refund policy changes, and
business/admin posture changes have a local refresh path before future Owner/R3
review.

## Blocked Action Scan

- `actual_approval_record`: pass, blocked all.
- `approval_evidence_collection`: pass, blocked all.
- `public_use`: pass, blocked all.
- `final_export`: pass, blocked all.
- `sns_upload`: pass, blocked all.
- `external_action`: pass, blocked all.
- `customer_contact`: pass, blocked all.
- `crm_payment`: pass, blocked all.
- `secret_material`: pass, blocked all.
- `final_advice`: pass, blocked all.
- `kis_order_risk_prod_deploy`: pass, blocked all.

## Boundary

TASK-141 completes this local audit/readiness preview only. `TASK-142` may turn
the stale-evidence trigger coverage into a local evidence freshness contract.

Owner/R3 approval remains required before actual Owner approval records, actual
approval evidence collection, public use, final PDF/PPTX export, public landing
publication, SNS upload, customer contact, CRM/customer-record activation,
payment or paid ad execution, external account action, OAuth, platform API
calls, secret handling, or legal/tax/securities reliance.

## Verification

```powershell
python -m json.tool agents\project\PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST-AUDIT-PREVIEW.json
python scripts\promotion_asset_owner_decision_evidence_checklist_audit_preview_gate.py --check
python -m pytest tests\unit\test_promotion_asset_owner_decision_evidence_checklist_audit_preview_gate.py -q
```
