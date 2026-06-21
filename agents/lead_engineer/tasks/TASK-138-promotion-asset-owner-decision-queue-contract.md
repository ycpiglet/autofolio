---
type: task
id: TASK-138
display_id: TASK-138
task_uid: dbb21134-6931-4486-82ef-5f9e0034d1c9
registered_at: 2026-06-20T01:12:59+09:00
created_at: 2026-06-20T01:12:59+09:00
updated_at: 2026-06-20T01:36:54+09:00
status: 완료
started_at: 2026-06-20T01:30:10+09:00
completed_at: 2026-06-20T01:36:54+09:00
owner: Compliance Officer
assignees: [Compliance Officer, QA, Marketing Growth, Doc Steward]
priority: Medium
difficulty: 중
est_hours: 3
est_tokens: 35000
tags: [marketing, compliance, claims, review, owner-decision-queue]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-ASSET-OWNER-DECISION-QUEUE
gate: local Owner decision queue contract only; no actual approval records, no public approval, no final export, no SNS upload, no customer contact, no CRM/payment
trigger_meeting: Owner goal continuation 2026-06-20
audit_log: AUDIT-2026-06-20-011
created: 2026-06-20
actual_hours: 1
actual_tokens: 22000
---

# TASK-138 Promotion Asset Owner Decision Queue Contract

