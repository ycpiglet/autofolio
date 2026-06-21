# Promotion Asset Owner Decision Evidence Freshness Audit Preview

This is a local audit/readiness preview for the Owner decision evidence
freshness contract. It is not actual Owner approval, not actual approval evidence,
and not publication approval.

## Source

- Source contract:
  `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-FRESHNESS-CONTRACT.json`
- Source hash:
  `046299534ba38ebbf44960fda92909bdb17007e064791bb0bf57e77530caed43`
- Related task: `TASK-143`

## Freshness Record Coverage

The preview covers all 9 freshness records from the source contract. Each record
keeps `actual_approval_evidence_collected=false`,
`actual_approval_recorded=false`, and `action_permitted_now=false`.

## Stale-Trigger Map Coverage

Each record keeps 3 stale trigger mappings. The refresh map covers 8 trigger
types and routes them only to local refresh or expired states. No trigger grants
public use, final export, approval evidence collection, customer contact,
CRM/payment action, secret handling, platform API calls, or KIS/order/risk/prod
changes.

## Invalidating Event Scan

Every freshness record includes invalidating events, including
`source_preview_hash_change`, and every record includes an archive/rollback
instruction for stale local evidence.

## State Safety Scan

All 5 freshness states remain local-only. They keep `live_action=false`,
`action_permitted_now=false`, `actual_approval_recorded=false`, and
`actual_approval_evidence_collected=false`.

## Blocked Action Scan

The blocked action scan keeps these actions blocked for every record:

- actual approval record;
- approval evidence collection;
- public use;
- final export;
- SNS upload;
- external action;
- customer contact;
- CRM/payment;
- secret material;
- final advice;
- KIS/order/risk/prod/deploy.

## Owner/R3 Boundary

Owner/R3 is still required before any real approval record, approval evidence
collection, public claim use, final PDF/PPTX export, public URL, SNS upload,
customer contact, CRM/payment action, paid ad execution, external account
action, OAuth/platform API call, secret handling, or reliance on legal, tax, or
securities wording.
