---
type: task
id: TASK-168
display_id: TASK-168
task_uid: 12abadc7-a9e7-421e-905f-964ead5fb041
registered_at: 2026-06-20T10:42:57+09:00
created_at: 2026-06-20T10:42:57+09:00
updated_at: 2026-06-20T11:31:13+09:00
started_at: 2026-06-20T11:31:13+09:00
completed_at: 2026-06-20T11:31:13+09:00
status: 완료
owner: Doc Steward
assignees: [Doc Steward, Marketing Growth, Backend Engineer, UI/UX Designer, QA, Compliance Officer]
priority: Medium
difficulty: 중
est_hours: 3
est_tokens: 35000
tags: [marketing, assets, pdf, pptx, rendering, readiness]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-MARKETING-TEAM-OPERATING-SYSTEM
gate: readiness map only; no final PDF/PPTX binary export, no public URL, no SNS upload, no customer contact, no external account action
trigger_meeting: Owner direct request 2026-06-20
audit_log: AUDIT-2026-06-20-069
created: 2026-06-20
---

# TASK-168 Promotion Asset Generator Readiness Map

작업 ID: TASK-168
상태: 완료
Owner: Doc Steward
요청 시각: 2026-06-20T10:42:57+09:00
기록 시각: 2026-06-20T10:42:57+09:00
요청자: Owner
수행자: Doc Steward, Marketing Growth, Backend Engineer, UI/UX Designer, QA, Compliance Officer
의도: PDF/PPTX 등 홍보물 자동 생성 전에 source, renderer, review gate, blocked output을 정리한다.
대상: PROMOTION-ASSET-RENDERING-CONTRACT, PROMOTION-ASSET-PREVIEW-MANIFEST, future asset-generator implementation readiness
방법: 기존 asset rendering contract와 preview manifest를 재사용해 generator readiness map과 future task 분류를 만든다.
감사 로그: AUDIT-2026-06-20-069
완료 시각: 2026-06-20T11:40:01+09:00
실측 비용 (시간): 약 0.3h
실측 비용 (LLM 토큰): unknown
검토자: Doc Steward self-review + Marketing Growth perspective + Backend Engineer perspective + UI/UX Designer perspective + QA focused gate tests + Compliance Officer perspective
협업 waiver(사유): 단일 세션 범위의 local readiness map/gate 작업이다. 외부 subagent dispatch 없이 역할별 관점 검토와 deterministic local gate/tests로 대체했고, final PDF/PPTX export/publication/customer/contact/payment/OAuth/platform API/secret/KIS/deploy 경계는 건드리지 않았다.
routing_ref: TASKSET-MARKETING-TEAM-OPERATING-SYSTEM / TASK-168
selected_model: Codex coding agent

## 목표

PDF/PPTX 등 홍보물 자동 생성으로 가기 전 필요한 source, renderer, review gate를 정리한다.

## Taskset

- Initiative: `INIT-MARKETING-GROWTH`
- Taskset: `TASKSET-MARKETING-TEAM-OPERATING-SYSTEM`
- Depends on: `TASK-167`
- Source artifacts: `TASK-132`, `TASK-133`

## 범위

포함:

- `PROMOTION-ASSET-RENDERING-CONTRACT`와
  `PROMOTION-ASSET-PREVIEW-MANIFEST`의 reuse map 작성.
- PDF one-pager, PPTX deck, landing-page source, SNS image/text source별
  renderer 후보와 input schema 정리.
- Review gate, source hash, forbidden output field, rollback/delete evidence
  requirements 정리.
- Future implementation task 후보 분리.

제외:

- 최종 PDF/PPTX binary 생성.
- public landing page 배포.
- SNS 업로드 또는 live publishing.
- 고객 연락, CRM/payment, external account action.
- OAuth, secret/token handling.
- KIS/order/risk/prod/deploy 변경.

## 완료 조건

- [x] Asset generator readiness map artifact가 존재한다.
- [x] 각 target별 source, renderer candidate, review gate, blocked output이
      분리된다.
- [x] 실제 binary/export 작업은 별도 승인 경계로 남는다.
- [x] Future implementation tasks가 R2/R3로 분류된다.

## 완료 내용

- `agents/project/PROMOTION-ASSET-GENERATOR-READINESS-MAP.json`을 추가해
  Marketing Materials, campaign calendar, rendering contract, preview manifest,
  Marketing Brief, channel policy matrix의 source hash를 고정했다.
- `agents/project/PROMOTION-ASSET-GENERATOR-READINESS-MAP.md`를 추가해
  landing-page source, PDF one-pager source, PPTX deck source, SNS draft bundle
  source별 source artifact, renderer candidate, review gate, blocked output,
  rollback/delete requirement를 사람이 읽을 수 있게 정리했다.
