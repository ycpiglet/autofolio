# Promotion Asset Preview Manifest

Status: local preview manifest only, not asset export
Owner: Marketing Growth
Last updated: 2026-06-20T01:12:59+09:00
Related tasks: TASK-095, TASK-132, TASK-133
Related taskset: TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION

This manifest previews source material for future landing/PDF/PPTX/SNS assets.
It does not generate final binary files, publish a public URL, upload to SNS,
contact customers, create CRM or payment records, handle secrets, or change
KIS/order/risk/prod/deploy surfaces.

## Sources

- `PROMOTION-ASSET-RENDERING-CONTRACT.json`
- `MARKETING-MATERIALS-V1.json`

The local gate recalculates source hashes before passing.

## Preview Targets

| Target | Source section | Review state | Export boundary |
|--------|----------------|--------------|-----------------|
| landing page source | `assets.landing_page` | draft | final/public export blocked |
| PDF one-pager source | `assets.pdf_one_pager` | draft | PDF binary export blocked |
| PPTX deck source | `assets.pptx_deck` | draft | PPTX binary export blocked |
| SNS text bundle source | `assets.sns_draft_bundle` | draft | posting/upload blocked |

## Landing Page Source Preview

- Headline: Run an auditable investing workflow with safety gates first.
- Subheadline: For selected users who want portfolio visibility, agent
  summaries, and explicit approvals while keeping their own account authority.
- Sections: Safety-first workflow; Portfolio context in one place; Verified
  membership.
- CTA: Request verified membership review.

## PDF One-pager Source Preview

1. What it is: a user-controlled investing workflow service for selected users.
2. Who it is for: people comfortable managing their own broker, LLM, SNS,
   approval, and risk boundaries.
3. What it emphasizes: safety guards, portfolio visibility, workflow records,
   agent summaries, and explicit approvals.
4. What it is not: an account-control service, public recommendation service,
   or hands-off account operator.
5. Next step: verified membership review.

## PPTX Deck Source Preview

| Slide | Draft |
|-------|-------|
| 1 | Autofolio |
| 2 | Problem: investor context is fragmented. |
| 3 | Approach: connect safety guards, portfolio visibility, agent summaries, explicit approvals, and records. |
| 4 | Pilot boundary: selected users, user-owned accounts and tokens, mock/paper-first checks, and human approval. |
| 5 | Review gates. |
| 6 | Next step: request verified membership review. |

## SNS Text Bundle Source Preview

- Owner blog draft source exists.
- X draft source exists.
- LinkedIn draft source exists.
- Naver blog draft source exists.
- All items are draft-only and must not be posted.

## Boundary

- `public_export_blocked=true`
- `final_export_blocked=true`
- `binary_export_blocked=true`
- `external_upload_blocked=true`
- `customer_contact_blocked=true`
- `crm_payment_blocked=true`
- `secret_material_blocked=true`

Owner approval and Compliance review are required before public use or final
export. QA/Doc Steward review is required before generated file export.

## Rollback

If claim review changes, delete local preview derivatives, archive this manifest
entry, and regenerate from the canonical source packet.

## Next Slice

The downstream claim-review / review-queue / owner-review chain is deferred to a
separate lane and is not part of this branch. Any such future work must not
approve public use, provide legal/tax/securities final advice, export final
assets, publish a public URL, upload to SNS, contact customers, or create
CRM/payment records.

## Verification

```powershell
python scripts/promotion_asset_preview_manifest_gate.py --check
python -m pytest tests/unit/test_promotion_asset_preview_manifest_gate.py -q
```
