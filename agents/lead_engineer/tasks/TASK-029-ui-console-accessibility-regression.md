---
type: task
id: TASK-029
status: 완료
owner: QA
assignees: [UI/UX Designer, QA, Doc Steward]
priority: Medium
difficulty: 중
est_hours: 3
est_tokens: 30000
tags: [ui, qa, accessibility, alerts, agents]
trigger_meeting: 자가발생
audit_log: AUDIT-2026-06-11-006
created: 2026-06-11
created_at: 2026-06-11T12:50:32+09:00
---

# TASK-029 UI Console Accessibility Regression

작업 ID: TASK-029
상태: 완료
Owner: QA
요청 시각: 2026-06-11T12:50:32+09:00
기록 시각: 2026-06-11T12:50:32+09:00

## 배경 및 목적

Agents, Alerts, Settings 화면은 정보량이 많고 안전/연동/secret 경계를 함께 다룬다.
console surface와 접근성 회귀 기준을 정해 UI refresh가 오히려 위험 상태를 숨기지 않도록
마무리 검증한다.

## 구현 범위

- `app/ui/views/agents.py` console-like observability refresh
- `app/ui/views/alerts.py` severity/source grouping
- `app/ui/views/settings.py` secret/danger zone separation
- `ui.console_row()` helper와 테스트
- focused pytest와 `check_agent_docs` 검증

## 완료 기준

- [x] Agents 화면은 action보다 관찰/결정 로그를 우선 표시
- [x] Alerts 화면은 severity/source/time/next action을 표시
- [x] Settings 화면은 secret과 danger action을 일반 설정과 분리
- [x] 색상만으로 상태를 전달하지 않음
- [x] `pytest tests/unit/test_ui_components_contract.py -v` 통과
- [x] `python scripts/check_agent_docs.py` 0 error

## 계획 링크

- `docs/superpowers/plans/2026-06-11-autofolio-ui-control-desk.md` Task 5

## 리스크 및 경계

- secret 값은 표시하지 않는다. `.env`와 vault 데이터를 읽거나 수정하지 않는다.

## 완료 기록

### 2026-06-11T18:33:41+09:00

- `ui.console_row()`를 추가하고 timestamp/source/message 텍스트 계약을 테스트로 고정.
- Agents 화면에 관찰 콘솔 탭을 추가해 에이전트 연결 상태, registry, data source, 최근 IC 결정 로그를 action보다 먼저 표시.
- Alerts 화면을 feed-first 구조로 바꾸고 severity/source/time/next action을 색상 없이 텍스트로 표시.
- Settings 화면을 운영모드/리스크/증권계좌/알림채널/계정 순서로 재정렬하고, secret 입력과 계좌 삭제 danger action을 일반 설정에서 분리.
- App Key/App Secret/계좌번호 입력은 password field로 처리하고 저장된 secret 값을 표시하지 않음.
- 검증:
  - `pytest tests/unit/test_ui_components_contract.py -v` → 6 passed
  - `pytest tests/unit/test_backend_kpis.py tests/unit/test_ui_components_contract.py tests/unit/test_ui_theme_tokens.py tests/unit/test_ui_trade_guard_workflow.py -v` → 30 passed
  - `python -m py_compile app\ui\components\ui.py app\ui\views\agents.py app\ui\views\alerts.py app\ui\views\settings.py` → 통과
  - `python scripts\check_agent_docs.py` → 0 errors, 108 existing warnings
