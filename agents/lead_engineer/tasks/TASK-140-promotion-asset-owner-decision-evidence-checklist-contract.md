---
type: task
id: TASK-140
display_id: TASK-140
task_uid: 5a1117a3-babe-4819-beb4-6ddf65500b5d
registered_at: 2026-06-20T01:51:10+09:00
created_at: 2026-06-20T01:51:10+09:00
updated_at: 2026-06-20T02:06:08+09:00
status: 완료
started_at: 2026-06-20T02:00:20+09:00
completed_at: 2026-06-20T02:06:08+09:00
owner: Doc Steward
assignees: [Doc Steward, Compliance Officer, QA, Marketing Growth]
priority: Medium
difficulty: 중
est_hours: 3
est_tokens: 35000
tags: [marketing, compliance, claims, review, owner-decision-evidence]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST
gate: local Owner decision evidence checklist contract only; no actual approval records, no approval evidence collection, no public approval, no final export, no SNS upload, no customer contact, no CRM/payment
trigger_meeting: Owner goal continuation 2026-06-20
audit_log: AUDIT-2026-06-20-014
created: 2026-06-20
actual_hours: 1
actual_tokens: 24000
---

# TASK-140 Promotion Asset Owner Decision Evidence Checklist Contract

작업 ID: TASK-140
상태: 완료
Owner: Doc Steward
요청 시각: 2026-06-20T01:51:10+09:00
기록 시각: 2026-06-20T01:51:10+09:00
요청자: Owner goal continuation
수행자: Doc Steward, Compliance Officer, QA, Marketing Growth
의도: TASK-139 audit/readiness preview의 evidence gaps를 future Owner/R3 review용 local checklist contract로 정리한다.
대상: local evidence checklist contract JSON/Markdown, decision type evidence map, acceptance criteria, stale-evidence triggers, forbidden fields, gate, focused tests
방법: `PROMOTION-ASSET-OWNER-DECISION-QUEUE-AUDIT-PREVIEW`를 입력으로 actual approval/evidence collection 없이 checklist contract만 만든다.
감사 로그: AUDIT-2026-06-20-014

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST`
- Depends on: `TASK-139`

## 범위

포함:

- Local evidence checklist contract only.
- Source artifact path/hash.
- Decision type to required evidence map.
- Accountable role and review role for each evidence item.
- Acceptance criteria and stale-evidence triggers.
- Forbidden fields and blocked action flags.
- Local gate and focused tests.

제외:

- Actual Owner approval records or signatures.
- Actual approval evidence collection.
- Public approval or publication clearance.
- Legal, tax, securities, or regulatory final advice.
- Final PDF/PPTX binary export.
- Public landing page deployment.
- SNS upload or live publishing.
- Customer contact, CRM, payment, billing, support execution.
- External account action, OAuth, secret/token handling.
- KIS/order/risk/prod/deploy changes.

## 완료 조건

- [x] Owner decision evidence checklist contract exists as local JSON/Markdown.
- [x] Contract includes source hash, decision type evidence map, role ownership,
  acceptance criteria, stale-evidence triggers, and forbidden fields.
- [x] Gate rejects actual approval records, approval evidence collection,
  publication approval, final advice, missing blocked-action flags,
  secret/customer keys, CRM/payment fields, and final/public export fields.
- [x] Focused tests pass.

## 완료 내용

완료 시각: 2026-06-20T02:06:08+09:00
기록 시각: 2026-06-20T02:06:08+09:00
수행자: Doc Steward + Compliance Officer + QA + Marketing Growth perspective (Codex)
검토자: Doc Steward + Compliance Officer + QA perspective (same-session self-review)
감사 로그: AUDIT-2026-06-20-015
실측 비용 (시간): 1h
실측 비용 (LLM 토큰): 24000
요청: Owner goal continuation에 따라 TASK-139 audit/readiness preview의 evidence gaps를 future Owner/R3 review용 local checklist contract로 정리한다.

작업:

- `PROMOTION-ASSET-OWNER-DECISION-QUEUE-AUDIT-PREVIEW` source hash를 기록한 local evidence checklist contract JSON/Markdown을 만들었다.
- 9개 decision type을 required evidence, accountable role, review roles, acceptance criteria, stale-evidence triggers, forbidden fields로 매핑했다.
- 모든 checklist item에 `actual_approval_evidence_collected=false`, `actual_approval_recorded=false`, `action_permitted_now=false`와 public/final/export/external/customer/CRM-payment/secret/final-advice/KIS blocked flags를 고정했다.
- `promotion_asset_owner_decision_evidence_checklist_gate.py`와 focused tests를 추가해 source drift, missing boundary, missing item, evidence count drift, actual evidence collection flag, public-use unblock, forbidden approval key, platform/live flag를 차단했다.

결과:

- TASK-140 완료.
- `TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST` 완료.
- `TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-AUDIT-PREVIEW`와 `TASK-141`을 다음 local-only audit preview 후보로 등록했다.

변경 파일:

- `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST-CONTRACT.json`
- `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST-CONTRACT.md`
- `scripts/promotion_asset_owner_decision_evidence_checklist_gate.py`
- `tests/unit/test_promotion_asset_owner_decision_evidence_checklist_gate.py`

검증:

- `python -m json.tool agents\project\PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST-CONTRACT.json` -> pass
- `python scripts\promotion_asset_owner_decision_evidence_checklist_gate.py --check` -> pass
- `python -m pytest tests\unit\test_promotion_asset_owner_decision_evidence_checklist_gate.py -q` -> 13 passed
- `python -m py_compile scripts\promotion_asset_owner_decision_evidence_checklist_gate.py` -> pass

남은 경계:

- Actual Owner approval records, actual approval evidence collection, public approval, legal/tax/securities final advice, final PDF/PPTX binary export, public landing page, SNS upload, customer contact, CRM/payment, paid ads, support/refund execution, external account action, OAuth, platform API call, secret/customer data, KIS/order/risk/prod/deploy changes remain Owner/R3.

## 완료 기록

결과:

- `PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST-CONTRACT.json`/`.md` created.
- `promotion_asset_owner_decision_evidence_checklist_gate.py` and focused tests created.
- `TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST` completed.
- `TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-AUDIT-PREVIEW` and `TASK-141` registered as the next local-only slice.

## 증거

- `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST-CONTRACT.json`
- `agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST-CONTRACT.md`
- `scripts/promotion_asset_owner_decision_evidence_checklist_gate.py`
- `tests/unit/test_promotion_asset_owner_decision_evidence_checklist_gate.py`
- `agents/project/initiatives/TASKSET-MARKETING-ASSET-OWNER-DECISION-EVIDENCE-AUDIT-PREVIEW.md`
- `agents/lead_engineer/tasks/TASK-141-promotion-asset-owner-decision-evidence-checklist-audit-preview.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-20-008.md`

## 리뷰

- Reviewers: Doc Steward + Compliance Officer + QA perspective.
- Same-session self-review: yes, Codex performed implementation and review in one session.
- Evidence: focused gate and tests above.

## Independent Audit

- 기록 시각: 2026-06-20T02:06:08+09:00
- 수행자: Independent Auditor perspective (same Codex session)
- 대상: TASK-140 artifacts and gate/test outputs
- 방법: source hash verification, forbidden key scan, live flag scan, decision type coverage, evidence count alignment, blocked action flag validation, focused regression tests
- 판정: 통과
- 근거:
  - Source hash is recorded and recalculated by the gate.
  - All 9 decision types are covered by checklist items.
  - Required evidence counts match the TASK-139 evidence gap scan.
  - Every checklist item keeps `actual_approval_evidence_collected=false`, `actual_approval_recorded=false`, and `action_permitted_now=false`.
  - Every checklist item keeps public use, final export, external action, customer contact, CRM/payment, secret material, final advice, and KIS/order/risk/prod/deploy blocked.
  - Focused tests reject source drift, missing boundary, summary drift, missing required fields, missing item coverage, approval/action flags, stale evidence omissions, forbidden approval keys, and live platform flags.

## 검증

- `python -m json.tool agents\project\PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST-CONTRACT.json` pass
- `python scripts\promotion_asset_owner_decision_evidence_checklist_gate.py --check` pass
- `python -m pytest tests\unit\test_promotion_asset_owner_decision_evidence_checklist_gate.py -q` 13 passed
- `python -m py_compile scripts\promotion_asset_owner_decision_evidence_checklist_gate.py` pass
