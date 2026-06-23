---
type: task
id: TASK-167
display_id: TASK-167
task_uid: 49f5003e-c951-45d8-99ba-3f5cc2899e18
registered_at: 2026-06-20T10:42:57+09:00
created_at: 2026-06-20T10:42:57+09:00
updated_at: 2026-06-20T11:15:48+09:00
started_at: 2026-06-20T11:11:07+09:00
completed_at: 2026-06-20T11:15:48+09:00
status: 완료
owner: Marketing Growth
assignees: [Marketing Growth, Compliance Officer, Business Planner, QA, Doc Steward]
priority: High
difficulty: 중
est_hours: 3
est_tokens: 35000
tags: [marketing, campaign, content-calendar, claim-bank, early-users]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-TEAM-OPERATING-SYSTEM
gate: draft campaign planning only; no public posting, no paid ads, no customer contact, no external account action, no final asset export
trigger_meeting: Owner direct request 2026-06-20
audit_log: AUDIT-2026-06-20-067
created: 2026-06-20
---

# TASK-167 Promotion Campaign Backlog And Content Calendar V1

작업 ID: TASK-167
상태: 완료
Owner: Marketing Growth
요청 시각: 2026-06-20T10:42:57+09:00
기록 시각: 2026-06-20T11:15:48+09:00
요청자: Owner
수행자: Marketing Growth, Compliance Officer, Business Planner, QA, Doc Steward
의도: Marketing Brief와 Marketing Materials v1을 실행 가능한 campaign backlog와 content calendar로 분해한다.
대상: private pilot explainer, owner blog/dev log, landing-page source, PDF/PPTX source, SNS draft bundle backlog
방법: source claim, review status, channel candidate, required approval을 가진 draft-only backlog/calendar artifact를 만든다.
감사 로그: AUDIT-2026-06-20-067
완료 시각: 2026-06-20T11:15:48+09:00
실측 비용 (시간): 약 0.25h
실측 비용 (LLM 토큰): unknown
검토자: Marketing Growth self-review + Compliance Officer perspective + Business Planner perspective + QA focused gate tests + Doc Steward perspective
협업 waiver(사유): 단일 세션 범위의 local campaign backlog/calendar 문서 및 게이트 작업이다. 외부 subagent dispatch 없이 역할별 관점 검토와 deterministic local gate/tests로 대체했고, public/SNS/customer/payment/CRM/Sales/OAuth/platform API/final asset export/KIS/deploy 경계는 건드리지 않았다.
routing_ref: TASKSET-MARKETING-TEAM-OPERATING-SYSTEM / TASK-167
selected_model: Codex coding agent

## 목표

기존 marketing brief를 실행 가능한 campaign backlog와 content calendar로 쪼갠다.

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-TEAM-OPERATING-SYSTEM`
- Depends on: `TASK-166`

## 범위

포함:

- Private pilot explainer, owner blog/dev log, landing-page source,
  PDF/PPTX source, SNS draft bundle의 backlog 항목화.
- 각 campaign item별 audience, promise, proof, source claim, review status,
  channel candidate, required approval, owner role 기록.
- 2~4주 draft-only content calendar 초안.
- `allowed`, `needs_compliance_review`, `do_not_use` claim 분류 연결.

제외:

- 실제 게시, 예약 게시, 광고 집행, 고객 이메일/DM.
- 공개 가격/성과/추천/투자자문 claim 확정.
- 외부 계정 로그인, OAuth, token, platform API call.
- 최종 asset export, public URL, CRM/payment.

## 완료 조건

- [x] Campaign backlog artifact가 존재한다.
- [x] Content calendar가 draft/review gate 상태를 가진다.
- [x] 모든 campaign item이 source artifact와 claim status를 가진다.
- [x] 금지 claim과 review-required claim이 campaign copy와 분리된다.

## 완료 내용

- `PROMOTION-CAMPAIGN-BACKLOG-CALENDAR-V1.json`와 `.md`를 추가했다.
- Private pilot explainer, owner blog/dev log, landing-page source,
  PDF/PPTX source bundle, SNS draft bundle을 campaign backlog item으로 분리했다.
- 2026-06-24부터 2026-07-17까지 4주 draft-only content calendar를 만들고
  각 항목에 source artifact, claim status, review gate, approval gate,
  `live_action_enabled=false`, `publish_ready=false`를 기록했다.
- `allowed_draft`, `needs_review`, `do_not_use` claim을 분리하고, review-required
  claim과 금지 claim이 campaign copy seed에 들어가면 실패하는 gate를 추가했다.
- TASK-168, TASK-169, TASK-170을 후속 후보로 남기고, 추천 다음 작업을 TASK-168
  asset generator readiness map으로 정리했다.

## 완료 기록

완료일: 2026-06-20
결과: TASK-167은 draft-only campaign backlog/content calendar v1으로 완료됐다.
변경 파일: `PROMOTION-CAMPAIGN-BACKLOG-CALENDAR-V1.json`,
`PROMOTION-CAMPAIGN-BACKLOG-CALENDAR-V1.md`,
`scripts/promotion_campaign_backlog_calendar_gate.py`,
`tests/unit/test_promotion_campaign_backlog_calendar_gate.py`, taskset/task/report/status/generated views.
이슈: 없음. 실제 public post, SNS upload, paid ads, customer contact,
CRM/customer records, payment request, Sales/Revenue activation, OAuth,
platform API call, browser automation, final PDF/PPTX export, public URL,
secret/customer data, KIS/order/risk/prod/deploy 변경 없음.
다음 담당자 인수 사항: TASK-168은 이 backlog/calendar를 입력으로 PDF/PPTX,
landing source, SNS draft source의 asset generator readiness map을 작성한다.

## 증거

- `agents/project/PROMOTION-CAMPAIGN-BACKLOG-CALENDAR-V1.json`
- `agents/project/PROMOTION-CAMPAIGN-BACKLOG-CALENDAR-V1.md`
- `scripts/promotion_campaign_backlog_calendar_gate.py`
- `tests/unit/test_promotion_campaign_backlog_calendar_gate.py`
- `agents/lead_engineer/reports/BRIEF-2026-06-20-035.md`

## 검증

- `python -m json.tool agents\project\PROMOTION-CAMPAIGN-BACKLOG-CALENDAR-V1.json`
- `python -m py_compile scripts\promotion_campaign_backlog_calendar_gate.py`
- `python scripts\promotion_campaign_backlog_calendar_gate.py --check`
- `python -m pytest tests\unit\test_promotion_campaign_backlog_calendar_gate.py -q`

## 리뷰

- Marketing Growth perspective: campaign backlog가 channel/surface 단위로 쪼개졌고, copy seed는 allowed_draft claim만 사용한다.
- Compliance Officer perspective: recommendation, paid pilot, token integration, KIS commercial wording은 review queue로 격리됐다.
- Business Planner perspective: verified-person pilot, pricing/support/refund/privacy boundary가 public copy와 분리됐다.
- QA perspective: local gate/tests가 live/publication flag, forbidden key, missing campaign, weak calendar coverage, forbidden/review claim drift를 실패시킨다.
- Doc Steward perspective: source artifacts와 후속 TASK-168~170 handoff가 명시됐다.

## Independent Audit

판정: 통과

- Same-session audit note: only local docs/JSON/gate/tests/governance records changed.
- No public posting, SNS upload, paid ads, customer contact, CRM/customer record,
  payment request, Sales/Revenue activation, OAuth, external platform API call,
  browser automation, final PDF/PPTX binary export, public URL publication,
  secret/customer data, legal/tax/securities final advice, KIS/order/risk/prod,
  or deploy boundary was crossed.
