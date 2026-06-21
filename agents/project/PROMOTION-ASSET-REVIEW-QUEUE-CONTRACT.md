# Promotion Asset Review Queue Contract

Status: local review queue contract only, not public approval
Owner: Compliance Officer
Last updated: 2026-06-20T01:12:59+09:00
Related tasks: TASK-095, TASK-130, TASK-133, TASK-134, TASK-135
Related taskset: TASKSET-MARKETING-ASSET-REVIEW-QUEUE-FOUNDATION

This contract defines local review queue records for draft promotional asset
claims. It does not approve publication, provide legal/tax/securities final
advice, export final PDF/PPTX assets, publish URLs, upload to SNS, contact
customers, create CRM/payment records, handle secrets, call external platform
APIs, or change KIS/order/risk/prod/deploy surfaces.

## Sources

- `PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.json`
- `PROMOTION-ASSET-PREVIEW-MANIFEST.json`
- `PROMOTION-PUBLISHING-STATE-MACHINE.json`

The local gate recalculates source hashes before passing.

## Queue States

| State | Meaning | Live action |
|-------|---------|-------------|
| draft classified | Matrix classification exists but no public path is approved. | false |
| compliance review required | Compliance Officer must classify public claim risk. | false |
| owner review required | Owner/R3 approval is required before public use or export. | false |
| QA/Doc review required | Generated-file reproducibility and source traceability must be checked. | false |
| ready for future Owner review | Record-only state; still not approved for public use. | false |
| blocked | Item cannot proceed locally. | false |
| withdrawn or archived | Item is removed from active review. | false |

## Required Queue Record Fields

- `queue_item_id`
- `target_id`
- `source_asset_id`
- `source_artifact`
- `source_hash`
- `claim_bucket`
- `current_state`
- `assigned_role`
- `blockers`
- `required_evidence`
- `public_use_blocked`
- `final_export_blocked`
- `publication_approval_blocked`
- `rollback_or_archive_instruction`

## Boundary

- `public_use_blocked=true`
- `final_export_blocked=true`
- `publication_approval_blocked=true`
- `external_action_blocked=true`
- `customer_contact_blocked=true`
- `crm_payment_blocked=true`
- `secret_material_blocked=true`
- `no_final_pdf_export=true`
- `no_final_pptx_export=true`
- `no_sns_upload=true`
- `no_oauth_flow=true`
- `no_platform_api_call=true`

Owner approval and professional review are required before public use,
publication, customer contact, paid ads, final PDF/PPTX export, external
account action, or reliance on financial, legal, tax, securities, KIS,
recommendation, performance, or regulated-service wording.

## Queue Items

| Target | Current state | Assigned role | Public use | Final export |
|--------|---------------|---------------|------------|--------------|
| landing page source | compliance review required | Compliance Officer | blocked | blocked |
| PDF one-pager source | QA/Doc review required | QA | blocked | blocked |
| PPTX deck source | QA/Doc review required | Doc Steward | blocked | blocked |
| SNS text bundle source | Owner review required | Owner | blocked | blocked |

## Handoff

- TASK-135 completed the local review queue contract slice.
- TASK-136 completed the local review queue audit preview.
- TASK-137 may create a local Owner review packet.
- Public use, final PDF/PPTX export, public landing publication, SNS upload,
  customer contact, CRM/customer-record activation, payment or paid ad
  execution, external account action, and legal/tax/securities reliance remain
  Owner/R3.

## Verification

```powershell
python -m json.tool agents\project\PROMOTION-ASSET-REVIEW-QUEUE-CONTRACT.json
python scripts\promotion_asset_review_queue_contract_gate.py --check
python -m pytest tests\unit\test_promotion_asset_review_queue_contract_gate.py -q
```
