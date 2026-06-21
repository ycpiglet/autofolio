# Promotion Asset Claim Review Matrix

Status: local claim classification only, not public approval
Owner: Compliance Officer
Last updated: 2026-06-20T01:12:59+09:00
Related tasks: TASK-095, TASK-132, TASK-133, TASK-134
Related taskset: TASKSET-MARKETING-ASSET-CLAIM-REVIEW-FOUNDATION

This matrix classifies draft promotion claims from the local preview manifest.
It is not publication approval, legal advice, tax advice, securities advice,
final PDF/PPTX export, public URL publication, SNS upload, customer contact,
CRM/payment action, external account action, or secret handling.

## Sources

- `PROMOTION-ASSET-PREVIEW-MANIFEST.json`
- `MARKETING-MATERIALS-V1.json`
- `PROMOTION-ASSET-RENDERING-CONTRACT.json`

The local gate recalculates source hashes before passing.

## Boundary

- `public_use_blocked=true`
- `final_export_blocked=true`
- `publication_approval_blocked=true`
- `professional_review_required_before_reliance=true`
- `no_final_pdf_export=true`
- `no_final_pptx_export=true`
- `no_sns_upload=true`
- `no_customer_contact=true`
- `no_crm_or_payment_action=true`
- `no_secret_or_token_storage=true`

Owner approval and professional review are required before public use,
publication, customer contact, paid ads, final PDF/PPTX export, or reliance on
any financial, legal, tax, securities, KIS, recommendation, performance, or
regulated-service wording.

## Claim Buckets

| Bucket | Local disposition |
|--------|-------------------|
| allowed draft | Workflow, recordkeeping, explicit approval, visibility, verified membership, and mock/paper-first wording may remain in local drafts. |
| needs compliance review | Recommendation, user-owned LLM/SNS token integration, KIS, automated trading/live-readiness, and financial-service/regulatory wording require review. |
| Owner-only before public use | Pricing/paid pilot, public landing hero, PDF/PPTX export, SNS post, customer CTA/contact, and paid ads require Owner approval. |
| reject | Guarantees, risk-free or safe-return wording, hands-free wealth management, investment advice, paid signals, model portfolios, broker/asset-manager/robo-advisor identity, KIS commercial clearance, and AI winning-stock claims must not be used. |

## Preview Target Reviews

| Target | Classification | Public use | Final export | Publication approval |
|--------|----------------|------------|--------------|----------------------|
| landing page source | classified draft, not approved | blocked | blocked | blocked |
| PDF one-pager source | classified draft, not approved | blocked | blocked | blocked |
| PPTX deck source | classified draft, not approved | blocked | blocked | blocked |
| SNS text bundle source | classified draft, not approved | blocked | blocked | blocked |

## Handoff

- TASK-134 completed the local claim classification slice.
- TASK-135 completed the local review queue contract.
- TASK-136 completed a local audit preview from the review queue contract.
- TASK-137 may create a local Owner review packet.
- TASKSET-MARKETING-ASSET-CLAIM-REVIEW-FOUNDATION is complete.
- Public use, final PDF/PPTX export, public landing publication, SNS upload,
  customer contact, CRM/customer-record activation, payment or paid ad
  execution, and legal/tax/securities reliance remain Owner/R3.

## Verification

```powershell
python -m json.tool agents\project\PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.json
python scripts\promotion_asset_claim_review_matrix_gate.py --check
python -m pytest tests\unit\test_promotion_asset_claim_review_matrix_gate.py -q
```
