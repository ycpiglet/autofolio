---
type: task
id: TASK-134
display_id: TASK-134
task_uid: 8ba9f848-f72c-4deb-be8f-d0b8c5304a41
registered_at: 2026-06-20T00:04:38+09:00
created_at: 2026-06-20T00:04:38+09:00
updated_at: 2026-06-20T00:25:10+09:00
started_at: 2026-06-20T00:19:57+09:00
completed_at: 2026-06-20T00:25:10+09:00
status: 완료
owner: Compliance Officer
assignees: [Compliance Officer, Marketing Growth, QA, Doc Steward]
priority: Medium
difficulty: 중
est_hours: 3
actual_hours: 1
est_tokens: 35000
actual_tokens: 17000
tags: [marketing, compliance, claims, review, assets]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-ASSET-CLAIM-REVIEW-FOUNDATION
gate: local claim classification matrix only; no public approval, no legal/tax/securities final advice, no final asset export, no SNS upload, no customer contact, no CRM/payment
trigger_meeting: Owner goal continuation 2026-06-20
audit_log: AUDIT-2026-06-20-003
created: 2026-06-20
---

# TASK-134 Promotion Asset Claim Review Matrix

작업 ID: TASK-134
상태: 완료
Owner: Compliance Officer
요청 시각: 2026-06-20T00:04:38+09:00
기록 시각: 2026-06-20T00:25:10+09:00
완료 시각: 2026-06-20T00:25:10+09:00
요청자: Owner goal continuation
수행자: Compliance Officer, Marketing Growth, QA, Doc Steward
검토자: Compliance Officer, QA, Doc Steward perspective
실측 비용 (시간): 1h
실측 비용 (LLM 토큰): 17000
의도: TASK-133 preview manifest claims를 local classification matrix로 분류한다.
대상: local claim review matrix JSON/Markdown, source hash, allowed/needs-review/Owner-only/reject buckets, gate, focused tests
방법: `PROMOTION-ASSET-PREVIEW-MANIFEST`와 `MARKETING-MATERIALS-V1`을 읽고 public approval이 아닌 draft claim classification만 만든다.
감사 로그: AUDIT-2026-06-20-003

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-ASSET-CLAIM-REVIEW-FOUNDATION`
- Depends on: `TASK-133`

## 범위

포함:

- Local claim classification matrix only.
- Source artifact path/hash.
- Allowed draft, needs Compliance review, Owner-only, reject buckets.
- Public-use blocker and professional-review caveat.
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

- [x] Claim review matrix exists as local JSON/Markdown.
- [x] Matrix includes source hashes and bucketed claim classifications.
- [x] Gate rejects public approval, final advice, missing public-use blocker,
  forbidden claims, secret/customer keys, and final/public export fields.
- [x] Focused tests pass.

## 완료 내용

- `PROMOTION-ASSET-PREVIEW-MANIFEST`, `MARKETING-MATERIALS-V1`, and
  `PROMOTION-ASSET-RENDERING-CONTRACT` source hashes were recorded in
  `PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.json`.
- Claims were split into allowed draft, needs Compliance review, Owner-only
  before public use, and reject buckets.
- Landing/PDF/PPTX/SNS preview targets now have local classification records
  with `public_use_blocked=true`, `final_export_blocked=true`, and
  `publication_approval_blocked=true`.
- A local gate and focused tests now reject source drift, missing review
  buckets, missing preview target coverage, public approval flags, secret or
  customer keys, final output fields, and missing prohibited-claim coverage.
- `TASKSET-MARKETING-ASSET-CLAIM-REVIEW-FOUNDATION` is complete and
  `TASK-135` is registered as the next no-Owner local review-queue contract
  candidate.

## 완료 기록

결과:

- `PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.json`/`.md` created.
- `promotion_asset_claim_review_matrix_gate.py` and focused tests created.
- Public use, publication approval, final advice, final PDF/PPTX export, SNS
  upload, customer contact, CRM/payment action, external account action,
  secrets, KIS/order/risk/prod, and deploy changes remain blocked.
- Next local slice: `TASK-135 Promotion Asset Review Queue Contract`.

변경 파일:

- `agents/project/PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.json`
- `agents/project/PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.md`
- `scripts/promotion_asset_claim_review_matrix_gate.py`
- `tests/unit/test_promotion_asset_claim_review_matrix_gate.py`

## 증거

- `agents/project/PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.json`
- `agents/project/PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.md`
- `scripts/promotion_asset_claim_review_matrix_gate.py`
- `tests/unit/test_promotion_asset_claim_review_matrix_gate.py`
- `agents/project/initiatives/TASKSET-MARKETING-ASSET-REVIEW-QUEUE-FOUNDATION.md`
- `agents/lead_engineer/tasks/TASK-135-promotion-asset-review-queue-contract.md`

## 리뷰

판정: 통과

- The matrix is local claim classification only and does not approve public use.
- Reject bucket includes guarantee, risk-free, investment-advice, paid-signal,
  model-portfolio, broker/asset-manager/robo-advisor, KIS clearance, and
  winning-stock language.
- Needs-review and Owner-only buckets keep recommendation, KIS, LLM/SNS token,
  pricing, public landing, PDF/PPTX export, SNS, customer contact, and paid ads
  behind review gates.

## Independent Audit

same-session self-review:

- Gate rejects source hash drift, missing boundaries, missing bucket entries,
  missing preview target coverage, unblocked public use, public approval flags,
  forbidden final output keys, and secret/customer/final-advice key names.
- No final legal/tax/securities advice was issued; this remains a draft
  classification packet.

## 검증

- `python -m json.tool agents\project\PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.json` pass
- `python scripts\promotion_asset_claim_review_matrix_gate.py --check` pass
- `python -m pytest tests\unit\test_promotion_asset_claim_review_matrix_gate.py -q` 10 passed
- `python -m py_compile scripts\promotion_asset_claim_review_matrix_gate.py` pass
