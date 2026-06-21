# Promotion Asset Owner Decision Queue Audit Preview

Status: local audit/readiness preview only, not actual Owner approval
Owner: QA
Last updated: 2026-06-20T01:44:56+09:00
Related tasks: TASK-138, TASK-139
Related taskset: TASKSET-MARKETING-ASSET-OWNER-DECISION-AUDIT-PREVIEW

This preview summarizes the local Owner decision queue contract for
promotional assets. It does not record actual Owner approval, approve
publication, provide legal/tax/securities final advice, export final PDF/PPTX
assets, publish URLs, upload to SNS, contact customers, create CRM/payment
records, handle secrets, call external platform APIs, or change
KIS/order/risk/prod/deploy surfaces.

## Source

- `PROMOTION-ASSET-OWNER-DECISION-QUEUE-CONTRACT.json`

The local gate recalculates the source hash before passing.

## Summary

| Metric | Value |
|--------|-------|
| Decision records | 9 |
| Evidence required records | 7 |
| Owner decision needed records | 2 |
| Actual approval records | 0 |
| Public use blocked | 9/9 |
| Final export blocked | 9/9 |
| External action blocked | 9/9 |
| Customer contact blocked | 9/9 |
| CRM/payment blocked | 9/9 |
| Secret material blocked | 9/9 |
| Final advice blocked | 9/9 |
| KIS/order/risk/prod/deploy blocked | 9/9 |
| Live-action states | 0 |

## Decision Record Coverage

| Decision | State | Readiness | Audit |
|----------|-------|-----------|-------|
| public landing use | evidence required | evidence required before Owner/R3 | pass |
| final PDF export | evidence required | evidence required before Owner/R3 | pass |
| final PPTX export | evidence required | evidence required before Owner/R3 | pass |
| SNS upload | Owner decision needed | Owner/R3 required before action | pass |
| customer contact | evidence required | evidence required before Owner/R3 | pass |
| CRM/payment setup | evidence required | evidence required before Owner/R3 | pass |
| paid ads | evidence required | evidence required before Owner/R3 | pass |
| external account action | Owner decision needed | Owner/R3 required before action | pass |
| legal/tax/securities reliance | evidence required | evidence required before Owner/R3 | pass |

## Evidence Gap Scan

Each decision record has required evidence listed in the source contract, but
none of that evidence is an approval record. The preview keeps
`actual_approval_recorded=false` and `action_permitted_now=false` for every
decision type.

## Blocked Action Scan

- `actual_approval_record`: pass, blocked all.
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

TASK-139 completes this local audit/readiness preview only. `TASK-140` may
turn the evidence gaps into a local Owner decision evidence checklist contract.

Owner/R3 approval remains required before actual Owner approval records, public
use, final PDF/PPTX export, public landing publication, SNS upload, customer
contact, CRM/customer-record activation, payment or paid ad execution, external
account action, OAuth, platform API calls, or legal/tax/securities reliance.

## Verification

```powershell
python -m json.tool agents\project\PROMOTION-ASSET-OWNER-DECISION-QUEUE-AUDIT-PREVIEW.json
python scripts\promotion_asset_owner_decision_queue_audit_preview_gate.py --check
python -m pytest tests\unit\test_promotion_asset_owner_decision_queue_audit_preview_gate.py -q
```
