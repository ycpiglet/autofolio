---
type: task
id: TASK-146
display_id: TASK-146
task_uid: e09ffeaa-9657-4864-84a3-2b37fe8b9e68
registered_at: 2026-06-20T03:34:53+09:00
created_at: 2026-06-20T03:34:53+09:00
updated_at: 2026-06-20T03:56:06+09:00
started_at: 2026-06-20T03:47:08+09:00
completed_at: 2026-06-20T03:56:06+09:00
status: 완료
owner: Doc Steward
assignees: [Doc Steward, QA, Compliance Officer, Marketing Growth]
priority: Medium
difficulty: 중
est_hours: 3
est_tokens: 35000
tags: [marketing, compliance, claims, review, owner-decision-evidence, freshness, refresh-queue, work-order]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT
gate: local Owner decision evidence refresh work-order contract only; no actual evidence refresh execution, no approval evidence collection, no approval records, no public approval, no final export, no SNS upload, no customer contact, no CRM/payment
trigger_meeting: Owner goal continuation 2026-06-20
audit_log: AUDIT-2026-06-20-026
created: 2026-06-20
actual_hours: 1
actual_tokens: 42000
---

# TASK-146 Promotion Asset Owner Decision Evidence Refresh Work-order Contract

작업 ID: TASK-146
상태: 완료
Owner: Doc Steward
요청 시각: 2026-06-20T03:34:53+09:00
기록 시각: 2026-06-20T03:34:53+09:00
요청자: Owner goal continuation
수행자: Doc Steward, QA, Compliance Officer, Marketing Growth
의도: TASK-145 refresh queue audit/readiness preview 이후 future evidence refresh work를 실행하지 않고 local work-order contract로 분해한다.
대상: local refresh work-order contract JSON/Markdown, work-order record map, precondition/proof requirement map, expiry trigger map, blocked action scan, gate, focused tests
방법: `PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-QUEUE-AUDIT-PREVIEW`를 입력으로 actual evidence refresh execution이나 approval evidence collection 없이 work-order contract만 만든다.
감사 로그: AUDIT-2026-06-20-026

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT`
- Depends on: `TASK-145`

## 범위

포함:

- Local refresh work-order contract only.
- Source artifact path/hash.
- Work-order records for the 9 refresh queue records.
- Accountable role and review role for each future local work order.
- Preconditions, proof requirements, expiry/stale triggers, archive/rollback expectation, and blocked action flags.
- Local gate and focused tests.

제외:

- Actual evidence refresh execution.
- Actual Owner approval records or signatures.
- Actual approval evidence collection.
- Public approval or publication clearance.
- Legal, tax, securities, or regulatory final advice.
- Final PDF/PPTX binary export.
- Public landing page deployment.
- SNS upload or live publishing.
- Customer contact, CRM, payment, billing, support execution.
- External account action, OAuth, secret/token handling, platform API call.
- KIS/order/risk/prod/deploy changes.

## 완료 조건

- [x] Owner decision evidence refresh work-order contract exists as local JSON/Markdown.
- [x] Contract includes source hash, work-order records, preconditions, proof
  requirements, expiry/stale triggers, archive/rollback expectation, role
  ownership, and blocked action flags.
- [x] Gate rejects actual evidence refresh execution, actual approval evidence
  collection, actual approval records, publication approval, final advice,
  missing blocked-action flags, secret/customer keys, CRM/payment fields, and
  final/public export fields.
- [x] Focused tests pass.

## 완료 내용

완료 시각: 2026-06-20T03:56:06+09:00
기록 시각: 2026-06-20T03:56:06+09:00
수행자: Doc Steward + QA + Compliance Officer + Marketing Growth perspective (Codex)
검토자: QA + Doc Steward + Independent Auditor perspective (same-session self-review)
감사 로그: AUDIT-2026-06-20-027
실측 비용 (시간): 1h
실측 비용 (LLM 토큰): 42000
요청: Owner goal continuation에 따라 TASK-145 refresh queue audit/readiness preview 이후 future evidence refresh work를 실행하지 않고 local work-order contract로 분해한다.

작업:

- `PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-QUEUE-AUDIT-PREVIEW` source hash를 기록한 local refresh work-order contract JSON/Markdown을 만들었다.
- 9개 refresh queue record를 future local work order로 매핑하고 accountable role, review roles, preconditions, proof requirements, expiry triggers, archive/rollback expectation, blocked action flags를 기록했다.
- 5개 work-order state와 8개 invalidating trigger-to-work-order map을 만들고 모든 state/trigger를 `live_action=false`, `refresh_execution_allowed=false`, `actual_refresh_executed=false`, `action_permitted_now=false`로 고정했다.
- `promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py`와 focused tests를 추가해 source drift, missing boundary, summary drift, missing work-order record, actual refresh execution, actual approval/evidence/action flags, state/live flag, missing preconditions/proof requirements, missing trigger map, source count mismatch, blocked-action scan drift, forbidden approval/secret/final-output keys, live platform flag를 차단했다.

결과:

- TASK-146 완료.
- `TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT` 완료.
- `TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-AUDIT-PREVIEW`와 `TASK-147`을 다음 local-only audit/readiness preview 후보로 등록했다.

변경 파일:

- `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT.json`
- `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT.md`
- `scripts/promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py`
- `tests/unit/test_promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py`

검증:

- `python -m json.tool agents\project\PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT.json` -> pass
- `python scripts\promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py --check` -> pass
- `python -m pytest tests\unit\test_promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py -q` -> 17 passed
- `python -m py_compile scripts\promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py` -> pass
- `python scripts\promotion_asset_owner_decision_evidence_refresh_queue_audit_preview_gate.py --check` -> pass

남은 경계:

- Actual evidence refresh execution, actual Owner approval records, actual approval evidence collection, public approval, legal/tax/securities final advice, final PDF/PPTX binary export, public landing page, SNS upload, customer contact, CRM/payment, paid ads, support/refund execution, external account action, OAuth, platform API call, secret/customer data, KIS/order/risk/prod/deploy changes remain Owner/R3.

## 완료 기록

결과:

- `PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT.json`/`.md` created.
- `promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py` and focused tests created.
- `TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT` completed.
- `TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-AUDIT-PREVIEW` and `TASK-147` registered as the next local-only slice.

## 증거

- `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT.json`
- `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT.md`
- `scripts/promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py`
- `tests/unit/test_promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py`
- `agents/project/initiatives/TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-AUDIT-PREVIEW.md`
- `agents/lead_engineer/tasks/TASK-147-promotion-asset-owner-decision-evidence-refresh-work-order-audit-preview.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-20-014.md`

## 리뷰

- Reviewers: QA + Doc Steward + Independent Auditor perspective.
- Same-session self-review: yes, Codex performed implementation and review in one session.
- Evidence: focused gate and tests above.

## Independent Audit

- 기록 시각: 2026-06-20T03:56:06+09:00
- 수행자: Independent Auditor perspective (same Codex session)
- 대상: TASK-146 artifacts and gate/test outputs
- 방법: source hash verification, forbidden key scan, live flag scan, work-order coverage, precondition/proof requirement coverage, work-order state safety, invalidating trigger map coverage, blocked action scan, focused regression tests
- 판정: 통과
- 근거:
  - Source hash is recorded and recalculated by the gate.
  - All 9 source refresh queue records and decision types are covered by work-order records.
  - All 5 source queue safety states are represented as local work-order states.
  - All 8 source invalidating trigger entries are mapped to local blocked work-order states.
  - Every work-order record keeps `actual_refresh_executed=false`, `refresh_execution_allowed=false`, `actual_approval_evidence_collected=false`, `actual_approval_recorded=false`, and `action_permitted_now=false`.
  - Every work-order record includes local preconditions, proof requirements, expiry triggers, and archive/rollback requirement.
  - Blocked action scan covers actual refresh execution, approval evidence collection, public use, final export, SNS upload, external action, customer contact, CRM/payment, secret material, final advice, and KIS/order/risk/prod/deploy.
  - Focused tests reject source drift, missing boundaries, summary drift, missing work-order coverage, refresh/action flags, state/live flags, missing preconditions/proof requirements, missing trigger coverage, source count drift, blocked action scan drift, forbidden approval keys, and live platform flags.

## 검증

- `python -m json.tool agents\project\PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT.json` pass
- `python scripts\promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py --check` pass
- `python -m pytest tests\unit\test_promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py -q` 17 passed
- `python -m py_compile scripts\promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py` pass
- `python scripts\promotion_asset_owner_decision_evidence_refresh_queue_audit_preview_gate.py --check` pass
