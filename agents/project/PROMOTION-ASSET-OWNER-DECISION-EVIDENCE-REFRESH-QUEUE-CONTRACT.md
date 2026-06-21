# Promotion Asset Owner Decision Evidence Refresh Queue Contract

This is a local refresh queue contract for Owner decision evidence. It is not actual Owner approval, not actual approval evidence, and not publication approval.

## Source

- Source preview:
  `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-FRESHNESS-AUDIT-PREVIEW.json`
- Source hash:
  `063fb6492868e41548cb011d59743fb60b3bde1e84d2cb6a9d22b4fbd6a78a65`
- Related task: `TASK-144`

## Refresh Queue Record Coverage

The contract covers all 9 freshness records from the TASK-143 audit preview.
Each queue record keeps `actual_approval_evidence_collected=false`,
`actual_approval_recorded=false`, and `action_permitted_now=false`.

## Queue State Coverage

The contract keeps the 5 local queue states inherited from the source preview:
current local snapshot, refresh required before Owner review, expired/blocked,
archived or superseded, and future Owner/R3 packet candidate after refresh.
Every queue state keeps `live_action=false` and remains non-actionable.

## Invalidating Trigger Map

The invalidating trigger map covers all 8 source refresh triggers. Each trigger
routes only to local refresh or expired states and requires archive handling.
No trigger grants public use, final export, approval evidence collection,
customer contact, CRM/payment action, secret handling, platform API calls, or
KIS/order/risk/prod changes.

## Blocked Action Scan

The blocked action scan keeps these actions blocked for every queue record:

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
