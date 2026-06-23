# Promotion Channel Policy Matrix

Status: research packet, not publish-ready
Owner: Marketing Growth
Last updated: 2026-06-19T23:08:29+09:00
Related tasks: TASK-095, TASK-096, TASK-129
Related taskset: TASKSET-MARKETING-GROWTH

This packet completes the no-Owner channel-policy research slice for
`TASK-096`. It does not approve live publication, external account actions,
OAuth flows, paid ads, customer contact, or social platform API calls.

## Bottom Line

Autofolio can safely design a draft-first approval queue, but live posting must
stay blocked. X, LinkedIn, and Instagram may support future API publication only
after Owner-controlled account/app setup, current permission review, Compliance
Officer copy review, and an explicit Owner approval record. Naver Blog should be
manual-only because the official write API was terminated.

`PROMOTION-PUBLISHING-POLICY-PACKET.json` is the stricter TASK-096 handoff. It
adds Telegram, KakaoTalk, Naver Share/Cafe, and Google Business Profile as
policy-reviewed candidates while keeping every live/OAuth/token/customer action
blocked.

## Channel Matrix

| Channel | v1 Classification | Why | Rollback/Delete |
|---------|-------------------|-----|-----------------|
| Owner blog/dev log | Manual export candidate, not approved | Owner-controlled surface can be reviewed without external API integration. | Manual archive/remove plus local source hash and withdrawal note. |
| X | Future approval-queue candidate | Official API supports create/delete for authenticated users, but automation rules and user auth apply. | Delete authored posts through API only after approved live integration; keep local withdrawal note. |
| LinkedIn | Future approval-queue candidate | Posts API is versioned and permissions/page roles must be confirmed. | Delete through current Posts API where permitted; no batch-delete assumption. |
| Instagram | Defer live API publishing | Content publishing exists for supported account types, but account type, media requirements, permissions, and app review need a separate lane. | Confirm delete/withdrawal behavior by API version and media type before any live scheduling. |
| Naver Blog | Manual-only, auto posting unsupported | NAVER announced the login-based Blog Open API write function shutdown effective 2020-05-06. | Owner manual correction/deletion in Naver UI. |

## Required Queue Fields

- campaign_id
- channel
- copy_surface
- source_artifact
- source_hash
- claim_review_status
- compliance_reviewer
- owner_approval_required
- owner_approval_record
- dry_run_preview
- scheduled_at
- live_action_blocked_by_default
- external_post_id_after_live_only
- external_url_after_live_only
- rollback_or_delete_instruction

## Live Boundary

Before any future live post:

- refresh current official docs for the chosen channel;
- confirm platform account type and permission path;
- confirm deletion or correction path;
- run local prohibited-claim and prohibited-automation gates;
- record source hash and dry-run preview;
- obtain Owner approval for the exact channel and content;
- obtain Compliance Officer review for public financial, performance,
  recommendation, KIS, legal, tax, or regulatory wording.

## Next Safe Slices

1. `promotion_publish_state_machine_contract`: define approval states while
   live action remains disabled by default.
2. `promotion_dry_run_audit_preview`: generate local preview/audit records
   without network calls or token handling.
3. `channel_asset_rendering_requirements`: record per-channel copy/media
   constraints without final public export.

## Sources

- X Manage Posts: https://docs.x.com/x-api/posts/manage-tweets/introduction
- X authentication mapping: https://docs.x.com/fundamentals/authentication/guides/v2-authentication-mapping
- X automation rules: https://help.x.com/en/rules-and-policies/x-automation
- LinkedIn Posts API: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2026-06
- LinkedIn Community Management overview: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/community-management-overview?view=li-lms-2026-06
- LinkedIn Marketing API changes: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/recent-changes?view=li-lms-2026-05
- Instagram content publishing: https://developers.facebook.com/docs/instagram-platform/content-publishing/
- Instagram media publish reference: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media_publish/
- Instagram Platform changelog: https://developers.facebook.com/docs/instagram-platform/changelog/
- NAVER Blog Open API shutdown notice: https://developers.naver.com/notice/article/7527
- NAVER Blog share guide: https://developers.naver.com/docs/share/share/
- NAVER Blog search API: https://developers.naver.com/docs/serviceapi/search/blog/blog.md

## Verification

```powershell
python scripts/promotion_channel_policy_gate.py --check
python -m pytest tests/unit/test_promotion_channel_policy_gate.py -q
python scripts/promotion_publishing_policy_gate.py --check
python -m pytest tests/unit/test_promotion_publishing_policy_gate.py -q
```
