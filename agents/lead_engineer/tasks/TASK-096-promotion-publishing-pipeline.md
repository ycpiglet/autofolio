---
type: task
id: TASK-096
display_id: TASK-096
task_uid: ffcc5f5c-33c2-42e0-b1ff-1d9c426fd36e
registered_at: 2026-06-19T00:16:06+09:00
created_at: 2026-06-19T00:16:06+09:00
updated_at: 2026-06-19T23:22:07+09:00
started_at: 2026-06-19T00:16:06+09:00
completed_at: 2026-06-19T23:22:07+09:00
status: 완료
owner: Marketing Growth
assignees: [Marketing Growth, Backend Engineer, Compliance Officer, QA, Doc Steward]
priority: Medium
difficulty: 상
est_hours: 8
actual_hours: 5
est_tokens: 80000
actual_tokens: 108000
tags: [marketing, sns, external-api, publishing, automation, audit-log]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-GROWTH
gate: start after TASK-095; channel-specific official API/policy research and Owner approval required before any live post or external account action
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-003
created: 2026-06-19
---

# TASK-096 Promotion Publishing Pipeline

작업 ID: TASK-096
상태: 완료
Owner: Marketing Growth
요청 시각: 2026-06-19T00:16:06+09:00
기록 시각: 2026-06-19T23:22:07+09:00
완료 시각: 2026-06-19T23:22:07+09:00
요청자: Owner
수행자: Marketing Growth, Backend Engineer, Compliance Officer, QA, Doc Steward
검토자: Compliance Officer, QA, Doc Steward perspective
실측 비용 (시간): 5h
실측 비용 (LLM 토큰): 108000
의도: SNS/외부 채널 자동 업로드를 장기적으로 가능하게 하되, v1은 draft-first와 Owner 승인형 queue로 안전하게 설계한다.
대상: campaign draft workflow, publishing approval queue, channel policy evidence, audit log model
방법: official API/policy research 이후 draft -> preview -> approval -> publish queue 상태모델과 dry-run path를 먼저 설계하고, live posting은 Owner approval checkpoint로 막는다.
감사 로그: AUDIT-2026-06-19-003

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-GROWTH`

## TASK-129 선행 리서치 결과

`TASK-129` completed the channel-specific official API/policy research slice.

Created artifacts:

- `agents/project/PROMOTION-CHANNEL-POLICY-MATRIX.json`
- `agents/project/PROMOTION-CHANNEL-POLICY-MATRIX.md`
- `agents/project/PROMOTION-PUBLISHING-POLICY-PACKET.json`
- `agents/project/PROMOTION-PUBLISHING-POLICY-PACKET.md`
- `agents/research_agent/notes/EVIDENCE-2026-06-19-008-promotion-channel-policy.md`
- `scripts/promotion_channel_policy_gate.py`
- `scripts/promotion_publishing_policy_gate.py`

Result:

- X, LinkedIn, and Instagram are future approval-queue candidates only.
- Naver Blog is manual-only because automated write API support is treated as
  unavailable.
- Owner blog/dev log is a manual export candidate after claim review.
- Telegram, KakaoTalk Message, Naver Share/Cafe, and Google Business Profile
  are policy-reviewed candidates only; all require Owner/R3 boundaries before
  any live use.
- Live posting, OAuth, external account action, external API upload, paid ads,
  customer contact, browser automation, lead scraping, token handling, and public
  financial/performance/recommendation claims remain blocked.

## TASK-130 상태머신 계약 결과

`TASK-130` completed the local publishing state-machine contract.

Created artifacts:

- `agents/project/PROMOTION-PUBLISHING-STATE-MACHINE.json`
- `agents/project/PROMOTION-PUBLISHING-STATE-MACHINE.md`
- `scripts/promotion_publishing_state_machine_gate.py`

Result:

- Draft, copy-review, compliance-review, Owner-review, manual-export, dry-run,
  blocked, archive, and record-only after-live states are defined.
- Every transition has `live_action: false`.
- `live_recorded_after_owner_action` records an Owner-external action only; it
  never triggers publication.
- Auto-publish, OAuth, token storage, customer contact, paid ad, browser
  automation, lead scraping, fake engagement, and public investment/performance/
  KIS clearance claims are forbidden transitions.

## TASK-131 dry-run audit preview 결과

`TASK-131` completed the local dry-run audit preview.

Created artifacts:

- `agents/project/PROMOTION-DRY-RUN-AUDIT-PREVIEW.json`
- `agents/project/PROMOTION-DRY-RUN-AUDIT-PREVIEW.md`
- `scripts/promotion_dry_run_audit_preview_gate.py`

Result:

- The preview uses local source hashes from `MARKETING-MATERIALS-V1`,
  `PROMOTION-CHANNEL-POLICY-MATRIX`, `PROMOTION-PUBLISHING-POLICY-PACKET`, and
  `PROMOTION-PUBLISHING-STATE-MACHINE`.
- The preview record uses `owner_blog_manual`, `dry_run_scheduled`,
  `local_preview_only`, `not_scheduled`, `external_network_calls=false`, and
  `external_action_enabled=false`.
- The gate rejects source hash mismatch, live/external flags, token/customer
  fields, missing Owner boundary, forbidden copy phrases, and unknown channels.

## 시작 조건

- [x] TASK-095 Marketing Materials v1 완료.
- [x] 게시 후보 채널이 TASK-129에서 initial set으로 선택됨.
- [x] Research Agent가 각 채널의 공식 API 문서, 권한, rate/policy, 삭제/수정
      가능성, automation 정책을 확인.
- [x] Compliance Officer가 public marketing claim과 platform-risk boundary를 검토.

## 범위

포함:

- campaign draft -> preview -> approval -> publish queue 상태 모델 설계.
- manual export mode와 approval queue mode 구분.
- dry-run CLI 또는 문서화된 API contract 설계.
- audit log 필드: campaign_id, channel, approver, scheduled_at, posted_at,
  source_hash, external_url, rollback/delete instruction.
- per-channel policy gate와 unsupported channel 차단.
- live posting 전 Owner approval checkpoint.

제외:

- v1에서 무승인 자동 게시.
- viewbots, fake traffic/engagement, spam, unauthorized bulk posting, ToS evasion,
  platform manipulation, unsourced lead scraping.
- 외부 OAuth secret 저장, 실제 계정 로그인, 유료 광고 결제.
- 투자자문/성과보장/금융서비스 claim 자동 게시.
- 주문, 리스크, KIS, prod, secret, production DB 경로 변경.

## 완료 조건

- [x] publishing workflow state machine이 문서화됐다.
- [x] official-source evidence note가 채널별로 연결됐다.
- [x] dry-run path는 외부 네트워크 게시 없이 audit record preview를 만든다.
- [x] live post path는 Owner approval 없이는 실행 불가하다.
- [x] rollback/delete instruction이 채널별로 기록됐다.
- [x] BRIEF와 검증 기록이 남았다.

## 완료 내용

- TASK-129에서 채널별 공식 정책 matrix와 stricter publishing policy packet을 만들었다.
- TASK-130에서 promotion publishing state-machine contract를 만들고 live action을 모두 차단했다.
- TASK-131에서 local dry-run audit preview artifact와 gate/test를 추가했다.
- TASK-096은 no-Owner local design/preview scope에 한해 완료했다.
- Live public posting, OAuth, external account action, token/channel-id handling,
  paid ads, customer contact, generated public asset export는 계속 Owner/R3로
  남겼다.

## 완료 기록

완료일: 2026-06-19

결과:

- TASK-129, TASK-130, and TASK-131 completed the promotion publishing design
  chain: channel policy, publishing policy, state-machine contract, and dry-run
  audit preview.
- TASK-096 is complete for the no-Owner local design/preview scope.
- Live public posting, OAuth, account setup, token/channel-id handling, external
  API upload, paid ads, customer contact, and generated public asset export
  remain excluded and Owner/R3.

## 증거

- `agents/project/PROMOTION-CHANNEL-POLICY-MATRIX.json`
- `agents/project/PROMOTION-PUBLISHING-POLICY-PACKET.json`
- `agents/project/PROMOTION-PUBLISHING-STATE-MACHINE.json`
- `agents/project/PROMOTION-DRY-RUN-AUDIT-PREVIEW.json`
- `scripts/promotion_channel_policy_gate.py`
- `scripts/promotion_publishing_policy_gate.py`
- `scripts/promotion_publishing_state_machine_gate.py`
- `scripts/promotion_dry_run_audit_preview_gate.py`
- `agents/lead_engineer/reports/BRIEF-2026-06-19-041.md`

## 리뷰

판정: 통과

- Compliance boundary는 live/OAuth/token/external/customer/paid-ad/browser
  automation/scraping 경로를 모두 별도 Owner/R3 lane으로 분리했다.
- QA boundary는 focused gates와 dry-run tests로 local preview-only behavior를
  확인했다.
- Doc Steward boundary는 task, BRIEF, status, initiative, next-session pointer에
  completion/handoff를 기록했다.

## 검증

- `python scripts/check_agent_docs.py`
- `python scripts/generate_views.py --check`
- `python scripts/promotion_channel_policy_gate.py --check`
- `python scripts/promotion_publishing_policy_gate.py --check`
- `python scripts/promotion_publishing_state_machine_gate.py --check`
- `python scripts/promotion_dry_run_audit_preview_gate.py --check`
- dry-run test는 token 없이 실행되며 외부 게시를 만들지 않아야 한다.
- prohibited automation keyword와 banned claim이 publish queue를 통과하지 못해야 한다.
