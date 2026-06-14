---
type: task
id: TASK-058
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer, QA]
priority: High
difficulty: 낮
est_hours: 1
est_tokens: 10000
tags: [bug, ui, history, pnl]
gate: -
trigger_meeting: 즉시 처리 권고
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T14:15:00+09:00
---

# TASK-058 fix: history.py 라이브 모드 조기 return으로 PnL/배당 탭 미렌더

작업 ID: TASK-058
상태: 완료
Owner: UI/UX Designer
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: UI/UX Designer
의도: history.py 라이브 모드 조기 return 제거로 전체 탭 렌더링
대상: app/ui/history.py ~line 41
방법: 라이브 모드 분기 끝 불필요 return 제거 + test_history_kis_view.py 라이브 3탭 렌더링 검증 추가
감사 로그: AUDIT-2026-06-14-001

## 버그 내용

`app/ui/history.py` 약 41번째 줄에서 라이브 모드 주문 로그 표시 후 `return`이 있어 fills/PnL/dividend 탭이 라이브 모드에서 영원히 미렌더.

**증상**: 라이브 모드에서 내역 화면에 주문 로그만 표시되고 PnL 탭과 배당 탭이 렌더링되지 않음.

**원인**: 라이브 모드 분기 처리 블록 끝에 불필요한 `return` 문이 있어 이후 탭 렌더링 코드에 도달하지 못함.

## 수정 방향

1. `history.py` ~line 41의 `return` 제거
2. 라이브 모드에서도 fills/PnL/dividend 탭 전부 렌더링 확인
3. `test_history_kis_view.py`에 라이브 모드 3탭 렌더링 검증 추가

## 완료 기준

- 라이브 모드에서 주문 로그 + PnL + 배당 탭 모두 표시
- `test_history_kis_view.py` 통과
- `python -m pytest tests/ -q` green

## Done When

- 라이브 모드에서 주문 로그 + PnL + 배당 탭 모두 표시
- `test_history_kis_view.py` 통과

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙: `agents/lead_engineer/tasks/units/TASK-058/UNIT-TASK-058-001.md`

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`

## 완료 기록

완료 시각: 2026-06-14T14:15:00+09:00
검토자: UI/UX Designer / QA

## 증거

- `app/ui/views/history.py` line 41 `return` 제거 (라이브 모드 조기 종료 원인).
- 라이브 모드에서 `backend.daily_pnl_series()` 기반 일·월 손익 섹션 추가 (빈 데이터 시 empty_state).
- 라이브 모드에서 배당 섹션 추가 (live 배당 소스 미구현 — empty_state "배당 내역 없음").
- `tests/unit/test_history_live_mode_tabs.py` 신규 (2개 테스트):
  - `test_live_mode_renders_pnl_and_dividend_tabs`: 수정 전 FAILED (서브헤더 `['KIS 날짜별 주문내역']`만 존재) → 수정 후 PASSED.
  - `test_live_mode_renders_all_three_tab_sections`: 수정 전 FAILED → 수정 후 PASSED.
- 기존 `test_history_view_queries_kis_order_history_from_date_controls`: PASSED (회귀 없음).
- 수정 후: 521 unit tests passed, 668 tests passed (전체).

## 리뷰

- 데모 모드 동작 무변경 — `st.tabs(["체결내역", "일·월 손익", "배당"])` 코드 그대로.
- 라이브 모드 empty_state 패턴: `ui.empty_state()` — 다른 뷰와 동일한 방식.
- `backend.daily_pnl_series()` 예외 처리: try/except로 안전하게 폴백.
- 배당 라이브 소스 없음 → 빈 상태 표시 (데이터 조작 없음).

실측 비용 (시간): ~0.3h

## Independent Audit

판정: 통과 — 조기 return 제거로 라이브 모드 PnL/배당 서브헤더 렌더 확인. 2개 신규 TDD 테스트 수정 전 FAIL → 수정 후 PASS. 기존 테스트 회귀 없음. 521 unit passed, 668 전체 passed. check_agent_docs 0 error.
