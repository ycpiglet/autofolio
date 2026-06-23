# Promotion Asset Generator Readiness Map

Status: local readiness map, not asset export
Owner: Doc Steward
Updated: 2026-06-20T11:57:37+09:00
Related task: TASK-168
Related taskset: TASKSET-MARKETING-TEAM-OPERATING-SYSTEM

This map prepares future promotion asset generation without creating a final
PDF, PPTX, landing page, SNS post, customer record, payment request, OAuth flow,
platform API call, secret, KIS/order/risk/prod/deploy change, or public
publication.

## Source Hashes

| Source | Path | Hash role |
|--------|------|-----------|
| Marketing Materials v1 | `agents/project/MARKETING-MATERIALS-V1.json` | canonical asset copy and section source |
| Campaign Backlog Calendar v1 | `agents/project/PROMOTION-CAMPAIGN-BACKLOG-CALENDAR-V1.json` | campaign backlog, target audience, calendar, and review queue source |
| Asset Rendering Contract | `agents/project/PROMOTION-ASSET-RENDERING-CONTRACT.json` | render target and blocked output contract |
| Asset Preview Manifest | `agents/project/PROMOTION-ASSET-PREVIEW-MANIFEST.json` | local preview surface and claim-review status source |
| Marketing Brief | `agents/project/MARKETING-BRIEF.md` | claim bank, marketing boundary, and taskset routing source |
| Promotion Channel Policy Matrix | `agents/project/PROMOTION-CHANNEL-POLICY-MATRIX.json` | channel policy, live action, OAuth, platform API, and rollback boundary source |

Hashes are canonical in `PROMOTION-ASSET-GENERATOR-READINESS-MAP.json`.
Hash drift means the map must be refreshed before generator implementation.

## Asset Surface Map

| Surface | Source section | Renderer candidate | Review gate | Output state |
|---------|----------------|--------------------|-------------|--------------|
| Landing page source | `assets.landing_page` | static landing source renderer | Marketing Growth, Compliance Officer, Owner/R3 before final or public use | `final_export_blocked=true`, `public_export_blocked=true` |
| PDF one-pager source | `assets.pdf_one_pager` | PDF source-to-preview renderer | Marketing Growth, Compliance Officer, Owner/R3 before final or public use | `final_export_blocked=true`, `public_export_blocked=true` |
| PPTX deck source | `assets.pptx_deck` | deck source-to-slide renderer | Marketing Growth, Compliance Officer, Owner/R3 before final or public use | `final_export_blocked=true`, `public_export_blocked=true` |
| SNS draft bundle source | `assets.sns_draft_bundle` | SNS caption bundle renderer | Marketing Growth, Compliance Officer, Owner/R3 before final or public use | `final_export_blocked=true`, `public_export_blocked=true` |
| SNS image caption source | `campaign_backlog.sns_draft_bundle` | SNS image caption source mapper | Marketing Growth, Compliance Officer, Owner/R3 before final or public use | `final_export_blocked=true`, `public_export_blocked=true` |

All surfaces are `local_source_or_preview_only`.

## Tooling Readiness

| Stage | Status | Boundary |
|-------|--------|----------|
| source_parse | ready for local parser design | local only |
| hash_manifest | ready | local only |
| template_mapping | partial ready, source mapping only | local only |
| preview_manifest | ready | local only |
| claim_review_link | ready | local only |
| export_blocker | ready | local only |
| rollback_manifest | ready for local manifest design | local only |

No stage enables external action, final export, binary export, public export,
OAuth, or platform API calls.

## Future Task Classification

| Candidate | Level | Owner needed before execution | Scope |
|-----------|-------|-------------------------------|-------|
| local_asset_source_parser | R2 | no | deterministic local source section parsing |
| local_preview_renderer_stub | R2 | no | local text/HTML preview source only |
| final_pdf_pptx_binary_export | R3 | yes | final PDF/PPTX binaries for external use |
| public_landing_or_sns_publication | R3 | yes | landing publication, SNS upload, or platform API posting |

## Blocked Outputs

- final PDF binary;
- final PPTX binary;
- public landing page deployment;
- SNS upload;
- customer email or direct message;
- paid ad creative upload;
- CRM lead or customer record;
- payment or checkout request;
- external URL publication;
- OAuth flow or platform API call;
- investment advice claim;
- paid signal claim;
- model portfolio claim;
- performance guarantee;
- KIS commercial clearance claim;
- secret or token material.

## Handoff

TASK-168 is complete. TASK-169 remains the next no-Owner local readiness slice
for SNS publishing automation. That next slice must still keep OAuth, platform
API calls, live posts, browser automation against social platforms, public
publication, customer contact, CRM/payment, secrets, and KIS/order/risk/prod/
deploy changes blocked.

## Validation

```powershell
python scripts/promotion_asset_generator_readiness_map_gate.py --check
python -m pytest tests/unit/test_promotion_asset_generator_readiness_map_gate.py -q
```
