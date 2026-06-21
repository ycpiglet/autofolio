# Promotion Asset Owner Decision Evidence Refresh Work-order Audit Preview

Status: local audit/readiness preview only.

This artifact audits `PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT.json` before any future Owner/R3 packet. It is not actual refresh execution, not actual Owner approval, and not actual approval evidence collection.

## Source

| Item | Value |
|------|-------|
| Source contract | `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT.json` |
| Source hash | `9999163d895dffcde3fb5e734b7521f2b6d7705bcb6d5bcd11adeeb779f8f9ff` |
| Generated | `2026-06-20T04:08:29+09:00` |

## Refresh Work-order Record Coverage

| Metric | Count |
|--------|-------|
| Decision types | 9 |
| Source refresh work-order records | 9 |
| Local record summaries | 9 |
| Required evidence items | 25 |
| Stale evidence trigger items | 27 |
| Invalidating event items | 36 |
| Records blocked from execution | 9 |

Covered decision types:

- `public_landing_use`
- `final_pdf_export`
- `final_pptx_export`
- `sns_upload`
- `customer_contact`
- `crm_payment_setup`
- `paid_ads`
- `external_account_action`
- `legal_tax_securities_reliance`

## Work-order State Safety Scan

All five work-order states are local-only and blocked from live action:

- `work_order_drafted_local_only`
- `requires_source_refresh_before_owner_review`
- `blocked_until_refresh`
- `archived_or_superseded`
- `future_owner_r3_packet_candidate_after_refresh`

Each state keeps `live_action`, `refresh_execution_allowed`, `actual_refresh_executed`, `action_permitted_now`, `actual_approval_recorded`, and `actual_approval_evidence_collected` false. Owner/R3 remains required before action.

## Invalidating Trigger Map Coverage

All eight invalidating trigger map coverage entries are represented and remain blocked:

- `source_preview_hash_change`
- `checklist_item_coverage_change`
- `required_evidence_count_change`
- `stale_evidence_trigger_count_change`
- `blocked_action_scan_change`
- `forbidden_field_or_output_change`
- `external_policy_or_platform_rule_change`
- `owner_r3_boundary_change`

Each trigger preserves archive/rollback requirements and maps only to blocked local work-order states.

## Precondition/Proof/Expiry Coverage

Every work-order record retains three local preconditions, three proof requirements, four expiry triggers, source-hash invalidation, and archive/rollback coverage. These are readiness checks only; they do not collect real approval evidence.

## Blocked Action Scan

Blocked domains:

- actual refresh execution
- actual Owner approval record
- approval evidence collection
- public use
- final export
- SNS upload
- external account action
- customer contact
- CRM/payment
- secret material
- final advice
- KIS/order/risk/prod/deploy changes

## Owner/R3 Boundary

Owner/R3 is required before any actual evidence refresh execution, approval record, approval evidence collection, public use of a claim, final PDF/PPTX export, public landing deployment, SNS upload, customer contact, CRM/payment activation, paid ads, legal/tax/securities reliance, external account action, OAuth/platform API call, or secret/token handling.
