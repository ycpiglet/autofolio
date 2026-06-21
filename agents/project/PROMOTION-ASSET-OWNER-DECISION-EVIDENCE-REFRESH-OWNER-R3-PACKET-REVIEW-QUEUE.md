# Promotion Asset Owner/R3 Packet Review Queue Contract

This packet review queue contract is local evidence for TASK-150. It is a review queue not approval. It is not actual owner approval, not actual owner signature, and not actual approval evidence.

## Scope

- Owner/R3: required before public use, final export, SNS upload, customer
  contact, CRM/payment setup, external account action, or legal/tax/securities
  reliance.
- No actual review submission, refresh execution, Owner approval record,
  signature collection, approval evidence collection, public publication,
  platform API call, OAuth flow, token handling, customer contact, payment
  action, or KIS/order/risk/prod/deploy change was performed.
- Source contract:
  `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-CANDIDATE-AUDIT-PREVIEW.json`.

## Review Queue Records

| Decision Type | Queue State | Owner/R3 | Public Use | Final Export |
|---|---|---|---|---|
| public_landing_use | queued_for_future_owner_r3_review | required | blocked | blocked |
| final_pdf_export | queued_for_future_owner_r3_review | required | blocked | blocked |
| final_pptx_export | queued_for_future_owner_r3_review | required | blocked | blocked |
| sns_upload | queued_for_future_owner_r3_review | required | blocked | blocked |
| customer_contact | queued_for_future_owner_r3_review | required | blocked | blocked |
| crm_payment_setup | queued_for_future_owner_r3_review | required | blocked | blocked |
| paid_ads | queued_for_future_owner_r3_review | required | blocked | blocked |
| external_account_action | queued_for_future_owner_r3_review | required | blocked | blocked |
| legal_tax_securities_reliance | queued_for_future_owner_r3_review | required | blocked | blocked |

## Queue State Records

The queue state records are local only:

- queue_drafted_local_only
- queued_for_future_owner_r3_review
- awaiting_owner_r3_inputs
- blocked_until_evidence_refresh
- archived_or_superseded
- future_owner_r3_decision_after_review

Every state keeps live action, Owner review submission, Owner approval,
signature, approval evidence, and action execution disabled.

## Queue Entry Preconditions

The queue entry preconditions require source hash match, packet candidate
coverage, evidence bundle reference coverage, Owner prompt coverage, blocker
preservation, and blocked action scan pass before any future Owner/R3 packet
review can be considered.

## Review Routing Records

Review routing records make Compliance Officer accountable and route QA, Doc
Steward, and Marketing Growth as reviewers. Owner/R3 remains the only final
authority for approval, signature, public use, publication, export, or
customer-facing action.

## Required Owner/R3 Input Map

The required owner/r3 input map lists the missing future inputs: refreshed
evidence if source coverage changes, explicit Owner/R3 decision, approval record,
signature if required, professional review clearance where applicable, and
archive/rollback decision for superseded candidates.

## Expiry Invalidating Trigger Map

The expiry invalidating trigger map keeps source hash changes, candidate
coverage changes, evidence reference changes, Owner prompt changes, blocker
changes, blocked action scan changes, external policy/platform changes, and
Owner/R3 boundary changes as invalidating events. These do not execute refresh
work; they only require a future local refresh/evidence cycle or Owner/R3
decision.

## Blocked Action Scan

The blocked action scan passes for actual refresh execution, actual Owner
approval record, Owner signature, approval evidence collection, public use,
final export, SNS upload, external action, customer contact, CRM/payment, secret
material, final advice, and KIS/order/risk/prod/deploy changes.

## Handoff

TASK-150 can close when the local gate and focused unit test pass. The next
no-Owner slice may define a local Owner/R3 packet review queue audit preview,
but it must still avoid actual review submission, approval, signature, approval
evidence collection, public use, final export, SNS upload, customer contact,
CRM/payment, external account action, secrets, OAuth, platform API calls, and
production changes.
