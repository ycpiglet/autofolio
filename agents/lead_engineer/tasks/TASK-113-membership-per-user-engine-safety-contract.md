---
type: task
id: TASK-113
display_id: TASK-113
task_uid: eaa406bb-fdd7-42cd-8583-549f04562114
registered_at: 2026-06-19T18:29:43+09:00
created_at: 2026-06-19T18:29:43+09:00
started_at: 2026-06-19T19:46:50+09:00
updated_at: 2026-06-19T19:46:50+09:00
completed_at: 2026-06-19T19:46:50+09:00
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, Backend Engineer, Compliance Officer, QA]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 22000
tags: [membership, engine-safety, multitenant, contract, production-readiness]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-PROD-READINESS
gate: local contract and validation only; no engine/order/risk behavior change, no production DB, no deploy, no secret, no KIS/order/risk/prod change
trigger_meeting: Owner goal continuation 2026-06-19
audit_log: AUDIT-2026-06-19-024
created: 2026-06-19
---

# TASK-113 Membership per-user engine safety contract

작업 ID: TASK-113
상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-19T18:29:43+09:00
기록 시각: 2026-06-19T19:46:50+09:00
완료 시각: 2026-06-19T19:46:50+09:00
요청자: Owner goal continuation
수행자: Lead Engineer + Backend Engineer + Compliance Officer + QA perspective (Codex)
검토자: Lead Engineer self-review + Backend Engineer boundary perspective + Compliance boundary perspective + QA perspective
협업 waiver: Same-session scoped task with named role perspectives; no engine, order, risk, KIS, production DB, deploy, or secret boundary crossed.
routing_ref: TASKSET-MEMBERSHIP-PROD-READINESS / TASK-113
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 local reversible implementation; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.5h
실측 비용 (LLM 토큰): unknown
의도: user_id 단위 engine state, queue, kill switch, risk limit, order intent 격리의 production 계약을 local contract/gate로 고정한다.
대상: per-user engine safety contract, local validation gate, readiness checklist, TASK-087 handoff map
방법: engine/order/risk/KIS runtime behavior를 변경하지 않고 JSON/Markdown contract와 stdlib-only gate/test로 tenant isolation invariant를 검증한다.
감사 로그: AUDIT-2026-06-19-024

## 목표

Local per-user engine/safety contract defines tenant-owned runtime state and
launch-blocking isolation invariants before any multi-user live-readiness work.

## 완료 조건

- [x] Contract maps engine state, queue, kill switch, risk limit, and order intent to user scope.
- [x] Gate validates required isolation invariants.
- [x] TASK-087 distinguishes contract readiness from production implementation.
- [x] No order path, risk gate, KIS broker, or production runtime behavior is changed.
- [x] Focused tests and governance gates pass.

## 완료 기록

완료일: 2026-06-19
결과: TASK-087의 per-user engine/safety isolation gap을 production runtime 변경 없이 R2 contract/gate로 좁혔다. Readiness API는 `per_user_engine_safety_contract`를 pass로 표시하지만 실제 engine/order/risk/KIS implementation은 여전히 `per_user_engine_safety` block과 `can_launch=false`로 남긴다.
변경 파일: `agents/project/MEMBERSHIP-ENGINE-SAFETY-CONTRACT.json`, `agents/project/MEMBERSHIP-ENGINE-SAFETY-CONTRACT.md`, `scripts/membership_engine_safety_gate.py`, `tests/unit/test_membership_engine_safety_gate.py`, `app/services/membership_readiness.py`, `tests/api/test_membership.py`, membership planning/taskset records.
이슈: contract는 design evidence일 뿐 production schema, per-user engine worker, KIS credential scoping, live execution, or staging dry-run evidence가 아니다.
다음 담당자 인수 사항: TASKSET-MEMBERSHIP-PROD-READINESS의 local policy/contract/matrix slice는 완료됐고, 다음은 TASK-087의 staging Supabase/RLS plan, payment recognition decision, production secret store implementation plan, or deploy evidence 중 R2/R3 경계를 골라야 한다.

## 완료 내용

- Added per-user engine/safety contract JSON/Markdown covering engine state, engine run queue, trade conditions, safety flags, risk limits, circuit breakers, append-only order intents, order/execution logs, notifications, worker context, and launch gates.
- Added local validation gate for user_id-owned runtime surfaces, live-execution block, append-only order-intent/log surfaces, worker user context, forbidden global fallbacks, and fail-closed behavior.
- Added readiness API visibility for `per_user_engine_safety_contract` while keeping `per_user_engine_safety` blocked.
- Updated production contract, TASK-087, membership access plan, initiative/taskset records, STATUS, AUDIT, BRIEF, and generated views.

## 증거

- `agents/project/MEMBERSHIP-ENGINE-SAFETY-CONTRACT.json`
- `agents/project/MEMBERSHIP-ENGINE-SAFETY-CONTRACT.md`
- `scripts/membership_engine_safety_gate.py`
- `tests/unit/test_membership_engine_safety_gate.py`
- `app/services/membership_readiness.py`
- `tests/api/test_membership.py`
- `agents/lead_engineer/reports/BRIEF-2026-06-19-023.md`

## 리뷰

- Lead Engineer self-review: scope is local contract/gate only and does not change runtime execution.
- Backend Engineer perspective: current global surfaces are mapped to future user_id-owned surfaces without applying schema or code changes.
- Compliance perspective: live/member execution remains blocked until R3 approval, KIS terms, per-user credentials, and staging evidence exist.
- QA perspective: unit tests cover valid contract, missing user scope, live-execution allowance, append-only order intent enforcement, and missing fail-closed behavior.

## Independent Audit

판정: 통과

Same-session audit note: this is readiness-contract evidence, not production engine isolation or live-execution certification.

## 검증

- `python scripts\membership_engine_safety_gate.py --check`
- `.venv\Scripts\python.exe -m pytest tests\unit\test_membership_engine_safety_gate.py tests\api\test_membership.py -q` — 21 passed, 2 warnings.
- Broader generated/governance gates are recorded in `AUDIT-2026-06-19-024`.
