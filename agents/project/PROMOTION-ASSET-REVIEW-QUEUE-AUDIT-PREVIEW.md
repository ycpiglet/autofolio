# Promotion Asset Review Queue Audit Preview

Status: local audit preview only, not public approval
Owner: QA
Last updated: 2026-06-20T01:12:59+09:00
Related tasks: TASK-134, TASK-135, TASK-136
Related taskset: TASKSET-MARKETING-ASSET-REVIEW-AUDIT-PREVIEW

This preview summarizes the local review queue contract for promotional assets.
It does not approve publication, provide legal/tax/securities final advice,
export final PDF/PPTX assets, publish URLs, upload to SNS, contact customers,
create CRM/payment records, handle secrets, call external platform APIs, or
change KIS/order/risk/prod/deploy surfaces.

## Source

- `PROMOTION-ASSET-REVIEW-QUEUE-CONTRACT.json`

The local gate recalculates the source hash before passing.

## Summary

| Metric | Value |
|--------|-------|
| Queue items | 4 |
| Public use blocked | 4/4 |
| Final export blocked | 4/4 |
| Publication approval blocked | 4/4 |
| External action blocked | 4/4 |
| Customer contact blocked | 4/4 |
| CRM/payment blocked | 4/4 |
| Secret material blocked | 4/4 |
| Live-action states | 0 |

## Queue Item Status

| Target | State | Role | Audit |
|--------|-------|------|-------|
| landing page source | compliance review required | Compliance Officer | pass |
| PDF one-pager source | QA/Doc review required | QA | pass |
| PPTX deck source | QA/Doc review required | Doc Steward | pass |
| SNS text bundle source | Owner review required | Owner | pass |

## Blocked Action Scan

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

TASK-136 completed this local audit preview. `TASK-137` may package the same
evidence into a local Owner review packet.

Owner/R3 approval remains required before public use, final PDF/PPTX export,
public landing publication, SNS upload, customer contact, CRM/customer-record
activation, payment or paid ad execution, external account action, OAuth,
platform API calls, or legal/tax/securities reliance.

## Verification

```powershell
python -m json.tool agents\project\PROMOTION-ASSET-REVIEW-QUEUE-AUDIT-PREVIEW.json
python scripts\promotion_asset_review_queue_audit_preview_gate.py --check
python -m pytest tests\unit\test_promotion_asset_review_queue_audit_preview_gate.py -q
```
