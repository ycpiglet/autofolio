---
type: task
id: TASK-132
display_id: TASK-132
task_uid: 2cf84d66-edb3-475c-81c3-314c45945e57
registered_at: 2026-06-19T23:40:40+09:00
created_at: 2026-06-19T23:40:40+09:00
updated_at: 2026-06-19T23:40:40+09:00
started_at: 2026-06-19T23:40:40+09:00
completed_at: 2026-06-19T23:40:40+09:00
status: 완료
owner: Marketing Growth
assignees: [Marketing Growth, Backend Engineer, Compliance Officer, QA, Doc Steward]
priority: Medium
difficulty: 중
est_hours: 2
actual_hours: 1
est_tokens: 25000
actual_tokens: 14000
tags: [marketing, assets, pdf, pptx, rendering, gate]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION
gate: local contract only; no final PDF/PPTX export, no public URL, no SNS upload, no customer contact, no CRM/payment
trigger_meeting: Owner goal continuation 2026-06-19
audit_log: AUDIT-2026-06-19-045
created: 2026-06-19
---

# TASK-132 Promotion Asset Rendering Contract

작업 ID: TASK-132
상태: 완료
Owner: Marketing Growth
요청 시각: 2026-06-19T23:40:40+09:00
기록 시각: 2026-06-19T23:40:40+09:00
완료 시각: 2026-06-19T23:40:40+09:00
요청자: Owner goal continuation
수행자: Marketing Growth, Backend Engineer, Compliance Officer, QA, Doc Steward
검토자: QA, Compliance Officer, Doc Steward perspective
실측 비용 (시간): 1h
실측 비용 (LLM 토큰): 14000
의도: future PDF/PPTX/landing/SNS asset rendering 전에 local source/hash/review/export boundary contract를 고정한다.
대상: `PROMOTION-ASSET-RENDERING-CONTRACT.json`/`.md`, local gate, focused tests
방법: MARKETING-MATERIALS-V1, MARKETING-BRIEF, SALES-REVENUE-LANE-DECISION을 source input으로 묶고 final binary/public export를 차단하는 contract/gate를 만든다.
감사 로그: AUDIT-2026-06-19-045

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION`
- Next task: `TASK-133`

## 범위

포함:

- Local rendering contract.
- Source artifact paths and hashes.
- Landing/PDF/PPTX/SNS source preview target definitions.
- Render queue required/forbidden fields.
- Final export, public upload, customer contact, CRM/payment, secret, KIS/order/risk/prod/deploy blockers.
- Local gate and focused tests.

제외:

- Final PDF/PPTX binary generation.
- Public landing page deployment.
- SNS upload or live publishing.
- Customer contact, CRM, payment, billing, support execution.
- External account action, OAuth, secret/token handling.
- KIS/order/risk/prod/deploy changes.

## 완료 조건

- [x] Contract records source hashes.
- [x] Contract defines local preview source targets only.
- [x] Gate rejects final export, public export, forbidden output keys, source drift, missing review boundary, and missing next handoff.
- [x] Focused tests cover happy path and forbidden export paths.
- [x] TASK-133 is registered as the next no-Owner slice.

## 완료 내용

- Future PDF/PPTX/landing/SNS asset rendering 전에 사용할 local-only rendering
  contract를 만들었다.
- Contract가 `MARKETING-MATERIALS-V1`, `MARKETING-BRIEF`,
  `SALES-REVENUE-LANE-DECISION` source hash를 기록하게 했다.
- Final binary export, public export, SNS upload, customer contact, CRM/payment,
  OAuth/secret/external account action을 Owner/R3 boundary로 차단했다.
- TASK-133을 다음 local preview manifest 후보로 등록했다.

## 완료 기록

결과:

- `PROMOTION-ASSET-RENDERING-CONTRACT.json`/`.md` created.
- `promotion_asset_rendering_contract_gate.py` and focused tests created.
- `TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION` registered with TASK-133 as the next ACT candidate.

## 증거

- `agents/project/PROMOTION-ASSET-RENDERING-CONTRACT.json`
- `agents/project/PROMOTION-ASSET-RENDERING-CONTRACT.md`
- `scripts/promotion_asset_rendering_contract_gate.py`
- `tests/unit/test_promotion_asset_rendering_contract_gate.py`
- `agents/lead_engineer/tasks/TASK-133-promotion-asset-preview-manifest.md`

## 리뷰

판정: 통과

- Contract is local-only and hash-bound to source artifacts.
- No renderer implementation, final export, public URL, SNS upload, customer contact, CRM/payment action, secret, or external account action was created.

## Independent Audit

same-session self-review:

- Every render target has `final_export_enabled=false`, `binary_export_enabled=false`, and `public_export_enabled=false`.
- Owner and Compliance review are required before public/export use.
- Actual asset export remains a separate Owner/R3 boundary.

## 검증

- `python -m json.tool agents\project\PROMOTION-ASSET-RENDERING-CONTRACT.json` pass
- `python scripts\promotion_asset_rendering_contract_gate.py --check` pass
- `python -m pytest tests\unit\test_promotion_asset_rendering_contract_gate.py -q` 8 passed
- `python -m py_compile scripts\promotion_asset_rendering_contract_gate.py` pass
