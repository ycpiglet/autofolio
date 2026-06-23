---
type: task
id: TASK-117
display_id: TASK-117
task_uid: 8e395a40-54d4-4ba6-9abc-b56a53d04192
registered_at: 2026-06-19T19:57:08+09:00
created_at: 2026-06-19T19:57:08+09:00
updated_at: 2026-06-19T20:50:20+09:00
started_at: 2026-06-19T20:47:06+09:00
completed_at: 2026-06-19T20:50:20+09:00
status: 완료
owner: Regulatory Admin
assignees: [Regulatory Admin, Backend Engineer, Compliance Officer, QA]
priority: Medium
difficulty: 중
est_hours: 2
est_tokens: 35000
tags: [membership, payment, bank-transfer, recognition, decision-packet]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING
gate: official-source decision packet only; no bank account setup, no API credential, no payment provider action, no real payment data
trigger_meeting: Owner goal continuation 2026-06-19
audit_log: AUDIT-2026-06-19-029
created: 2026-06-19
---

# TASK-117 Membership payment recognition decision packet

작업 ID: TASK-117
상태: 완료
Owner: Regulatory Admin
요청 시각: 2026-06-19T19:57:08+09:00
기록 시각: 2026-06-19T19:57:08+09:00
완료 시각: 2026-06-19T20:50:20+09:00
요청자: Owner goal continuation
수행자: Regulatory Admin + Backend Engineer + Compliance Officer + QA perspective (Codex)
검토자: Regulatory Admin self-review + Backend Engineer data-boundary review + Compliance Officer privacy/tax boundary perspective + QA checklist perspective; 협업 waiver(사유): single-session official-source decision packet scope; no bank/PG/Open Banking account setup, credential, API call, real payment data, production DB apply, deploy, or legal/tax/accounting final advice crossed.
routing_ref: TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING / TASK-117
selected_model: Codex coding agent
policy_model: Regulatory Admin official-source rule + official FSC/KFTC/Hometax/privacy/provider source checks; AGENTS.md §6 R1/R2 local reversible planning lane; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.4h
실측 비용 (LLM 토큰): unknown
의도: Manual approval, CSV import, open-banking API, PG, virtual account options를 official-source 기반으로 비교한다.
대상: payment recognition decision packet and payment evidence policy handoff.
방법: official-source decision packet only. No bank account setup, no API credential, no payment provider action, no real payment data.
감사 로그: AUDIT-2026-06-19-029

## 범위

포함:

- Current official-source research where needed.
- Option matrix for cost, operational burden, privacy, audit, refund/receipt/tax implications.
- Recommended MVP and upgrade path.

제외:

- External account login, contract, payment, bank/PG API setup.
- Real bank account number or payment record.
- Legal/tax/accounting final advice.

## 완료 조건

- [x] Option decision packet exists.
- [x] Owner-only external actions are separated.
- [x] Payment evidence policy remains enforced.

## 협업 / 승인

- 협업 waiver: 단일 세션의 official-source decision packet 작업으로 제한했다. 실제 은행/PG/Open Banking 계정 생성, credential 발급, API 호출, 실결제 데이터 처리, 법률/세무 최종 판단은 하지 않았다.
- 적용한 관점: Regulatory Admin official-source rule, Backend Engineer data-boundary view, Compliance Officer privacy/tax boundary, QA local gate view.

## 완료 내용

- `MEMBERSHIP-PAYMENT-RECOGNITION-DECISION-PACKET.json`/`.md`를 작성해 manual bank-app check, code-assisted match, CSV review, provider reference, PG virtual-account webhook, Open Banking transaction inquiry를 비교했다.
- MVP 결정은 `manual_bank_app_check_plus_code_assisted_deposit_match`로 고정했다.
- Open Banking은 official participation/security/function-test/credential/consent가 필요한 R3 lane으로 분리했다.
- PG/virtual-account webhook은 provider contract, webhook source verification, idempotency/retry, refund/receipt/tax/privacy review 후 scale upgrade로 분리했다.
- `scripts/membership_payment_recognition_decision_gate.py`와 focused unit tests를 추가해 packet이 not-applied 상태, no real payment data, no raw statement persistence, no immediate Open Banking/PG activation을 유지하는지 검증한다.

