# Promotion Asset Owner Decision Evidence Refresh Work-order Contract

This is a local refresh work-order contract for future Owner decision evidence
refresh work. It is not actual refresh execution, not actual Owner approval,
not actual approval evidence, and not publication approval.

## Source

- Source preview:
  `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-QUEUE-AUDIT-PREVIEW.json`
- Source hash:
  `8355516ca441dd9694ee2d7abf6eede784712bd66ed1eab57a05d937a0c5a44e`
- Related task: `TASK-146`

## Refresh Work-order Record Coverage

The contract covers all 9 refresh queue records from the source preview. Each
record is represented as a future local work order and keeps
`actual_refresh_executed=false`, `refresh_execution_allowed=false`,
`actual_approval_evidence_collected=false`, `actual_approval_recorded=false`,
and `action_permitted_now=false`.

## Work-order State Safety Scan

All 5 work-order states are local-only. They keep `live_action=false`,
`refresh_execution_allowed=false`, `actual_refresh_executed=false`,
`action_permitted_now=false`, `actual_approval_recorded=false`, and
`actual_approval_evidence_collected=false`.

## Preconditions And Proof Requirements

Every work-order record requires local preconditions before it can be reused:
the source preview hash must still match, the source queue record must still be
current local-only, and the blocked action scan must still pass.

Proof requirements are local evidence requirements only: local source hash
report, local queue record diff summary, and local blocked action scan result.
They are not actual approval evidence collection and do not record Owner
approval.

## Expiry Trigger Map

All 8 invalidating triggers from the source preview are mapped to blocked local
work-order states. Source hash changes, evidence-count changes, blocked-action
scan changes, forbidden-field changes, external policy/platform changes, and
Owner/R3 boundary changes do not permit refresh execution or public action.

## Blocked Action Scan

The blocked action scan keeps these actions blocked for every work order:

- actual refresh execution;
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

Owner/R3 is still required before any real refresh execution, approval record,
approval evidence collection, public claim use, final PDF/PPTX export, public
URL, SNS upload, customer contact, CRM/payment action, paid ad execution,
external account action, OAuth/platform API call, secret handling, or reliance
on legal, tax, or securities wording.
