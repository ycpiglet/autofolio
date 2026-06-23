---
type: evidence
id: EVIDENCE-2026-06-19-008
title: Promotion publishing channel policy research
created_at: 2026-06-19T23:00:13+09:00
owner: Research Agent
related_task: TASK-129
tags: [marketing, sns, publishing, external-api, official-sources]
status: pass
redaction: no tokens, account ids, channel ids, customer data, or external login recorded
---

# Promotion publishing channel policy research

## Question

Which promotion channels can Autofolio prepare for without Owner approval, and
which actions must remain Owner/R3 before any live publication?

## Sources Checked

Official and primary sources:

- Telegram Bot API: https://core.telegram.org/bots/api
- Telegram Bots FAQ: https://core.telegram.org/bots/faq
- X API introduction: https://docs.x.com/x-api/introduction
- X Create or Edit Post: https://docs.x.com/x-api/posts/create-post
- X API v2 authentication mapping: https://docs.x.com/fundamentals/authentication/guides/v2-authentication-mapping
- LinkedIn Share: https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin
- Google Business Profile local posts: https://developers.google.com/my-business/reference/rest/v4/accounts.locations.localPosts
- KakaoTalk Message REST API: https://developers.kakao.com/docs/ko/kakaotalk-message/rest-api
- Naver Share: https://developers.naver.com/docs/share/navershare/
- Naver Cafe write API: https://developers.naver.com/docs/login/cafe-api/cafe-api.md

## Findings

1. Telegram is the lowest-friction automation candidate for private or opt-in
   notices, but it is not a general public discovery feed. Bot setup requires
   BotFather, token handling, and rate-limit/broadcast review.

2. X supports programmatic post creation, but it is a public social API with
   pay-per-use pricing, OAuth user-token authorization, and tweet.write scope.
   Treat live X posting as Owner/R3.

3. LinkedIn sharing requires member OAuth and `w_member_social`, and the create
   flow posts to the UGC API. Treat live LinkedIn publishing as Owner/R3.

4. Naver Share is a web share helper for public URLs, not server-side Naver Blog
   auto-publishing. Naver Cafe writing is OAuth/cafe-specific and requires
   membership and community policy review.

5. KakaoTalk messaging is constrained to self or same-service/permissioned user
   messaging. It should not be modeled as a generic marketing broadcast path.

6. Google Business Profile local posts are tied to a business profile/location.
   Defer until business registration/profile setup is intentionally selected.

## Applied Repo Decision

- Keep `PROMOTION-CHANNEL-POLICY-MATRIX.json` and `.md` as the channel matrix.
- Add `PROMOTION-PUBLISHING-POLICY-PACKET.json` and `.md` as the stricter
  policy/dry-run handoff packet for TASK-096.
- Keep TASK-096 live publishing blocked.
- Allow only a future local dry-run audit preview generator as the next R2
  slice.
- Keep developer app creation, OAuth login, token handling, channel id handling,
  live post/schedule/edit/delete, paid ads, and customer messaging Owner/R3.
