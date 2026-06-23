---
type: task
id: TASK-133
display_id: TASK-133
task_uid: 68e72326-c314-46c3-a45b-d40179c4f70f
registered_at: 2026-06-19T23:40:40+09:00
created_at: 2026-06-19T23:40:40+09:00
updated_at: 2026-06-20T00:04:38+09:00
started_at: 2026-06-19T23:57:46+09:00
completed_at: 2026-06-20T00:04:38+09:00
status: 완료
owner: Marketing Growth
assignees: [Marketing Growth, Backend Engineer, Compliance Officer, QA, Doc Steward]
priority: Medium
difficulty: 중
est_hours: 3
actual_hours: 1
est_tokens: 35000
actual_tokens: 18000
tags: [marketing, assets, pdf, pptx, rendering, preview]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION
gate: local Markdown preview manifest only; no final PDF/PPTX export, no public URL, no SNS upload, no customer contact, no CRM/payment
trigger_meeting: Owner goal continuation 2026-06-19
audit_log: AUDIT-2026-06-20-001
created: 2026-06-19
---

# TASK-133 Promotion Asset Preview Manifest

작업 ID: TASK-133
상태: 완료
Owner: Marketing Growth
요청 시각: 2026-06-19T23:40:40+09:00
기록 시각: 2026-06-20T00:04:38+09:00
완료 시각: 2026-06-20T00:04:38+09:00
요청자: Owner goal continuation
수행자: Marketing Growth, Backend Engineer, Compliance Officer, QA, Doc Steward
검토자: QA, Compliance Officer, Doc Steward perspective
실측 비용 (시간): 1h
실측 비용 (LLM 토큰): 18000
의도: TASK-132 contract를 입력으로 local Markdown preview manifest를 만든다.
대상: local preview manifest JSON/Markdown, source hash, review status, final export blocked flag, rollback/delete notes
방법: `PROMOTION-ASSET-RENDERING-CONTRACT`와 `MARKETING-MATERIALS-V1`을 읽고 landing/PDF/PPTX/SNS preview source manifest를 생성한다.
감사 로그: AUDIT-2026-06-20-001

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION`
- Depends on: `TASK-132`

## 범위

포함:

- Local Markdown preview manifest only.
- Source artifact path/hash.
- Asset target list and review status.
- `final_export_blocked=true` and `public_export_blocked=true`.
- Rollback/delete instruction for future exported artifacts.
- Local gate and focused tests.

제외:

- Final PDF/PPTX binary export.
- Public landing page deployment.
- SNS upload or live publishing.
- Customer contact, CRM, payment, billing, support execution.
- External account action, OAuth, secret/token handling.
- KIS/order/risk/prod/deploy changes.

## 완료 조건

- [x] Preview manifest exists as local JSON/Markdown.
- [x] Manifest includes source hash, target ids, review status, final/public export blockers, and rollback/delete notes.
- [x] Gate rejects binary/public export fields, customer/private data, secret keys, and missing Owner/Compliance boundaries.
- [x] Focused tests pass.

## 완료 내용

- `PROMOTION-ASSET-RENDERING-CONTRACT`와 `MARKETING-MATERIALS-V1`을 source로
  삼아 local preview manifest를 만들었다.
- Landing/PDF/PPTX/SNS target별 source section, source hash, review status,
  final/public/binary/export blockers, rollback/delete instruction을 기록했다.
- Gate가 source drift, missing target, final/public export flags, forbidden
  output fields, secret/customer key names, Owner/Compliance boundary 누락,
  forbidden claim phrase를 차단하게 했다.
- TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION을 완료했다. 후속 claim-review
  체인은 별도 레인으로 미루며 이 브랜치에는 포함하지 않는다.

## 완료 기록

결과:

- `PROMOTION-ASSET-PREVIEW-MANIFEST.json`/`.md` created.
- `promotion_asset_preview_manifest_gate.py` and focused tests created.
- Landing/PDF/PPTX/SNS source previews are embedded as local Markdown-source
  metadata only.
- `TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION` is complete.
- The downstream claim-review chain is deferred to a separate lane and is not
  part of this branch.

변경 파일:

- `agents/project/PROMOTION-ASSET-PREVIEW-MANIFEST.json`
- `agents/project/PROMOTION-ASSET-PREVIEW-MANIFEST.md`
- `scripts/promotion_asset_preview_manifest_gate.py`
- `tests/unit/test_promotion_asset_preview_manifest_gate.py`

## 증거

- `agents/project/PROMOTION-ASSET-PREVIEW-MANIFEST.json`
- `agents/project/PROMOTION-ASSET-PREVIEW-MANIFEST.md`
- `scripts/promotion_asset_preview_manifest_gate.py`
- `tests/unit/test_promotion_asset_preview_manifest_gate.py`

## 리뷰

판정: 통과

- Manifest is local-only, hash-bound, and source-preview-only.
- No final PDF/PPTX binary, public URL, SNS upload, customer contact,
  CRM/payment, external account action, secret, KIS/order/risk/prod, or deploy
  change was created.

## Independent Audit

same-session self-review:

- Gate rejects source hash drift, missing targets, live/export flags,
  public/export output fields, secret/customer keys, missing Owner/Compliance
  review status, missing rollback instruction, and forbidden claim phrases.
- The manifest itself grants no public approval and no legal/tax/securities
  advice; any downstream claim-review work is out of scope for this branch.

## 검증

- `python -m json.tool agents\project\PROMOTION-ASSET-PREVIEW-MANIFEST.json` pass
- `python scripts\promotion_asset_preview_manifest_gate.py --check` pass
- `python -m pytest tests\unit\test_promotion_asset_preview_manifest_gate.py -q` 10 passed
- `python -m py_compile scripts\promotion_asset_preview_manifest_gate.py` pass
