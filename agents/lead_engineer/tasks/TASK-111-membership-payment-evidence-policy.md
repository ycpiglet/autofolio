---
type: task
id: TASK-111
display_id: TASK-111
task_uid: 63665749-9763-4ac7-8c44-4207121b12c2
registered_at: 2026-06-19T18:29:43+09:00
created_at: 2026-06-19T18:29:43+09:00
started_at: 2026-06-19T18:29:43+09:00
updated_at: 2026-06-19T18:29:43+09:00
completed_at: 2026-06-19T18:29:43+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, Compliance Officer, QA, Lead Engineer]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 18000
tags: [membership, payment-evidence, policy, quality-gate, production-readiness]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-PROD-READINESS
gate: local policy and validation only; no production DB, no deploy, no bank/payment API, no real payment record, no secret, no KIS/order/risk/prod change
trigger_meeting: Owner goal continuation 2026-06-19
audit_log: AUDIT-2026-06-19-021
created: 2026-06-19
---

# TASK-111 Membership payment evidence policy gate

작업 ID: TASK-111
상태: 완료
Owner: Backend Engineer
Owner: Backend Engineer
요청 시각: 2026-06-19T18:29:43+09:00
기록 시각: 2026-06-19T18:29:43+09:00
완료 시각: 2026-06-19T18:29:43+09:00
요청자: Owner goal continuation
수행자: Backend Engineer + Compliance Officer + QA + Lead Engineer perspective (Codex)
검토자: Backend Engineer self-review + Compliance boundary perspective + QA perspective + Lead Engineer perspective
협업 waiver: Same-session scoped task with named role perspectives; no external mutation or production boundary crossed.
협업 waiver: 단일 세션 범위 작업. Compliance/QA/Lead 관점 검토를 같은 세션에서 기록했고, 실제 결제/은행/API/secret/production 경계는 건드리지 않았다.
routing_ref: TASKSET-MEMBERSHIP-PROD-READINESS / TASK-111
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 local reversible implementation; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.5h
실측 비용 (LLM 토큰): unknown
의도: verified signup의 manual/code-assisted 입금 확인에서 무엇을 보존하고 무엇을 금지할지 local policy와 gate로 고정한다.
대상: payment evidence policy asset, local validation gate, readiness checklist, TASK-087 handoff map
방법: JSON/Markdown policy를 만들고 stdlib-only gate와 unit/API tests로 최소 보존 필드, 금지 evidence, redaction, audit invariant를 검증한다.
감사 로그: AUDIT-2026-06-19-021

## 목표

Local payment evidence policy and gate define minimal retained fields, forbidden
evidence, redaction rules, and audit invariants for verified signup.

## 범위

포함:

- `MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json` machine-readable policy.
- Human-readable policy summary.
- `scripts/membership_payment_policy_gate.py --check`.
- Unit tests for policy acceptance and failure modes.
- Readiness API item `payment_evidence_policy`.
- TASK-087 and membership planning records updated with the policy evidence.

제외:

- Production DB/Supabase/RLS apply.
- Real bank/payment API, PG, open-banking, virtual account.
- Real customer payment evidence storage.
- Refund, receipt, tax, accounting conclusion.
- External deploy.
- Secret handling.
- KIS/order/risk/prod path change.

## 완료 조건

- [x] Policy lists allowed evidence sources and forbids raw/private evidence.
- [x] Policy limits retained fields to minimal masked audit fields.
- [x] Gate fails if raw source persistence or redaction rules are missing.
- [x] Owner-visible readiness API shows the policy as pass while launch remains blocked.
- [x] TASK-087 is updated to distinguish policy readiness from production payment recognition.
- [x] Focused tests and governance gates pass.

## 완료 기록

완료일: 2026-06-19
결과: TASK-087의 `payment evidence retention` gap을 production apply 없이 R2 policy/gate로 좁혔다. 외부 paid launch는 여전히 production DB/RLS, recognition method, refund/receipt/tax boundary, and staging privacy tests가 필요하다.
변경 파일: `agents/project/MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json`, `agents/project/MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.md`, `scripts/membership_payment_policy_gate.py`, `tests/unit/test_membership_payment_policy_gate.py`, `app/services/membership_readiness.py`, `tests/api/test_membership.py`, membership planning/taskset records.
이슈: policy는 design evidence일 뿐 실제 payment operation approval이나 legal/tax review가 아니다.
다음 담당자 인수 사항: TASK-112에서 production secret/token 보존 정책을 같은 방식으로 local policy/gate로 분리한다.

## 완료 내용

- Added membership payment evidence policy JSON and Markdown asset.
- Added local validation gate for allowed evidence sources, forbidden evidence,
  retained field allowlist, redaction rules, audit invariants, and launch gates.
- Added readiness API visibility for `payment_evidence_policy`.
- Registered TASKSET-MEMBERSHIP-PROD-READINESS follow-up work.

## 증거

- `agents/project/MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json`
- `agents/project/MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.md`
- `scripts/membership_payment_policy_gate.py`
- `tests/unit/test_membership_payment_policy_gate.py`
- `app/services/membership_readiness.py`
- `tests/api/test_membership.py`
- `agents/lead_engineer/reports/BRIEF-2026-06-19-020.md`

## 완료 내용

- Payment evidence policy JSON/Markdown을 추가해 허용 source, 금지 evidence, 최소 보존 필드, redaction, audit invariant를 명시했다.
- `membership_payment_policy_gate.py`와 unit/API tests로 policy readiness를 검증하고 readiness API에 `payment_evidence_policy` 항목을 노출했다.
- TASK-087, taskset, initiative, BRIEF, review 기록에 production payment recognition과 local policy readiness의 차이를 남겼다.

## 증거

- `agents/project/MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json`
- `agents/project/MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.md`
- `scripts/membership_payment_policy_gate.py`
- `tests/unit/test_membership_payment_policy_gate.py`
- `tests/api/test_membership.py`
- `agents/lead_engineer/reports/BRIEF-2026-06-19-020.md`
- `reviews/REVIEW-2026-06-19-membership-prod-readiness-taskset.md`

## 리뷰

- Backend Engineer self-review: gate is local and stdlib-only; it does not connect to external systems.
- Compliance perspective: raw statements, full account numbers, identifiers, payment secrets, and private freeform notes are explicitly forbidden.
- QA perspective: unit tests cover valid policy, raw-source persistence rejection, and missing redaction rejection.
- Lead Engineer perspective: this advances TASK-087 without crossing production/payment boundaries.

## Independent Audit

판정: 통과

Same-session audit note: this is readiness-policy evidence, not production payment compliance certification.

## 검증

- `python scripts\membership_payment_policy_gate.py --check`
- `.venv\Scripts\python.exe -m pytest tests\unit\test_membership_payment_policy_gate.py tests\api\test_membership.py -q`
- broader governance gates recorded in `AUDIT-2026-06-19-021`
