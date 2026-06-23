---
type: task
id: TASK-129
display_id: TASK-129
task_uid: 6203af88-51f1-4e82-9aed-3b80ca8d97b5
registered_at: 2026-06-19T22:58:13+09:00
created_at: 2026-06-19T22:58:13+09:00
updated_at: 2026-06-19T23:08:29+09:00
started_at: 2026-06-19T22:58:13+09:00
completed_at: 2026-06-19T22:58:13+09:00
status: 완료
owner: Marketing Growth
assignees: [Marketing Growth, Research Agent, Compliance Officer, QA, Doc Steward]
priority: Medium
difficulty: 중
est_hours: 2
actual_hours: 1
est_tokens: 30000
actual_tokens: 18000
tags: [marketing, sns, external-api, publishing, policy, research]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-GROWTH
gate: no live post, no OAuth, no external account action, no token handling, no customer contact, no paid ads
trigger_meeting: Owner goal continuation 2026-06-19
audit_log: AUDIT-2026-06-19-041
created: 2026-06-19
---

# TASK-129 Promotion Channel Policy Matrix

작업 ID: TASK-129
상태: 완료
Owner: Marketing Growth
요청 시각: 2026-06-19T22:58:13+09:00
기록 시각: 2026-06-19T23:08:29+09:00
요청자: Owner goal continuation
수행자: Marketing Growth, Research Agent, Compliance Officer, QA, Doc Steward
검토자: Compliance Officer, QA, Doc Steward perspective
routing_ref: `@marketing` -> `@research` -> `@compliance` -> `@qa`
협업 waiver(사유): same-session Codex execution; deterministic artifact gates and official-source URLs recorded.
의도: TASK-096의 channel-specific official API/policy research 선행조건을 live action 없이 완료하고, 향후 approval-queue/dry-run 설계의 근거를 만든다.
대상: X, LinkedIn, Instagram, Naver Blog, Owner-controlled blog/dev log publishing policy matrix and stricter TASK-096 publishing policy packet
방법: official-source research, local JSON/Markdown policy packets, local gates, focused unit tests.
감사 로그: AUDIT-2026-06-19-041
실측 비용 (시간): 1h
실측 비용 (LLM 토큰): ~18000

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-GROWTH`
- Parent task: `TASK-096`

## 범위

포함:

- X, LinkedIn, Instagram, Naver Blog, Owner blog/dev log의 official-source policy/API matrix.
- Telegram, X, LinkedIn, Naver Share/Cafe, KakaoTalk Message, Google Business Profile의 TASK-096 publishing policy/dry-run handoff packet.
- create/update/delete or rollback capability summary.
- future approval queue required fields.
- prohibited automation and prohibited public-claim boundaries.
- local validation gate and focused unit tests.

제외:

- live public post, scheduled post, paid ad, customer email/DM.
- OAuth authorization flow, external account login, token handling, app setup.
- external API upload, browser automation against social platforms.
- customer/lead scraping, CRM creation, customer record storage.
- investment advice, performance, KIS commercial clearance, legal/tax final claim publication.
- KIS/order/risk/prod/deploy/secret changes.

## 완료 내용

- 공식 출처 기반 promotion channel policy matrix를 작성했다.
- TASK-096 handoff용 stricter publishing policy packet을 보존했다.
- X, LinkedIn, Instagram은 future approval-queue candidate로만 분류했다.
- Naver Blog는 자동 게시 unsupported/manual-only로 분류했다.
- Local gates/tests로 live publication, OAuth, external account action, token
  storage, paid ads, customer contact, scraping/spam/fake engagement boundary를
  검증했다.

## 완료 기록

완료일: 2026-06-19
완료 시각: 2026-06-19T22:58:13+09:00

결과:

- `PROMOTION-CHANNEL-POLICY-MATRIX.json` and `.md` created as research-only channel policy packet.
- `PROMOTION-PUBLISHING-POLICY-PACKET.json` and `.md` created as the stricter policy/dry-run handoff for TASK-096.
- `EVIDENCE-2026-06-19-008-promotion-channel-policy.md` records current official-source findings for the expanded promotion channel set.
- `promotion_channel_policy_gate.py` validates that the packet remains non-publishing, non-OAuth, non-secret, non-customer-contact, non-ad, and non-spam.
- `promotion_publishing_policy_gate.py` validates that the TASK-096 handoff keeps live posting, external action, OAuth, token handling, customer contact, paid ads, scraping, and engagement manipulation blocked.
- TASK-096 now has its official-source research prerequisite partially satisfied, but live publishing remains blocked.

변경 파일:

- `agents/project/PROMOTION-CHANNEL-POLICY-MATRIX.json`
- `agents/project/PROMOTION-CHANNEL-POLICY-MATRIX.md`
- `agents/project/PROMOTION-PUBLISHING-POLICY-PACKET.json`
- `agents/project/PROMOTION-PUBLISHING-POLICY-PACKET.md`
- `agents/research_agent/notes/EVIDENCE-2026-06-19-008-promotion-channel-policy.md`
- `scripts/promotion_channel_policy_gate.py`
- `scripts/promotion_publishing_policy_gate.py`
- `tests/unit/test_promotion_channel_policy_gate.py`
- `tests/unit/test_promotion_publishing_policy_gate.py`
- `agents/project/MARKETING-BRIEF.md`
- `agents/project/initiatives/TASKSET-MARKETING-GROWTH.md`
- `agents/lead_engineer/tasks/TASK-096-promotion-publishing-pipeline.md`

## 증거

- X Manage Posts: https://docs.x.com/x-api/posts/manage-tweets/introduction
- X authentication mapping: https://docs.x.com/fundamentals/authentication/guides/v2-authentication-mapping
- X automation rules: https://help.x.com/en/rules-and-policies/x-automation
- LinkedIn Posts API: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2026-06
- LinkedIn Community Management overview: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/community-management-overview?view=li-lms-2026-06
- LinkedIn Marketing API changes: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/recent-changes?view=li-lms-2026-05
- Instagram content publishing: https://developers.facebook.com/docs/instagram-platform/content-publishing/
- Instagram media publish reference: https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media_publish/
- Instagram Platform changelog: https://developers.facebook.com/docs/instagram-platform/changelog/
- NAVER Blog Open API shutdown: https://developers.naver.com/notice/article/7527
- NAVER Blog share guide: https://developers.naver.com/docs/share/share/
- NAVER Blog search API: https://developers.naver.com/docs/serviceapi/search/blog/blog.md

## 검증

- `python -m json.tool agents\project\PROMOTION-CHANNEL-POLICY-MATRIX.json`
- `python scripts\promotion_channel_policy_gate.py --check`
- `python -m pytest tests\unit\test_promotion_channel_policy_gate.py -q`
- `python -m json.tool agents\project\PROMOTION-PUBLISHING-POLICY-PACKET.json`
- `python scripts\promotion_publishing_policy_gate.py --check`
- `python -m pytest tests\unit\test_promotion_publishing_policy_gate.py -q`

## 리뷰

판정: 통과

- Official-source policy matrix is local-only and reviewable.
- Publishing policy packet is local-only and blocks live/external action by default.
- Naver Blog auto posting is explicitly unsupported.
- X, LinkedIn, and Instagram are future approval-queue candidates only.
- Telegram, Naver Cafe, KakaoTalk Message, and Google Business Profile are future candidates only when their account, consent, credential, business-profile, and review boundaries are satisfied.
- Live publication, OAuth, account action, token handling, paid ads, customer contact, and platform API calls remain blocked.

## Independent Audit

same-session self-review:

- The task does not perform any external mutation.
- The gate fails if a channel is marked live-enabled or publish-ready.
- The matrix keeps Owner approval and Compliance Officer review ahead of any public content.
- The policy packet keeps TASK-096's next allowed slice to local dry-run audit preview only.
- Remaining live publishing, account setup, API permissions, app review, and external posting are Owner/R3.

## Remaining

- TASK-096 still needs a local dry-run audit preview/state-machine contract before it can move toward implementation.
- Actual live posting and external account work remain blocked until explicit Owner/R3 approval.
