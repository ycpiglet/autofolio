# Promotion Asset Owner Decision Evidence Freshness Contract

This is a local freshness contract for future Owner/R3 review packets. It is
not actual Owner approval, not actual approval evidence, and not publication
approval.

## Source

- Source preview:
  `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST-AUDIT-PREVIEW.json`
- Source hash:
  `28724706e9627f6a866ff63e8fe68a1a7b4b9327a0e4a9df71a49bb6d3e425e3`
- Related task: `TASK-142`

## Freshness Contract

The contract keeps nine Owner decision evidence surfaces in local-only
freshness states. The default state is `current_local_evidence_snapshot`.
Any stale signal moves the affected record to
`refresh_required_before_owner_review` or `expired_blocked_until_refresh`.

No state permits public use, final export, approval evidence collection,
customer contact, CRM/payment action, secret handling, platform API calls, or
KIS/order/risk/prod/deploy changes.

## Stale-Evidence Trigger Map

Each decision type carries three stale-evidence trigger groups:

- source or policy change;
- claim or asset content change;
- boundary or blocked-action change.

Those trigger groups map to refresh states only. They do not create an approval
record and do not collect approval evidence.

## Invalidating Events

Invalidating events include source preview hash changes, checklist coverage
changes, required evidence count changes, stale trigger count changes,
blocked-action scan changes, forbidden field/output changes, external policy or
platform rule changes, and Owner/R3 boundary changes.

When an invalidating event appears, stale local evidence must be archived or
regenerated before any future Owner/R3 packet can use it.

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
