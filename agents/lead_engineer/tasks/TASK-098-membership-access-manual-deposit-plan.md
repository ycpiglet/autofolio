---
type: task
id: TASK-098
display_id: TASK-098
task_uid: 384749ab-60a1-4bbd-873c-8865898559c0
registered_at: 2026-06-19T13:18:08+09:00
created_at: 2026-06-19T13:18:08+09:00
started_at: 2026-06-19T13:18:08+09:00
updated_at: 2026-06-19T13:18:08+09:00
completed_at: 2026-06-19T13:18:08+09:00
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, Business Planner, Regulatory Admin, Marketing Growth, Compliance Officer]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 12000
tags: [membership, payment, bank-transfer, approval, signup, taskset]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-ACCESS
gate: docs/planning only; no real bank account number, customer data, secret, external bank API, production DB, deploy, KIS/order/risk/prod change
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-008
created: 2026-06-19
---

# TASK-098 Membership access manual deposit plan

작업 ID: TASK-098
상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-19T13:18:08+09:00
기록 시각: 2026-06-19T13:18:08+09:00
완료 시각: 2026-06-19T13:18:08+09:00
요청자: Owner
수행자: Lead Engineer, Business Planner, Regulatory Admin, Marketing Growth, Compliance Officer perspective
검토자: Lead Engineer self-review + Regulatory Admin perspective + Compliance Officer perspective + Marketing Growth perspective
협업 waiver(사유): 단일 세션 docs/planning 범위 작업. 실제 payment/auth 구현 없이 deterministic docs gates로 검증.
routing_ref: TASKSET-MEMBERSHIP-ACCESS / TASK-098
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 docs-only lane; AGENTS.md §16 Autofolio R3 surface avoided
실측 비용 (시간): 약 0.2h
실측 비용 (LLM 토큰): unknown
의도: CTA를 검증된 사람만 가입승인하고, 무통장입금/입금코드 확인으로 계정을 활성화하는 운영 모델로 정정한다.
대상: `BUSINESS-PLAN.md`, `MARKETING-BRIEF.md`, `BUSINESS-ADMIN-REGISTER.md`, `MEMBERSHIP-ACCESS-PLAN.md`, `TASK-087`
방법: 실제 계좌번호/개인정보/외부 결제 연동 없이 placeholder-safe 계획과 taskset을 등록한다.
감사 로그: AUDIT-2026-06-19-008

## Taskset

- Initiative: `INIT-MEMBERSHIP-ACCESS`
- Taskset: `TASKSET-MEMBERSHIP-ACCESS`

## 범위

포함:

- CTA를 `verified signup request`로 정정.
- 무통장입금 가격/계좌 안내, 수동 입금 확인, 고유 입금코드 인식, 계정 승인 흐름을 문서화.
- membership state machine과 admin approval audit log 요구사항 정의.
- TASK-087 구현 입력 보강.

제외:

- 실제 계좌번호 커밋.
- 실제 고객 개인정보/입금 기록 저장.
- 외부 은행 API/OAuth/PG 연동.
- production DB, 배포, 결제, 회원가입 코드 구현.
- KIS/order/risk/prod/secret 변경.

## 완료 조건

- [x] `BUSINESS-PLAN.md` CTA와 pricing flow가 verified signup / manual deposit approval로 갱신됐다.
- [x] `MARKETING-BRIEF.md` CTA와 claim bank가 verified-person approval을 반영한다.
- [x] `BUSINESS-ADMIN-REGISTER.md`에 bank-transfer approval implications가 들어갔다.
- [x] `MEMBERSHIP-ACCESS-PLAN.md`가 생성됐다.
- [x] `TASKSET-MEMBERSHIP-ACCESS`가 생성됐다.
- [x] `TASK-087`에 구현 입력이 연결됐다.

## 완료 기록

완료일: 2026-06-19
결과: membership access plan과 taskset을 등록했고, Business/Marketing/Admin 문서가 검증회원 + 무통장입금 승인 흐름을 같은 정본으로 가리킨다.
변경 파일: `agents/project/MEMBERSHIP-ACCESS-PLAN.md`, `BUSINESS-PLAN.md`, `MARKETING-BRIEF.md`, `BUSINESS-ADMIN-REGISTER.md`, `TASK-087`, `INIT-MEMBERSHIP-ACCESS`, `TASKSET-MEMBERSHIP-ACCESS`.
이슈: 실제 구현에는 auth/state schema, admin UI, payment evidence handling, 개인정보/환불/영수증 정책이 필요하다.
다음 담당자 인수 사항: TASK-087 구현 전에 real bank account numbers and customer data must stay out of repo.

## 완료 내용

- `verified signup request -> price/bank-transfer instruction -> manual/code-assisted deposit confirmation -> account activation` 흐름을 정본화했다.
- account states를 requested, verification_pending, deposit_pending, active, rejected, expired로 정의했다.
- manual confirmation과 code-assisted recognition의 차이를 분리했다.
- 실제 계좌번호는 repo가 아니라 runtime/admin configuration에서 주입하도록 경계화했다.

## 결과

TASK-098 완료. TASK-087 구현은 더 구체적인 입력을 갖게 됐지만, production deploy/payment/bank API/DB migration은 여전히 별도 승인 경계다.

## 증거

- `agents/project/MEMBERSHIP-ACCESS-PLAN.md`
- `agents/project/BUSINESS-PLAN.md`
- `agents/project/MARKETING-BRIEF.md`
- `agents/project/BUSINESS-ADMIN-REGISTER.md`
- `agents/project/initiatives/TASKSET-MEMBERSHIP-ACCESS.md`
- `agents/lead_engineer/tasks/TASK-087-web-deploy-membership-gating.md`

## 리뷰

- Lead Engineer self-review: Owner가 정정한 CTA와 결제승인 모델을 taskset과 구현 입력으로 보존했다.
- Regulatory Admin perspective: payment/refund/receipt/tax/account-display policy는 후속 admin/professional review 대상이다.
- Compliance Officer perspective: membership/payment approval 자체보다 agent recommendation claim과 paid signal 오인이 더 큰 watch 항목이다.
- Marketing Growth perspective: public copy는 "승인 기반 가입"만 말할 수 있고 실제 계좌번호나 결제식별자는 홍보물 source에 넣으면 안 된다.

## Independent Audit

판정: 통과

Same-session audit note: 문서/계획 작업이며 외부 worker dispatch는 하지 않았다. R3 경계인 실제 계좌번호, 결제 구현, 외부 은행 API, production DB, 배포, KIS/order/risk/prod/secret 변경은 수행하지 않았다.

## 검증

- `python scripts/build_task_index.py --check`
- `python scripts/generate_views.py --check`
- `python scripts/generate_report_views.py --check`
- `python scripts/validate_task_schema.py`
- `python scripts/work_schema_gate.py --items --check`
- `python scripts/continuity_contract_gate.py --check`
- `python scripts/conversation_work_audit.py --check`
- `python scripts/owner_governance_gate.py --allow-empty-owner-docs`
- `python scripts/check_agent_docs.py`
- `git diff --check`
