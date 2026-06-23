---
type: task
id: TASK-127
display_id: TASK-127
task_uid: be5be28f-2bf8-4df2-9da3-bd704228db25
registered_at: 2026-06-19T22:31:45+09:00
created_at: 2026-06-19T22:31:45+09:00
updated_at: 2026-06-19T22:31:45+09:00
started_at: 2026-06-19T22:31:45+09:00
completed_at: 2026-06-19T22:31:45+09:00
status: 완료
owner: Regulatory Admin
assignees: [Regulatory Admin, Business Planner, QA, Doc Steward]
priority: Medium
difficulty: 중
est_hours: 1
est_tokens: 18000
tags: [business-admin, document-packet, hwpx, business-registration, governance]
initiative_id: INIT-MARKETING-GROWTH
task_set_id: TASKSET-BUSINESS-ADMIN-DOCUMENT-PACKET-FOUNDATION
gate: local schema/gate/test only; no Owner private data, official login, signature, payment, submission, final HWPX generation, or legal/tax/securities advice
trigger_meeting: Owner goal continuation 2026-06-19
audit_log: AUDIT-2026-06-19-038
created: 2026-06-19
---

# TASK-127 Business admin document packet schema

작업 ID: TASK-127
상태: 완료
Owner: Regulatory Admin
요청 시각: 2026-06-19T22:31:45+09:00
기록 시각: 2026-06-19T22:31:45+09:00
요청자: Owner goal continuation
수행자: Regulatory Admin + Business Planner + QA + Doc Steward perspective (Codex)
검토자: Regulatory Admin self-review + QA focused gate tests + Doc Steward perspective
routing_ref: TASKSET-BUSINESS-ADMIN-DOCUMENT-PACKET-FOUNDATION / TASK-127
의도: TASK-094의 실제 HWPX/admin packet prototype 전에 Owner private data 없이 재사용 가능한 document packet schema와 local gate를 만든다.
대상: `BUSINESS-ADMIN-DOCUMENT-PACKET-SCHEMA.json`, `BUSINESS-ADMIN-DOCUMENT-PACKET-SCHEMA.md`, `business_admin_document_packet_schema_gate.py`, focused tests, admin register.
방법: official-source register와 기존 Business Plan v1을 근거로 placeholder-safe packet contract를 작성하고, Owner-only steps와 forbidden repo data를 gate로 검증한다.
감사 로그: AUDIT-2026-06-19-038
완료 시각: 2026-06-19T22:31:45+09:00
실측 비용 (시간): 약 0.3h
실측 비용 (LLM 토큰): unknown

## 범위

포함:

- Business/admin document packet schema JSON/Markdown 작성.
- Owner non-sensitive business data, Owner private data placeholders,
  agent-drafted text, required attachments, generated artifacts, Owner-only
  steps, review gates, forbidden repo data를 분리.
- Future HWPX work를 Markdown-first, structured data, template fixture, XML
  diff, human review, no auto-submit으로 고정.
- Local gate와 focused tests 추가.
- `BUSINESS-ADMIN-REGISTER.md`에 TASK-127 foundation을 연결.

제외:

- 실제 사업자등록 신청서 작성 또는 제출.
- 홈택스/정부24/한컴/KIS/은행/결제사 로그인, 인증, 서명, 결제, 업로드.
- 주민등록번호, 인증서, 계좌번호, KIS key, API secret, 고객정보, signed filing 저장.
- 최종 법률/세무/회계/증권/KIS/regulatory advice.
- 대상 공식 서식 기반 HWPX/PDF 최종 생성.

## 완료 조건

- [x] Document packet schema JSON/Markdown이 존재한다.
- [x] Gate가 private/secret key names, owner-only boundary, HWPX fixture/XML diff policy를 검증한다.
- [x] TASK-094는 실제 target official form and Owner private-data path 전까지 blocked로 유지된다.
- [x] Focused tests가 pass한다.

## 완료 내용

- `agents/project/BUSINESS-ADMIN-DOCUMENT-PACKET-SCHEMA.json`와 `.md`를 추가했다.
- `scripts/business_admin_document_packet_schema_gate.py`를 추가해 local schema contract를 검증한다.
- `tests/unit/test_business_admin_document_packet_schema_gate.py`를 추가해 current packet, owner login boundary, NTS source, private key name, HWPX XML diff policy, owner-only submission step을 검증한다.
- `BUSINESS-ADMIN-REGISTER.md`에 TASK-127 foundation section을 연결했다.

## 완료 기록

완료일: 2026-06-19
결과: Future admin/HWPX packet work의 구조와 금지 경계가 deterministic local gate로 고정됐다. TASK-094는 target official form, Owner business type/private-data path, professional review boundary가 정해질 때까지 계속 보류된다.
변경 파일: `BUSINESS-ADMIN-DOCUMENT-PACKET-SCHEMA.json`, `BUSINESS-ADMIN-DOCUMENT-PACKET-SCHEMA.md`, `scripts/business_admin_document_packet_schema_gate.py`, `tests/unit/test_business_admin_document_packet_schema_gate.py`, `BUSINESS-ADMIN-REGISTER.md`, taskset/task/report/status/generated views.
이슈: 없음. 다만 이 작업은 공식 서식별 HWPX generator가 아니라 foundation schema다.
다음 담당자 인수 사항: TASK-094는 Owner가 사업 형태, 대상 공식 서식, private-data handling path를 정한 뒤 이 schema를 사용해 시작한다.

## 증거

- `agents/project/BUSINESS-ADMIN-DOCUMENT-PACKET-SCHEMA.json`
- `agents/project/BUSINESS-ADMIN-DOCUMENT-PACKET-SCHEMA.md`
- `scripts/business_admin_document_packet_schema_gate.py`
- `tests/unit/test_business_admin_document_packet_schema_gate.py`

## 검증

- `python -m json.tool agents\project\BUSINESS-ADMIN-DOCUMENT-PACKET-SCHEMA.json`
- `python scripts\business_admin_document_packet_schema_gate.py --check`
- `python -m pytest tests\unit\test_business_admin_document_packet_schema_gate.py -q`

## 리뷰

- Regulatory Admin self-review: Official-source register and Owner-only boundary are explicit; the schema avoids private data and final advice.
- Business Planner perspective: The packet consumes `BUSINESS-PLAN.md` as non-sensitive source data and does not change the business model.
- QA perspective: Focused tests cover the main failure modes: login boundary weakening, missing official source, forbidden private key names, HWPX diff policy, and Owner-only submission step.
- Doc Steward perspective: TASK-094 remains blocked and this task is correctly scoped as a foundation artifact.

## Independent Audit

판정: 통과
- Same-session audit note: Only local docs/schema/gate/tests and governance records changed.
- No Hometax/Government24/Hancom/KIS/bank/provider login, authentication, signature, payment, upload, submission, Owner private data, customer data, secret, HWPX final generation, legal/tax/securities final advice, product code, order/risk, deploy, or production data boundary changed.
