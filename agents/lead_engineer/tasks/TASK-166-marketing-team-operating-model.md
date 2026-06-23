---
type: task
id: TASK-166
display_id: TASK-166
task_uid: a118bfba-25f5-4bf2-8e64-b00f139f9cde
registered_at: 2026-06-20T10:42:57+09:00
created_at: 2026-06-20T10:42:57+09:00
updated_at: 2026-06-20T11:05:43+09:00
started_at: 2026-06-20T10:56:38+09:00
completed_at: 2026-06-20T11:00:16+09:00
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, Marketing Growth, Compliance Officer, Business Planner, Doc Steward, QA]
priority: High
difficulty: 중
est_hours: 2
est_tokens: 25000
tags: [marketing, agents, operating-model, routing, go-to-market]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-TEAM-OPERATING-SYSTEM
gate: local operating model only; no public posting, no customer contact, no external account action, no CRM/payment, no final asset export, no KIS/order/risk/prod/deploy change
trigger_meeting: Owner direct request 2026-06-20
audit_log: AUDIT-2026-06-20-066
created: 2026-06-20
---

# TASK-166 Marketing Team Operating Model

작업 ID: TASK-166
상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-20T10:42:57+09:00
기록 시각: 2026-06-20T11:05:43+09:00
요청자: Owner
수행자: Lead Engineer, Marketing Growth, Compliance Officer, Business Planner, Doc Steward, QA
의도: 기존 Marketing Growth plan을 marketing team이 반복 실행할 수 있는 operating model로 바꾼다.
대상: marketing team role routing, intake/review/closeout workflow, TASK-167~170 실행 기준
방법: 기존 BUSINESS-PLAN, MARKETING-BRIEF, TASKSET-MARKETING-GROWTH 산출물을 source로 삼아 local docs/readiness artifact만 만든다.
감사 로그: AUDIT-2026-06-20-066
완료 시각: 2026-06-20T11:00:16+09:00
실측 비용 (시간): 약 0.2h
실측 비용 (LLM 토큰): unknown
검토자: Marketing Growth perspective + Compliance Officer perspective + QA focused gate tests + Doc Steward perspective + same-session self-review
협업 waiver(사유): 단일 세션 범위의 docs/gate 작업이다. 외부 subagent dispatch 없이 역할별 관점 검토와 deterministic local gate/tests로 대체했고, public/SNS/customer/payment/KIS/deploy 경계는 건드리지 않았다.
routing_ref: TASKSET-MARKETING-TEAM-OPERATING-SYSTEM / TASK-166
selected_model: Codex coding agent

## 목표

Marketing Growth plan을 실행 가능한 team operating model로 바꾼다.

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-TEAM-OPERATING-SYSTEM`
- Source taskset: `TASKSET-MARKETING-GROWTH`

## 범위

포함:

- Marketing Growth, Compliance Officer, Business Planner, Regulatory Admin,
  Doc Steward, Backend Engineer, QA의 홍보 관련 책임 경계 정리.
- `marketing team`이 산출물을 만들 때의 intake, routing, review, closeout
  흐름 정의.
- Sales/Revenue가 아직 비활성인 상태에서 Marketing Growth가 맡을 수 있는
  범위와 넘겨야 할 조건 정리.
- Public/action gate 체크리스트 작성.

제외:

- 실제 공개 게시, SNS 업로드, 광고 집행, 고객 연락.
- Sales/Revenue role 생성 또는 활성화.
- 최종 PDF/PPTX binary export.
- CRM/customer record, payment, billing, support execution.
- OAuth, token, secret, external platform account action.
- KIS/order/risk/prod/deploy 변경.

## 완료 조건

- [x] `agents/project/MARKETING-TEAM-OPERATING-MODEL.md` 또는 동등한
      local artifact가 존재한다.
- [x] 역할별 input/output/forbidden action이 명확하다.
- [x] Compliance review trigger와 Owner/R3 trigger가 분리된다.
- [x] TASK-167~170 실행 기준이 연결된다.

## 완료 내용

- `MARKETING-TEAM-OPERATING-MODEL.json`와 `.md`를 추가했다.
- Marketing Growth, Compliance Officer, Business Planner, Regulatory Admin,
  Doc Steward, Backend Engineer, QA, Lead Engineer의 홍보 관련 input/output/
  forbidden action을 분리했다.
- campaign copy, PDF/PPTX/asset generation readiness, SNS publishing automation
  readiness, sales/revenue handoff 요청을 TASK-167~170으로 라우팅했다.
- Compliance review trigger와 Owner/R3 trigger를 별도 목록으로 고정했다.
- `marketing_team_operating_model_gate.py`와 focused tests를 추가해 public
  posting, SNS upload, customer contact, CRM/payment, OAuth, platform API call,
  final PDF/PPTX export, secret/customer key, KIS/order/risk/prod/deploy 플래그를
  차단한다.

## 완료 기록

완료일: 2026-06-20
결과: Marketing Team Operating Model은 local-only 운영모델로 완료됐다. TASK-167이
다음 no-Owner local campaign backlog/content calendar 후보로 남는다.
변경 파일: `MARKETING-TEAM-OPERATING-MODEL.json`, `MARKETING-TEAM-OPERATING-MODEL.md`,
`scripts/marketing_team_operating_model_gate.py`,
`tests/unit/test_marketing_team_operating_model_gate.py`, taskset/task/report/status/generated views.
이슈: 없음. 실제 public post, SNS upload, paid ads, customer contact, CRM/payment,
Sales/Revenue activation, OAuth, platform API call, final PDF/PPTX export,
secret/customer data, KIS/order/risk/prod/deploy 변경 없음.
다음 담당자 인수 사항: TASK-167은 이 운영모델을 입력으로 draft-only campaign
backlog와 content calendar를 작성한다.

## 증거

- `agents/project/MARKETING-TEAM-OPERATING-MODEL.json`
- `agents/project/MARKETING-TEAM-OPERATING-MODEL.md`
- `scripts/marketing_team_operating_model_gate.py`
- `tests/unit/test_marketing_team_operating_model_gate.py`
- `agents/lead_engineer/reports/BRIEF-2026-06-20-034.md`

## 검증

- `python -m json.tool agents\project\MARKETING-TEAM-OPERATING-MODEL.json`
- `python -m py_compile scripts\marketing_team_operating_model_gate.py`
- `python scripts\marketing_team_operating_model_gate.py --check`
- `python -m pytest tests\unit\test_marketing_team_operating_model_gate.py -q`

## 리뷰

- Lead Engineer self-review: taskset 첫 단계로 필요한 역할/라우팅/게이트를 source-of-truth artifact로 고정했고, TASK-167~170 시작 조건을 연결했다.
- Marketing Growth perspective: campaign/content work는 TASK-167로 분리되고, public publishing은 계속 Owner/R3로 남는다.
- Compliance Officer perspective: 금융/성과/추천/KIS/세무·법률/규제 claim review trigger가 별도 목록으로 분리됐다.
- QA perspective: gate/tests가 live/external action flag, forbidden key, missing trigger, route drift를 실패시킨다.

## Independent Audit

판정: 통과

- Same-session audit note: only local docs/JSON/gate/tests/governance records changed.
- No public posting, SNS upload, paid ads, customer contact, CRM/customer record,
  payment request, Sales/Revenue activation, OAuth, external platform API call,
  final PDF/PPTX binary export, public URL publication, secret/customer data,
  legal/tax/securities final advice, KIS/order/risk/prod, or deploy boundary was
  crossed.