- `scripts/promotion_asset_generator_readiness_map_gate.py`와 focused unit
  tests를 추가해 source hash drift, live/export/customer/payment/platform flag,
  forbidden key, missing Owner/R3 review, missing R2/R3 implementation split,
  handoff drift를 차단한다.
- TASK-169를 다음 no-Owner local SNS publishing automation readiness backlog로
  남겼다.

## 완료 기록

완료일: 2026-06-20
결과: TASK-168은 local asset generator readiness map으로 완료됐다.
변경 파일: `PROMOTION-ASSET-GENERATOR-READINESS-MAP.json`,
`PROMOTION-ASSET-GENERATOR-READINESS-MAP.md`,
`scripts/promotion_asset_generator_readiness_map_gate.py`,
`tests/unit/test_promotion_asset_generator_readiness_map_gate.py`, source hash
contract updates, taskset/task/report/status/generated views.
이슈: 없음. Renderer implementation, final PDF/PPTX binary export, public
landing page deployment, SNS upload, customer contact, CRM/customer records,
payment request, Sales/Revenue activation, OAuth, platform API call,
browser automation against social platforms, secret/customer data,
KIS/order/risk/prod/deploy 변경 없음.
다음 담당자 인수 사항: TASK-169는 promotion channel policy/state-machine/
dry-run/readiness sources를 입력으로 SNS publishing automation readiness
backlog를 작성한다.

## 변경 파일

- `agents/project/PROMOTION-ASSET-GENERATOR-READINESS-MAP.json`
- `agents/project/PROMOTION-ASSET-GENERATOR-READINESS-MAP.md`
- `scripts/promotion_asset_generator_readiness_map_gate.py`
- `tests/unit/test_promotion_asset_generator_readiness_map_gate.py`
- `agents/project/MARKETING-BRIEF.md`
- `agents/project/initiatives/TASKSET-MARKETING-TEAM-OPERATING-SYSTEM.md`
- `agents/project/PROMOTION-ASSET-RENDERING-CONTRACT.json`
- `agents/project/PROMOTION-ASSET-PREVIEW-MANIFEST.json`
- `agents/lead_engineer/tasks/TASK-168-promotion-asset-generator-readiness-map.md`

## 검증

- `python -m json.tool agents\project\PROMOTION-ASSET-GENERATOR-READINESS-MAP.json`
- `python -m py_compile scripts\promotion_asset_generator_readiness_map_gate.py`
- `python scripts\promotion_asset_generator_readiness_map_gate.py --check`
- `python -m pytest tests\unit\test_promotion_asset_generator_readiness_map_gate.py -q`
- `python scripts\promotion_asset_rendering_contract_gate.py --check`
- `python scripts\promotion_asset_preview_manifest_gate.py --check`

## 증거

- `agents/project/PROMOTION-ASSET-GENERATOR-READINESS-MAP.json`
- `agents/project/PROMOTION-ASSET-GENERATOR-READINESS-MAP.md`
- `scripts/promotion_asset_generator_readiness_map_gate.py`
- `tests/unit/test_promotion_asset_generator_readiness_map_gate.py`
- `agents/lead_engineer/reports/BRIEF-2026-06-20-037.md`

## 리뷰

- Doc Steward perspective: source/hash references are explicit and gate-checked.
- Marketing Growth perspective: asset surfaces map to existing campaign and
  marketing material sources without public copy approval.
- Backend Engineer perspective: future local parser/preview work is separated
  from OAuth, platform API, and live publishing work.
- UI/UX Designer perspective: landing/PDF/PPTX/SNS surfaces have renderer
  candidates but no implemented output.
- Compliance Officer perspective: public claims and final generated assets
  still require Compliance and Owner/R3 review.
- QA perspective: gate/tests fail source hash drift, live/export flags,
  missing review gates, forbidden keys, missing R2/R3 split, and handoff drift.

## 경계

- Final PDF/PPTX binary export: blocked.
- Public landing page deployment and external URL publication: blocked.
- SNS upload, OAuth, platform API call, browser automation against social
  platforms, external account action: blocked.
- Customer contact, CRM/customer records, payment request, Sales/Revenue
  activation: blocked.
- Secret/customer/private data, KIS/order/risk/prod/deploy changes: blocked.

## Independent Audit

- Verdict: pass.
- Evidence: local artifact, gate, tests, and taskset/status updates are scoped
  to TASK-168 readiness only.
- Residual risk: TASK-169 SNS publishing automation readiness remains pending;
  actual asset export and live publication require separate Owner/R3 lanes.
