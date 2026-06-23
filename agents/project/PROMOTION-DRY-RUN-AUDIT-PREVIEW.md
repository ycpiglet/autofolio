# Promotion Dry-run Audit Preview

Status: local preview only, not publication approval
Owner: Backend Engineer
Last updated: 2026-06-19T23:22:07+09:00
Related tasks: TASK-095, TASK-096, TASK-129, TASK-130, TASK-131
Related taskset: TASKSET-MARKETING-GROWTH

This packet is the first local dry-run preview for the promotion publishing
pipeline. It creates no post, upload, OAuth flow, token, customer message, paid
ad, browser automation, or external account action.

## Preview

| Field | Value |
|-------|-------|
| campaign_id | MKT-2026-06-19-001 |
| channel_id | owner_blog_manual |
| state | dry_run_scheduled |
| source_artifact | agents/project/MARKETING-MATERIALS-V1.json |
| copy_surface | sns_private_post |
| planned_visibility | local_preview_only |
| scheduled_at | not_scheduled |
| live_action_blocked_by_default | true |

Preview text:

```text
Building Autofolio as a verified-membership investing workflow: safety guards first, then portfolio visibility, workflow, and live-readiness. Draft preview only.
```

## Source Hashes

- `MARKETING-MATERIALS-V1.json`
- `PROMOTION-CHANNEL-POLICY-MATRIX.json`
- `PROMOTION-PUBLISHING-POLICY-PACKET.json`
- `PROMOTION-PUBLISHING-STATE-MACHINE.json`

The local gate recalculates every source hash before passing.

## Boundary

- No live post.
- No external network call.
- No OAuth or token handling.
- No customer contact.
- No paid ad.
- No platform API upload.
- No generated public asset export.
- No KIS/order/risk/prod/deploy change.

## Verification

```powershell
python scripts/promotion_dry_run_audit_preview_gate.py --check
python -m pytest tests/unit/test_promotion_dry_run_audit_preview_gate.py -q
```
