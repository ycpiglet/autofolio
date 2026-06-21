# Promotion Asset Owner Decision Queue Contract

Status: local decision queue contract only, not actual Owner approval
Owner: Compliance Officer
Last updated: 2026-06-20T01:30:10+09:00
Related tasks: TASK-137, TASK-138
Related taskset: TASKSET-MARKETING-ASSET-OWNER-DECISION-QUEUE

This contract defines how future Owner decisions for promotion assets may be
represented as local queue records. It does not record actual Owner approval,
approve publication, provide legal/tax/securities final advice, export final
PDF/PPTX assets, publish URLs, upload to SNS, contact customers, create
CRM/payment records, handle secrets, call external platform APIs, or change
KIS/order/risk/prod/deploy surfaces.

## Source

- `PROMOTION-ASSET-OWNER-REVIEW-PACKET.json`

The local gate recalculates the source hash before passing.

## Decision Queue States

| State | Meaning | Live action | Actual approval |
|-------|---------|-------------|-----------------|
| pending local review | Local draft record exists. | false | false |
| evidence required | Required review evidence is missing. | false | false |
| Owner decision needed | Owner/R3 boundary is explicit. | false | false |
| approved record ready for future R3 | Contract state for a future approval record; no approval is recorded here. | false | false |
| rejected | Decision is rejected locally or by Owner later. | false | false |
| blocked | Required evidence or boundary failed. | false | false |
| withdrawn or archived | Record is no longer active. | false | false |

## Decision Types

| Decision type | Required before |
|---------------|-----------------|
| `public_landing_use` | Any public landing-page use |
| `final_pdf_export` | Final PDF generation or sharing |
| `final_pptx_export` | Final PPTX generation or use |
| `sns_upload` | Any SNS posting or upload |
| `customer_contact` | Email, DM, sales, support, or customer outreach |
| `crm_payment_setup` | CRM, customer records, payment, checkout, billing, receipt |
| `paid_ads` | Ads, retargeting, or budgeted campaign action |
| `external_account_action` | OAuth, platform API, browser automation, channel upload |
| `legal_tax_securities_reliance` | Any reliance on legal, tax, securities, or regulated-service wording |

## Blocked Action Flags

Every seed decision record keeps these blocked:

- `public_use_blocked=true`
- `final_export_blocked=true`
- `external_action_blocked=true`
- `customer_contact_blocked=true`
- `crm_payment_blocked=true`
- `secret_material_blocked=true`
- `final_advice_blocked=true`
- `kis_order_risk_prod_deploy_blocked=true`

## Boundary

This is not actual Owner approval. Actual approval records, public use, final
PDF/PPTX export, public landing publication, SNS upload, customer contact,
CRM/customer-record activation, payment or paid ad execution, external account
action, OAuth, platform API calls, and legal/tax/securities reliance remain
Owner/R3.

## Verification

```powershell
python -m json.tool agents\project\PROMOTION-ASSET-OWNER-DECISION-QUEUE-CONTRACT.json
python scripts\promotion_asset_owner_decision_queue_contract_gate.py --check
python -m pytest tests\unit\test_promotion_asset_owner_decision_queue_contract_gate.py -q
```
