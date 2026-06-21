# Promotion Publishing State Machine

Status: local contract, not live publish implementation
Owner: Marketing Growth
Last updated: 2026-06-19T23:08:29+09:00
Related tasks: TASK-096, TASK-129, TASK-130
Related taskset: TASKSET-MARKETING-GROWTH

This contract defines the local state model for a future promotion publishing
queue. It does not create a live publishing path. Every transition is local and
`live_action: false`.

Inputs:

- `PROMOTION-CHANNEL-POLICY-MATRIX.json`
- `PROMOTION-PUBLISHING-POLICY-PACKET.json`

## States

| State | Meaning | Live Action |
|-------|---------|-------------|
| draft_created | Marketing source exists but is not reviewed. | false |
| copy_review | Business/marketing alignment review. | false |
| compliance_review_required | Compliance Officer classification required before public use. | false |
| owner_review_required | Exact destination and final copy require Owner approval. | false |
| approved_for_manual_export | Manual export is allowed after approval, with no API call. | false |
| dry_run_scheduled | Local preview/audit record can be generated. | false |
| live_recorded_after_owner_action | Record-only state after Owner performs a live action outside automation. | false |
| blocked | Terminal blocked state. | false |
| withdrawn_or_archived | Terminal archive state. | false |

## Forbidden Transitions

- auto_publish
- skip_owner_approval
- skip_compliance_review
- schedule_live_without_owner_approval
- external_api_upload
- oauth_authorization
- token_storage
- customer_contact
- paid_ad_purchase
- browser_automation_publish
- lead_scraping
- bulk_dm
- viewbot_or_fake_engagement
- investment_advice_publication
- performance_guarantee_publication
- kis_commercial_clearance_publication

## Queue Record Contract

Required fields include campaign id, state, channel, copy surface, source
artifact, source hash, draft text, claim/compliance/Owner review fields, dry-run
preview, schedule timestamp, live-action blocked flag, after-live external
record fields, rollback/delete instruction, blocked reason, and append-only
audit events.

Forbidden fields include token, password, cookie, customer contact, bank account,
and KIS secret style fields.

## Invariants

- All transitions have `live_action: false`.
- `live_recorded_after_owner_action` is terminal and record-only.
- No transition performs OAuth, platform API upload, browser automation, paid
  ads, customer contact, or secret storage.
- Source hash is required before review.
- Compliance Officer review is required for public financial, recommendation,
  performance, KIS, tax, legal, or regulatory claims.
- Owner approval is required before manual export, destination dry-run, or any
  live record creation.
- Naver Blog remains manual-only and unsupported for auto posting.

## Verification

```powershell
python scripts/promotion_publishing_state_machine_gate.py --check
python -m pytest tests/unit/test_promotion_publishing_state_machine_gate.py -q
```
