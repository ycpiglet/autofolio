---
type: task
id: TASK-135
display_id: TASK-135
task_uid: 0dcbc25f-291b-4ef4-8283-8c12667b7f66
registered_at: 2026-06-20T00:25:10+09:00
created_at: 2026-06-20T00:25:10+09:00
updated_at: 2026-06-20T00:40:56+09:00
started_at: 2026-06-20T00:37:19+09:00
completed_at: 2026-06-20T00:40:56+09:00
status: 완료
owner: Compliance Officer
assignees: [Compliance Officer, Marketing Growth, QA, Doc Steward]
priority: Medium
difficulty: 중
est_hours: 3
actual_hours: 1
est_tokens: 35000
actual_tokens: 17000
tags: [marketing, compliance, claims, review, queue, assets]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-ASSET-REVIEW-QUEUE-FOUNDATION
gate: local review queue contract only; no public approval, no final advice, no final asset export, no SNS upload, no customer contact, no CRM/payment
trigger_meeting: Owner goal continuation 2026-06-20
audit_log: AUDIT-2026-06-20-005
created: 2026-06-20
---

# TASK-135 Promotion Asset Review Queue Contract

작업 ID: TASK-135
상태: 완료
Owner: Compliance Officer
요청 시각: 2026-06-20T00:25:10+09:00
기록 시각: 2026-06-20T00:40:56+09:00
완료 시각: 2026-06-20T00:40:56+09:00
요청자: Owner goal continuation
수행자: Compliance Officer, Marketing Growth, QA, Doc Steward
검토자: Compliance Officer, QA, Doc Steward perspective
실측 비용 (시간): 1h
실측 비용 (LLM 토큰): 17000
의도: TASK-134 claim matrix 이후 review queue state/record contract를 local-only로 정의한다.
대상: local review queue contract JSON/Markdown, item schema, allowed states, blocked fields, gate, focused tests
방법: `PROMOTION-ASSET-CLAIM-REVIEW-MATRIX`와 `PROMOTION-ASSET-PREVIEW-MANIFEST`를 입력으로 review queue item contract를 만든다.
감사 로그: AUDIT-2026-06-20-005

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-ASSET-REVIEW-QUEUE-FOUNDATION`
- Depends on: `TASK-134`

## 범위

포함:

- Local review queue contract only.
- Queue item fields for asset target, claim bucket, review owner, state,
  blockers, required evidence, rollback/archive notes, and next action.
- Allowed local states such as draft_classified, compliance_review_required,
  owner_review_required, qa_doc_review_required, blocked, withdrawn, and
  ready_for_future_owner_review.
- Forbidden fields for public URL, final export paths, customer identifiers,
  payment/CRM records, external upload IDs, and secrets.
- Local gate and focused tests.

제외:

- Public approval or publication clearance.
- Legal, tax, securities, or regulatory final advice.
- Final PDF/PPTX binary export.
- Public landing page deployment.
- SNS upload or live publishing.
- Customer contact, CRM, payment, billing, support execution.
- External account action, OAuth, secret/token handling.
- KIS/order/risk/prod/deploy changes.

## 완료 조건

- [x] Review queue contract exists as local JSON/Markdown.
- [x] Contract includes source hashes and allowed/blocked queue states.
- [x] Gate rejects publication approval, final advice, missing public-use
  blocker, secret/customer keys, CRM/payment fields, and final/public export
  fields.
- [x] Focused tests pass.

## 완료 내용

- `PROMOTION-ASSET-CLAIM-REVIEW-MATRIX`,
  `PROMOTION-ASSET-PREVIEW-MANIFEST`, and
  `PROMOTION-PUBLISHING-STATE-MACHINE` source hashes were recorded in
  `PROMOTION-ASSET-REVIEW-QUEUE-CONTRACT.json`.
- Local review queue states were defined with `live_action=false`:
  draft_classified, compliance_review_required, owner_review_required,
  qa_doc_review_required, ready_for_future_owner_review, blocked, and
  withdrawn_or_archived.
- Landing/PDF/PPTX/SNS target queue items now require blockers, evidence,
  assigned role, source hash, rollback/archive instruction, and blocked public
  use/final export/publication approval flags.
- A local gate and focused tests now reject source drift, missing queue fields,
  live-action states, forbidden public/live states, missing target coverage,
  public-use unblock, final output fields, secret/customer keys, CRM/payment
  fields, and platform/live flags.
- `TASKSET-MARKETING-ASSET-REVIEW-QUEUE-FOUNDATION` is complete and
  `TASK-136` is registered as the next no-Owner review queue audit-preview
  candidate.

## 완료 기록

결과:

- `PROMOTION-ASSET-REVIEW-QUEUE-CONTRACT.json`/`.md` created.
- `promotion_asset_review_queue_contract_gate.py` and focused tests created.
- Public approval, final legal/tax/securities advice, final PDF/PPTX export,
  SNS upload, customer contact, CRM/payment, external account action, OAuth,
  platform API calls, secrets, KIS/order/risk/prod, and deploy changes remain
  blocked.
- Next local slice: `TASK-136 Promotion Asset Review Queue Audit Preview`.

변경 파일:

- `agents/project/PROMOTION-ASSET-REVIEW-QUEUE-CONTRACT.json`
- `agents/project/PROMOTION-ASSET-REVIEW-QUEUE-CONTRACT.md`
- `scripts/promotion_asset_review_queue_contract_gate.py`
- `tests/unit/test_promotion_asset_review_queue_contract_gate.py`

## 증거

- `agents/project/PROMOTION-ASSET-REVIEW-QUEUE-CONTRACT.json`
- `agents/project/PROMOTION-ASSET-REVIEW-QUEUE-CONTRACT.md`
- `scripts/promotion_asset_review_queue_contract_gate.py`
- `tests/unit/test_promotion_asset_review_queue_contract_gate.py`
- `agents/project/initiatives/TASKSET-MARKETING-ASSET-REVIEW-AUDIT-PREVIEW.md`
- `agents/lead_engineer/tasks/TASK-136-promotion-asset-review-queue-audit-preview.md`

## 리뷰

판정: 통과

- The queue contract is local-only and does not approve publication or final
  export.
- Every queue state has `live_action=false`.
- Every queue item remains blocked for public use, final export, publication,
  external action, customer contact, CRM/payment, and secret material.

## Independent Audit

same-session self-review:

- Gate rejects source hash drift, missing queue contract fields, live-action
  state transitions, forbidden public/live state names, missing target coverage,
  unblocked public use, final output keys, customer/private/secret keys, and
  platform/live flags.
- No final legal/tax/securities advice was issued; this remains a local review
  queue contract.

## 검증

- `python -m json.tool agents\project\PROMOTION-ASSET-REVIEW-QUEUE-CONTRACT.json` pass
- `python scripts\promotion_asset_review_queue_contract_gate.py --check` pass
- `python -m pytest tests\unit\test_promotion_asset_review_queue_contract_gate.py -q` 10 passed
- `python -m py_compile scripts\promotion_asset_review_queue_contract_gate.py` pass