## 완료 기록

완료일: 2026-06-19
결과: TASK-087의 payment recognition option decision gap이 R2 decision packet으로 좁혀졌다. 이 산출물은 decision packet only이며 launch evidence나 payment automation implementation이 아니다.
변경 파일: `agents/project/MEMBERSHIP-PAYMENT-RECOGNITION-DECISION-PACKET.json`, `agents/project/MEMBERSHIP-PAYMENT-RECOGNITION-DECISION-PACKET.md`, `scripts/membership_payment_recognition_decision_gate.py`, `tests/unit/test_membership_payment_recognition_decision_gate.py`, `agents/project/MEMBERSHIP-PRODUCTION-IMPLEMENTATION-PLAN.md`, `agents/project/initiatives/TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING.md`, `agents/lead_engineer/tasks/TASK-087-web-deploy-membership-gating.md`, TASKSET/STATUS/AUDIT/BRIEF/generated views.
이슈: 실제 PG/가상계좌/Open Banking 자동화는 Owner 승인, 외부 계정/계약, credential, staging webhook/API tests, privacy/refund/receipt/tax review 전까지 금지다.
다음 담당자 인수 사항: Next no-approval candidate is TASK-119 staging deploy preflight checklist. It must not deploy, mutate env vars, mutate external project settings, or publish a public URL.

## 증거

- `agents/project/MEMBERSHIP-PAYMENT-RECOGNITION-DECISION-PACKET.json`
- `agents/project/MEMBERSHIP-PAYMENT-RECOGNITION-DECISION-PACKET.md`
- `scripts/membership_payment_recognition_decision_gate.py`
- `tests/unit/test_membership_payment_recognition_decision_gate.py`
- `agents/project/MEMBERSHIP-PRODUCTION-IMPLEMENTATION-PLAN.md`
- `agents/project/initiatives/TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING.md`
- `agents/lead_engineer/tasks/TASK-087-web-deploy-membership-gating.md`

## 검증

- `python -m json.tool agents\project\MEMBERSHIP-PAYMENT-RECOGNITION-DECISION-PACKET.json`
- `python scripts\membership_payment_recognition_decision_gate.py --check`
- `python -m pytest tests\unit\test_membership_payment_recognition_decision_gate.py -q`
- `python scripts\membership_payment_policy_gate.py --check`
- `python scripts\build_task_index.py --check`
- `python scripts\generate_views.py --check`
- `python scripts\generate_report_views.py --check`
- `python scripts\work_schema_gate.py --items --check`
- `python scripts\check_agent_docs.py`
- `git diff --check`

## 리뷰

- Regulatory Admin self-review: The packet uses official/primary source checks and does not present legal, tax, accounting, securities, or payment-provider advice as a final conclusion.
- Backend Engineer perspective: The selected MVP path matches existing local manual/code-assisted flow and does not introduce bank/PG/Open Banking API dependencies.
- Compliance Officer perspective: Raw statements, full account numbers, unredacted identifiers, provider payloads, and real payment records remain outside repo artifacts.
- QA perspective: The local gate fails if Open Banking is selected for MVP, raw source persistence is allowed, Hometax/provider/source evidence is missing, or forbidden payment key names appear.

## Independent Audit

판정: 통과
- Same-session audit note: The task added decision/gate/test artifacts and handoff records only.
- No bank account, bank login, PG account, Open Banking account, credential, API call, real customer payment record, raw bank statement persistence, Supabase project, production database, deployment target, environment variable, secret, KIS/order/risk/prod surface, or legal/tax/accounting final advice boundary was crossed.

## 남은 이슈

- 실제 PG/가상계좌/Open Banking 자동화는 Owner 승인, 외부 계정/계약, credential, staging webhook/API tests, privacy/refund/receipt/tax review 전까지 금지다.
- 다음 no-approval 후보는 `TASK-119` staging deploy preflight checklist다.
