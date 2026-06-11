---
type: taskset
id: TASKSET-AF-UI-CONTROL-DESK
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, UI/UX Designer, QA, Doc Steward]
priority: High
difficulty: 상
est_hours: 16
est_tokens: 180000
tags: [ui, design-system, safety, streamlit, taskset]
trigger_meeting: 자가발생
audit_log: AUDIT-2026-06-11-006
created: 2026-06-11
created_at: 2026-06-11T12:50:32+09:00
---

# TASKSET-AF-UI-CONTROL-DESK — Autofolio UI Control Desk

상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-11T12:50:32+09:00
기록 시각: 2026-06-11T12:50:32+09:00

## 원 요청

`docs/design` 자료를 다시 첨부했으니 대화 기록 후 진행하고, UI 개발을 기획한 다음
taskset으로 등록한다.

## 목표

Autofolio UI를 안전 우선 운영 관제 콘솔로 정리한다. 디자인 방향은 Coinbase +
IBM(Carbon) + Binance 일부 + Linear/Raycast 일부 조합의 `Autofolio Control Desk`로
고정한다.

## 포함 범위

- 디자인 방향과 컴포넌트 매트릭스 문서화
- Streamlit theme/component 토큰 정리
- 상단 Safety Rail과 상태 badge 개선
- Home/Portfolio/Trade 주요 화면의 safety-first 재배치
- Agents/Alerts/Settings의 콘솔/연동/위험영역 표면 정리
- 접근성, 색상 의존성, 기본 회귀 테스트 추가

## 제외 범위

- KIS 주문 API, broker write, `app/engine/order_flow.py`, `app/risk/**` 동작 변경
- prod trading 활성화
- secret 또는 `.env` 접근/변경
- DB schema/migration
- CI workflow 변경

## Task 구성

| Task | Owner | 목적 | 의존성 |
|------|-------|------|--------|
| TASK-025 | Lead Engineer | 디자인 방향과 토큰 기반 확정 | 없음 |
| TASK-026 | UI/UX Designer | Safety Rail과 공용 컴포넌트 | TASK-025 |
| TASK-027 | UI/UX Designer | Home/Portfolio control desk 개편 | TASK-026 |
| TASK-028 | UI/UX Designer | Trade page guard-first 흐름 | TASK-026, TASK-024 |
| TASK-029 | QA | 콘솔/알림/설정 polish와 접근성 회귀 | TASK-027, TASK-028 |

## 진행 현황

| Task | 상태 | 기록 |
|------|------|------|
| TASK-025 | 완료 | 디자인 방향과 theme token 기반 확정 |
| TASK-026 | 완료 | Safety Rail과 공용 badge/helper contract 추가 |
| TASK-027 | 완료 | Home/Portfolio control desk 재배치 |
| TASK-028 | 완료 | Trade guard-first 주문 흐름 |
| TASK-029 | 완료 | 콘솔/알림/설정 polish와 접근성 회귀 |

## 완료 기준

- [x] TASK-025~029가 모두 완료
- [x] `docs/design/autofolio/` 정본 작성
- [x] `docs/superpowers/plans/2026-06-11-autofolio-ui-control-desk.md` 기준 구현 완료
- [x] UI가 `mock`/`paper`/`prod`/`unknown` 환경을 명확히 표시
- [x] 주문 가능 화면이 guard checklist를 action보다 먼저 표시
- [x] `pytest` focused UI/guard tests 통과
- [x] `python scripts/check_agent_docs.py` 0 error

## 완료 기록

### 2026-06-11T18:33:41+09:00

- TASK-025~029 모두 완료.
- focused UI pytest 30 passed, full `pytest tests -v` 322 passed.
- `python scripts\generate_views.py --check` OK, `python scripts\check_agent_docs.py` 0 errors.
- Streamlit app은 foreground smoke에서 `Local URL: http://localhost:8502`까지 부팅 확인. 이 shell 환경에서는 detached background 서버가 즉시 종료되어 장기 실행 URL은 유지하지 못함.
- Home/Portfolio/Trade/Agents/Alerts/Settings가 `Autofolio Control Desk` 방향으로 정리됨.
- R3 표면인 KIS write path, `app/risk/**`, DB schema, `.env`, CI workflow는 변경하지 않음.

## 관련 근거

- `EVIDENCE-2026-06-11-006`
- `docs/UI_SPEC.md`
- `docs/PRODUCT_BLUEPRINT.md`
- `agents/lead_engineer/SAFETY-RULEBOOK.md`
- `docs/superpowers/plans/2026-06-11-autofolio-ui-control-desk.md`

## 실행 경계

이 taskset은 R1/R2 문서·UI 변경으로 계획한다. `AGENTS.md §16`의 Autofolio R3 surface인
KIS 주문 경로, safety gate, DB schema, `.env`, CI workflow는 건드리지 않는다.
