---
type: task
id: TASK-095
display_id: TASK-095
task_uid: c194f519-83c2-4452-a360-431615fe3273
registered_at: 2026-06-19T00:16:06+09:00
created_at: 2026-06-19T00:16:06+09:00
updated_at: 2026-06-19T22:36:50+09:00
started_at: 2026-06-19T22:36:50+09:00
completed_at: 2026-06-19T22:36:50+09:00
status: 완료
owner: Marketing Growth
assignees: [Marketing Growth, Business Planner, Compliance Officer, UI/UX Designer, QA, Doc Steward]
priority: High
difficulty: 중
est_hours: 4
est_tokens: 50000
tags: [marketing, go-to-market, campaign, pdf, pptx, early-users]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-GROWTH
gate: draft source complete; no public posting, paid ads, customer contact, external account action, final PDF/PPTX export, or SNS upload before Owner/review approval
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-039
created: 2026-06-19
---

# TASK-095 Marketing Materials v1

작업 ID: TASK-095
상태: 완료
Owner: Marketing Growth
요청 시각: 2026-06-19T00:16:06+09:00
기록 시각: 2026-06-19T00:16:06+09:00
요청자: Owner
수행자: Marketing Growth, Business Planner, Compliance Officer, UI/UX Designer, QA, Doc Steward
검토자: Marketing Growth self-review + Compliance Officer perspective + QA focused gate tests + Doc Steward perspective
routing_ref: TASKSET-MARKETING-GROWTH / TASK-095
협업 waiver(사유): single-session scope with role-perspective review and deterministic marketing materials gate; no external worker dispatch was needed for this docs/gate-only slice.
의도: early external users를 대상으로 Autofolio 홍보물 v1을 작성하고, PDF/PPTX/SNS 초안 생성의 원천 자료를 만든다.
대상: `agents/project/MARKETING-BRIEF.md`, campaign source drafts, one-page PDF source, PPTX outline, SNS draft bundle
방법: Business Plan v1과 approved claim bank를 입력으로 삼아 reviewable text artifacts를 만들고, 각 claim을 allowed / needs-review / do-not-use로 분류한다.
감사 로그: AUDIT-2026-06-19-039
완료 시각: 2026-06-19T22:36:50+09:00
실측 비용 (시간): 약 0.4h
실측 비용 (LLM 토큰): unknown

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-GROWTH`

## 시작 조건

- TASK-093 Business Plan v1 완료.
- `agents/project/MARKETING-BRIEF.md`의 audience, positioning, claim bank,
  banned claim list, CTA, review gate가 갱신됨.
- Compliance Officer가 투자성과, 투자자문, 세무/법률, 금융서비스 경계 문구를
  검토할 수 있는 입력이 있음.

## 범위

포함:

- early-user campaign brief v1 작성.
- landing-page copy 초안.
- 1-page PDF explainer 원천 Markdown/YAML.
- PPTX pitch deck outline과 slide copy 초안.
- SNS post draft bundle.
- support FAQ와 disclaimer draft.
- 각 claim의 source/evidence/review status 표시.

제외:

- 실제 PDF/PPTX binary generator 구현.
- 공개 게시, 유료 광고, 이메일 발송, 고객 연락, 외부 계정 로그인.
- 수익률, 투자자문, 세무/법률 확정 claim.
- 제품 코드, KIS/order/risk/prod, secret, production DB 변경.

## 완료 조건

- [x] `MARKETING-BRIEF.md`에 campaign brief v1이 연결됐다.
- [x] 랜딩 카피, PDF one-pager source, PPTX deck source, SNS draft bundle이
      reviewable text artifact로 작성됐다.
- [x] 각 문구가 allowed / needs-review / do-not-use로 분류됐다.
- [x] Compliance Officer review 대상 문구가 분리됐다.
- [x] BRIEF와 검증 기록이 남았다.

## 완료 내용

- `agents/project/MARKETING-MATERIALS-V1.json`와 `.md`를 추가했다.
- Campaign brief, landing-page copy, PDF one-pager source, PPTX deck source,
  SNS draft bundle, support FAQ, disclaimer draft를 작성했다.
- Claim review map을 `allowed_draft`, `needs_review`, `do_not_use`로 분리했다.
- `scripts/marketing_materials_gate.py`와 focused tests를 추가해 draft-only,
  no-publication, no-secret, no customer/private data, no performance guarantee,
  no investment-advice/KIS-clearance claim boundary를 검증한다.
- `MARKETING-BRIEF.md`에 TASK-095 draft packet과 TASK-096 입력 경계를 연결했다.

## 완료 기록

완료일: 2026-06-19
결과: Marketing Materials v1은 reviewable draft source로 완료됐다. Public
posting, paid ads, customer contact, external account action, SNS upload, final
PDF/PPTX export, recommendation/performance/KIS commercial-readiness claim은
Owner/review gate 전까지 계속 금지된다.
변경 파일: `MARKETING-MATERIALS-V1.json`, `MARKETING-MATERIALS-V1.md`,
`scripts/marketing_materials_gate.py`, `tests/unit/test_marketing_materials_gate.py`,
`MARKETING-BRIEF.md`, task/report/status/generated views.
이슈: 최초 gate가 "not a broker/asset manager/investment advice"처럼 금지어를
포함한 부정 설명까지 잡아내서, public copy 표면에서는 금지 표현 자체를 피하는
방향으로 문구를 수정했다.
다음 담당자 인수 사항: TASK-096은 이 packet을 입력으로 approval queue,
channel policy, audit log, rollback/delete path를 설계해야 하며 live posting은
여전히 Owner/R3이다.

## 증거

- `agents/project/MARKETING-MATERIALS-V1.json`
- `agents/project/MARKETING-MATERIALS-V1.md`
- `scripts/marketing_materials_gate.py`
- `tests/unit/test_marketing_materials_gate.py`
- `agents/lead_engineer/reports/BRIEF-2026-06-19-037.md`

## 검증

- `python scripts/check_agent_docs.py`
- `python scripts/generate_views.py --check`
- `python -m json.tool agents\project\MARKETING-MATERIALS-V1.json`
- `python scripts\marketing_materials_gate.py --check`
- `python -m pytest tests\unit\test_marketing_materials_gate.py -q`
- 생성 소스에 secret, 계좌, KIS key, 고객 개인정보, 성과 보장 문구가 없는지
  수동 grep/리뷰.

## 리뷰

- Marketing Growth self-review: Business Plan v1과 Marketing Brief의 safe
  claim만 draft copy에 사용했고, 공개 승인으로 오인될 문구는 모두 차단했다.
- Compliance Officer perspective: recommendation, pricing, KIS commercial use,
  provider token, payment/refund/privacy/support 문구는 review 대상으로 남겼다.
- QA perspective: focused gate/tests가 publication approval, public posting
  boundary weakening, forbidden copy phrase, secret/private key names, missing
  SNS drafts를 실패시키는지 확인한다.
- Doc Steward perspective: `MARKETING-BRIEF.md`와 TASKSET-MARKETING-GROWTH가
  TASK-095 완료와 TASK-096 후속 입력을 가리킨다.

## Independent Audit

판정: 통과
- Same-session audit note: Only local docs/JSON/gate/tests/governance records
  changed.
- No public post, paid ad, customer contact, external account login/upload,
  SNS auto-posting, final PDF/PPTX binary generation, secret/customer/private
  data handling, bank account value, KIS/order/risk/prod/deploy boundary,
  investment-advice claim, performance guarantee, or KIS commercial clearance
  claim was created.
