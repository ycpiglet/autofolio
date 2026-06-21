---
type: task
id: TASK-094
display_id: TASK-094
task_uid: a3c2997f-f58d-4fb7-8f80-30dac73d2244
registered_at: 2026-06-19T00:04:30+09:00
created_at: 2026-06-19T00:04:30+09:00
updated_at: 2026-06-19T00:04:30+09:00
status: 보류
owner: Regulatory Admin
assignees: [Regulatory Admin, Business Planner, Backend Engineer, QA, Doc Steward]
priority: Medium
difficulty: 상
est_hours: 8
est_tokens: 90000
tags: [admin, documents, hwpx, business-registration, prototype]
gate: start after TASK-093 and target official form selection; no Owner identity data, no login, no submission, no legal/tax final advice
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-003
created: 2026-06-19
---

# TASK-094 Admin document packet and HWPX prototype

작업 ID: TASK-094
상태: 보류
Owner: Regulatory Admin
요청 시각: 2026-06-19T00:04:30+09:00
기록 시각: 2026-06-19T00:10:57+09:00
요청자: Owner
수행자: Regulatory Admin, Business Planner, Backend Engineer, QA, Doc Steward
의도: 사업자등록/행정절차에 필요한 문서 패킷을 구조화하고, 필요 시 HWPX 초안 생성 기능을 설계/시제품화한다.
대상: `agents/project/BUSINESS-ADMIN-REGISTER.md`, target official forms, document packet templates, optional HWPX fixture/generator
방법: Business Plan v1과 대상 공식 서식 확정 후 Owner data/generated text/attachment/Owner-only submission steps를 분리해 deterministic document packet prototype을 만든다.
감사 로그: AUDIT-2026-06-19-003

## 시작 조건

- TASK-093 Business Plan v1 완료.
- Owner가 사업 형태, 사업명, 주소/사업장 상태, 개업일, 업태/업종 후보,
  결제/판매 방식, 추천/자문 경계 선호를 제공.
- Regulatory Admin이 대상 공식 서식과 최신 공식 출처를 확인.

## 범위

포함:

- `BUSINESS-ADMIN-REGISTER.md`의 packet model을 실제 `DOC-PACKET-*` template로 확장.
- Owner 제공 데이터와 agent-drafted text를 분리하는 field map 작성.
- Markdown review draft -> generated HWPX/PDF/DOCX 후보 중 최소 1개 프로토타입 결정.
- HWPX를 선택할 경우 XML/ZIP fixture, deterministic generation, diffable output, tests 추가.
- 제출 전 Owner-only checklist 작성.

제외:

- 실제 사업자등록 제출, 홈택스/정부24 로그인, 인증서 사용, 서명, 결제.
- 주민등록번호, 인증서, 계좌, broker key, API secret 저장.
- 법률/세무/증권 규제 최종 자문.

## 완료 조건

- [ ] 공식 서식과 source URL이 기록됐다.
- [ ] field map이 Owner data / generated text / attachment / Owner-only step으로 나뉘었다.
- [ ] 최소 하나의 reviewable document draft가 생성된다.
- [ ] HWPX를 구현했다면 fixture와 deterministic test가 있다.
- [ ] 제출은 Owner-only임이 문서와 CLI 출력에 명확히 표시된다.
