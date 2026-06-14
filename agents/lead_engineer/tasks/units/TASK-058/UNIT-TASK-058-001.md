---
type: unit
id: UNIT-TASK-058-001
task_id: TASK-058
status: 완료
owner: UI/UX Designer
created_at: 2026-06-14T14:08:35+09:00
updated_at: 2026-06-14T14:15:00+09:00
---

# UNIT-TASK-058-001: history.py 라이브 모드 조기 return 제거

## 목표

`app/ui/views/history.py` 라이브 모드 분기 끝의 불필요한 `return` 제거 후
일·월 손익(PnL) 및 배당 섹션을 라이브 모드에서도 렌더링.

## 대상 파일

- `app/ui/views/history.py` — 조기 return 제거 + PnL/배당 섹션 추가
- `tests/unit/test_history_live_mode_tabs.py` — 신규 TDD 테스트 (2개)

## 구현 내용

1. `history.py` line 41 `return` 제거 (live 분기 끝에 있던 조기 종료).
2. 라이브 모드에서 `st.divider()` + `st.subheader("일·월 손익")` + `backend.daily_pnl_series()` 기반 바 차트 렌더링 (빈 데이터 시 empty_state).
3. 라이브 모드에서 `st.divider()` + `st.subheader("배당")` + empty_state("배당 내역 없음") 렌더링 (live 배당 소스 미구현 — 빈 상태 표시).
4. 데모 모드 동작 무변경.

## TDD 증거

- `test_live_mode_renders_pnl_and_dividend_tabs`: 수정 전 FAILED (서브헤더 없음) → 수정 후 PASSED.
- `test_live_mode_renders_all_three_tab_sections`: 수정 전 FAILED → 수정 후 PASSED.
- 기존 `test_history_view_queries_kis_order_history_from_date_controls`: 여전히 PASSED.

## 완료 기준 충족

- 521 unit tests passed (tests/unit)
- 668 tests passed (tests/ 전체)
- check_agent_docs: 0 error(s)