작업 ID: TASK-138
상태: 완료
Owner: Compliance Officer
요청 시각: 2026-06-20T01:12:59+09:00
기록 시각: 2026-06-20T01:12:59+09:00
요청자: Owner goal continuation
수행자: Compliance Officer, QA, Marketing Growth, Doc Steward
의도: TASK-137 Owner review packet 이후 future Owner decisions를 기록할 local queue contract를 만든다.
대상: local Owner decision queue contract JSON/Markdown, state model, required evidence, forbidden fields, gate, focused tests
방법: `PROMOTION-ASSET-OWNER-REVIEW-PACKET`을 입력으로 actual approval 없이 decision queue contract만 정의한다.
감사 로그: AUDIT-2026-06-20-011

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-ASSET-OWNER-DECISION-QUEUE`
- Depends on: `TASK-137`

## 범위

포함:

- Local decision queue contract only.
- Source artifact path/hash.
- Allowed local states for pending, evidence-required, Owner-decision-needed,
  approved-record-ready-for-future-R3, rejected, withdrawn, and archived.
- Required evidence for each future decision type.
- Forbidden fields and blocked action flags.
- Local gate and focused tests.

제외:

- Actual Owner approval records.
- Public approval or publication clearance.
- Legal, tax, securities, or regulatory final advice.
- Final PDF/PPTX binary export.
- Public landing page deployment.
- SNS upload or live publishing.
- Customer contact, CRM, payment, billing, support execution.
- External account action, OAuth, secret/token handling.
- KIS/order/risk/prod/deploy changes.

## 완료 조건

- [x] Owner decision queue contract exists as local JSON/Markdown.
- [x] Contract includes source hash, allowed states, decision types, required
  evidence, and forbidden fields.
- [x] Gate rejects actual approval records, publication approval, final advice,
  missing blocked-action flags, secret/customer keys, CRM/payment fields, and
  final/public export fields.
- [x] Focused tests pass.

## 완료 내용

완료 시각: 2026-06-20T01:36:54+09:00
기록 시각: 2026-06-20T01:36:54+09:00
수행자: Compliance Officer + QA + Marketing Growth perspective (Codex)
검토자: Compliance Officer + QA + Marketing Growth perspective (same-session self-review)
감사 로그: AUDIT-2026-06-20-011
실측 비용 (시간): 1h
실측 비용 (LLM 토큰): 22000
요청: Owner goal continuation에 따라 TASK-137 Owner review packet 이후 future Owner decisions를 기록할 local queue contract를 만든다.

작업:

- `PROMOTION-ASSET-OWNER-REVIEW-PACKET` source hash를 기록한 local decision queue contract JSON/Markdown을 만들었다.
- public landing use, final PDF/PPTX export, SNS upload, customer contact, CRM/payment setup, paid ads, external account action, legal/tax/securities reliance 등 9개 decision type을 Owner/R3 required로 고정했다.
- decision queue required fields, allowed local states, seed decision records, forbidden fields, forbidden outputs, handoff boundary를 machine-readable 형태로 정의했다.
- `promotion_asset_owner_decision_queue_contract_gate.py`와 focused tests를 추가해 approval/export/customer/payment/platform/secret/final-advice drift를 차단했다.

결과:

- TASK-138 완료.
- `TASKSET-MARKETING-ASSET-OWNER-DECISION-QUEUE` 완료.
- `TASKSET-MARKETING-ASSET-OWNER-DECISION-AUDIT-PREVIEW`와 `TASK-139`를 다음 local-only audit/readiness preview 후보로 등록했다.

변경 파일:

- `agents/project/PROMOTION-ASSET-OWNER-DECISION-QUEUE-CONTRACT.json`
- `agents/project/PROMOTION-ASSET-OWNER-DECISION-QUEUE-CONTRACT.md`
- `scripts/promotion_asset_owner_decision_queue_contract_gate.py`
- `tests/unit/test_promotion_asset_owner_decision_queue_contract_gate.py`

검증:

- `python -m json.tool agents\project\PROMOTION-ASSET-OWNER-DECISION-QUEUE-CONTRACT.json` -> pass
- `python scripts\promotion_asset_owner_decision_queue_contract_gate.py --check` -> pass
- `python -m pytest tests\unit\test_promotion_asset_owner_decision_queue_contract_gate.py -q` -> 13 passed
- `python -m py_compile scripts\promotion_asset_owner_decision_queue_contract_gate.py` -> pass

남은 경계:

- Actual Owner approval records, public approval, legal/tax/securities final advice, final PDF/PPTX binary export, public landing page, SNS upload, customer contact, CRM/payment, paid ads, support/refund execution, external account action, OAuth, platform API call, secret/customer data, KIS/order/risk/prod/deploy changes remain Owner/R3.

## 완료 기록

결과:

- `PROMOTION-ASSET-OWNER-DECISION-QUEUE-CONTRACT.json`/`.md` created.
- `promotion_asset_owner_decision_queue_contract_gate.py` and focused tests created.
- `TASKSET-MARKETING-ASSET-OWNER-DECISION-QUEUE` completed.
- `TASKSET-MARKETING-ASSET-OWNER-DECISION-AUDIT-PREVIEW` and `TASK-139` registered as the next local-only slice.

## 증거

- `agents/project/PROMOTION-ASSET-OWNER-DECISION-QUEUE-CONTRACT.json`
- `agents/project/PROMOTION-ASSET-OWNER-DECISION-QUEUE-CONTRACT.md`
- `scripts/promotion_asset_owner_decision_queue_contract_gate.py`
- `tests/unit/test_promotion_asset_owner_decision_queue_contract_gate.py`
- `agents/project/initiatives/TASKSET-MARKETING-ASSET-OWNER-DECISION-AUDIT-PREVIEW.md`
- `agents/lead_engineer/tasks/TASK-139-promotion-asset-owner-decision-queue-audit-preview.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-20-006.md`

## 리뷰

- Reviewers: Compliance Officer + QA + Marketing Growth perspective.
- Same-session self-review: yes, Codex performed implementation and review in one session.
- Evidence: focused gate and tests above.

## Independent Audit

- 기록 시각: 2026-06-20T01:36:54+09:00
- 수행자: Independent Auditor perspective (same Codex session)
- 대상: TASK-138 artifacts and gate/test outputs
- 방법: source hash verification, forbidden key scan, live flag scan, decision type coverage, seed record blocked flag coverage, focused regression tests
- 판정: 통과
- 근거:
  - Source hash is recorded and recalculated by the gate.
  - All 9 Owner/R3 decision types are covered by seed decision records.
  - All allowed states have `live_action=false` and `actual_approval_recorded=false`.
  - Seed records keep public use, final export, external action, customer contact, CRM/payment, secret material, final advice, and KIS/order/risk/prod/deploy blocked.
  - Focused tests reject source drift, missing boundaries, missing queue fields, live states, missing decision coverage, unblocked actions, forbidden approval keys, and live platform flags.

## 검증

- `python -m json.tool agents\project\PROMOTION-ASSET-OWNER-DECISION-QUEUE-CONTRACT.json` pass
- `python scripts\promotion_asset_owner_decision_queue_contract_gate.py --check` pass
- `python -m pytest tests\unit\test_promotion_asset_owner_decision_queue_contract_gate.py -q` 13 passed
- `python -m py_compile scripts\promotion_asset_owner_decision_queue_contract_gate.py` pass
