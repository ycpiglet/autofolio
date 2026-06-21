# Promotion Asset Owner Review Packet

Status: local Owner review packet only, not public approval
Owner: Compliance Officer
Last updated: 2026-06-20T01:12:59+09:00
Related tasks: TASK-135, TASK-136, TASK-137
Related taskset: TASKSET-MARKETING-ASSET-OWNER-REVIEW-PACKET

This packet packages local promotion-asset review evidence for later Owner
review. It does not approve publication, provide legal/tax/securities final
advice, export final PDF/PPTX assets, publish URLs, upload to SNS, contact
customers, create CRM/payment records, handle secrets, call external platform
APIs, or change KIS/order/risk/prod/deploy surfaces.

## Source

- `PROMOTION-ASSET-REVIEW-QUEUE-AUDIT-PREVIEW.json`

The local gate recalculates the source hash before passing.

## Owner Decisions

| Decision | Current state |
|----------|---------------|
| Public landing use | Owner/R3 required |
| Final PDF export | Owner/R3 required |
| Final PPTX export | Owner/R3 required |
| SNS upload | Owner/R3 required |
| Customer contact | Owner/R3 required |
| CRM/payment setup | Owner/R3 required |
| Paid ads | Owner/R3 required |
| External account/OAuth/API action | Owner/R3 required |
| Legal/tax/securities reliance | Owner/R3 required |

No decision above is approved by this local packet.

## Review Items

| Target | Role | Owner decision | Public use | Final export |
|--------|------|----------------|------------|--------------|
| landing page source | Compliance Officer | required | blocked | blocked |
| PDF one-pager source | QA | required | blocked | blocked |
| PPTX deck source | Doc Steward | required | blocked | blocked |
| SNS text bundle source | Owner | required | blocked | blocked |

## Evidence Map

- `PROMOTION-ASSET-REVIEW-QUEUE-AUDIT-PREVIEW` records the local audit source
  and blocked action scan.
- `PROMOTION-ASSET-REVIEW-QUEUE-CONTRACT` remains the queue item source.
- `PROMOTION-ASSET-CLAIM-REVIEW-MATRIX` remains the claim classification source.
- `PROMOTION-CHANNEL-POLICY-MATRIX` is required before any SNS or channel
  action.
- Professional review is missing until the Owner supplies it outside the repo.

## Blocked Action List

- `public_use`: blocked; Owner/R3 required.
- `final_export`: blocked; Owner/R3 required.
- `sns_upload`: blocked; Owner/R3 required.
- `external_action`: blocked; Owner/R3 required.
- `customer_contact`: blocked; Owner/R3 required.
- `crm_payment`: blocked; Owner/R3 required.
- `secret_material`: blocked; Owner/R3 required.
- `final_advice`: blocked; Owner/R3 required.
- `kis_order_risk_prod_deploy`: blocked; Owner/R3 required.

## Boundary

This is not public approval. Public use, final PDF/PPTX export, public landing
publication, SNS upload, customer contact, CRM/customer-record activation,
payment or paid ad execution, external account action, OAuth, platform API
calls, and legal/tax/securities reliance remain Owner/R3.

## Verification

```powershell
python -m json.tool agents\project\PROMOTION-ASSET-OWNER-REVIEW-PACKET.json
python scripts\promotion_asset_owner_review_packet_gate.py --check
python -m pytest tests\unit\test_promotion_asset_owner_review_packet_gate.py -q
```
