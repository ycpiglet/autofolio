# Promotion Publishing Policy Packet

Status: policy foundation only, not publication approval
Updated: 2026-06-19T23:08:29+09:00
Owner: Marketing Growth
Related tasks: TASK-095, TASK-096, TASK-128, TASK-129
Related taskset: TASKSET-MARKETING-GROWTH

This packet turns `MARKETING-MATERIALS-V1` into a channel policy and approval
queue foundation. It does not post, schedule, upload, authenticate, store
tokens, contact users, buy ads, or approve public copy.

## Decision

Use this order for promotion work:

1. Draft source from `MARKETING-MATERIALS-V1`.
2. Local preview only.
3. Compliance review through `@compliance` or `@co` for any financial,
   recommendation, paid-signal, model-portfolio, tax, legal, regulatory,
   performance, or KIS wording.
4. Owner approval for exact channel, account, content hash, schedule, and
   rollback path.
5. Only then may a future task design a live publisher.

## Channel Summary

| Channel | Current mode | Rationale |
|---------|--------------|-----------|
| Owner blog/manual | manual export candidate | Lowest automation risk; Owner copy/paste only. |
| Telegram bot/channel | notification candidate, Owner-only | Good for opt-in or private notices, not discovery. |
| X API | public social API candidate, R3 | Requires app, OAuth user token, write scope, cost review. |
| LinkedIn Share | professional API candidate, R3 | Requires OAuth member auth and `w_member_social`. |
| Naver Share | manual share link candidate | Share helper for public URLs, not server-side blog publishing. |
| Naver Cafe Write | community API candidate, R3 | OAuth, cafe membership, board permission, community policy. |
| KakaoTalk Message | blocked for marketing broadcast | Constrained to self/same-service/permissioned messaging. |
| Google Business Profile | blocked until business profile ready | Requires business/location context and Owner setup. |

## Required Owner/R3 Steps

- Channel account selection.
- Developer app creation.
- OAuth login or callback validation.
- Token, channel id, account id, or app secret handling.
- Live post, schedule, edit, delete, or API upload.
- Paid ad/billing setup.
- Customer messaging.

## Dry-Run Contract

A future local dry-run may generate only an audit preview with:

- `campaign_id`
- `channel_id`
- `source_hash`
- `claim_review_status`
- `owner_approval_status`
- `planned_visibility`
- `scheduled_at`
- `rollback_instruction`
- `blocked_reason`

It must not make network calls or mutate external accounts.

## Official Sources

- Telegram Bot API: https://core.telegram.org/bots/api
- Telegram Bots FAQ: https://core.telegram.org/bots/faq
- X API introduction: https://docs.x.com/x-api/introduction
- X Create or Edit Post: https://docs.x.com/x-api/posts/create-post
- X v2 authentication mapping: https://docs.x.com/fundamentals/authentication/guides/v2-authentication-mapping
- LinkedIn Share: https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin
- Google Business Profile local posts: https://developers.google.com/my-business/reference/rest/v4/accounts.locations.localPosts
- KakaoTalk Message REST API: https://developers.kakao.com/docs/ko/kakaotalk-message/rest-api
- Naver Share: https://developers.naver.com/docs/share/navershare/
- Naver Cafe write API: https://developers.naver.com/docs/login/cafe-api/cafe-api.md

## Validation

```powershell
python scripts/promotion_publishing_policy_gate.py --check
python -m pytest tests/unit/test_promotion_publishing_policy_gate.py -q
```
