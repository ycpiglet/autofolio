# Promotion Asset Rendering Contract

Status: local contract only, not asset export
Owner: Marketing Growth
Last updated: 2026-06-20T01:12:59+09:00
Related tasks: TASK-095, TASK-097, TASK-132, TASK-133
Related taskset: TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION

This contract prepares a future local asset-rendering workflow without creating
final PDF/PPTX files, public landing pages, SNS uploads, customer messages,
CRM/payment records, secrets, or external account actions.

## Sources

- `MARKETING-MATERIALS-V1.json`
- `MARKETING-BRIEF.md`
- `SALES-REVENUE-LANE-DECISION.json`

The local gate recalculates source hashes before passing.

## Render Targets

- landing page source preview;
- PDF one-pager source preview;
- PPTX deck source preview;
- SNS text bundle source preview.

Every target is `local_preview_source_only`, with final export disabled.

## Boundary

- No final PDF export.
- No final PPTX export.
- No binary asset generation.
- No public URL or upload.
- No SNS upload.
- No customer contact.
- No CRM or payment action.
- No secret or token storage.
- No KIS/order/risk/prod/deploy change.

## Follow-up Slice

`TASK-133` created local Markdown preview manifests from this contract. It did
not create final binary assets or public/exported materials. The downstream
claim-review / review-queue / owner-review chain is deferred to a separate lane
and is not part of this branch; it must never become public approval, final
asset export, or legal/tax/securities final advice.

## Verification

```powershell
python scripts/promotion_asset_rendering_contract_gate.py --check
python -m pytest tests/unit/test_promotion_asset_rendering_contract_gate.py -q
```
