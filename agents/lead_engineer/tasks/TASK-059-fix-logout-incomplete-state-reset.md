---
type: task
id: TASK-059
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, QA]
priority: Medium
difficulty: 낮
est_hours: 2
est_tokens: 15000
tags: [bug, security, session, logout]
gate: -
trigger_meeting: 다음 사이클
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T12:01:21+09:00
---

# TASK-059 fix: logout() 미완전 세션 상태 초기화 (state.py)

작업 ID: TASK-059
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: Backend Engineer
의도: logout() 함수에서 모든 세션 상태를 DEFAULTS로 완전 초기화
대상: app/ui/state.py logout() 함수
방법: DEFAULTS 전체 키 순회 초기화 구현 + 안전 키 명시 검증 + 재로그인 미유지 테스트 추가
감사 로그: AUDIT-2026-06-14-001

## 버그 내용

`app/ui/state.py`의 `logout()` 함수가 `kill_switch`, `mode`, `symbol_modes`, `auto_enabled` 등의 핵심 거래 설정 키를 초기화하지 않음.

**증상**: 로그아웃 후 다른 사용자로 로그인하면 이전 세션의 kill_switch 상태, 자동매매 모드, 종목별 설정이 그대로 남아있어 보안 및 안전 위험.

**원인**: `logout()`이 일부 키만 초기화하고 DEFAULTS 딕셔너리의 전체 키를 순회하지 않음.

## 수정 방향

1. `logout()`에서 `DEFAULTS` 딕셔너리의 전체 키를 순회하며 `st.session_state`를 DEFAULTS 값으로 초기화
2. 특히 안전 관련 키(`kill_switch`, `auto_enabled`, `mode`, `symbol_modes`) 명시적 초기화 검증
3. 재로그인 시 이전 상태 미유지 확인 테스트 추가

## 완료 기준

- `logout()` 후 모든 세션 상태 DEFAULTS로 초기화
- 재로그인 시 이전 상태 미유지
- `python -m pytest tests/ -q` green

## Done When

- `logout()` 후 모든 세션 상태 DEFAULTS로 초기화
- 재로그인 시 이전 상태 미유지

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙: `agents/lead_engineer/tasks/units/TASK-059/UNIT-TASK-059-001.md`

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`

## 완료 기록

완료 시각: 2026-06-14T12:01:21+09:00
검토자: Backend Engineer / QA

## 증거

- `app/ui/state.py` `logout()`: DEFAULTS 3개 키만 초기화 → DEFAULTS 전체 순회(`copy.copy`) + extra 키 3개 `pop`으로 교체.
  - `_EXTRA_SESSION_KEYS` 모듈 상수 신설 (`trade_ack_checked`, `_trade_ack_pending_message`, `_trade_ack_context`).
  - `import copy` 추가.
- `tests/unit/test_state_logout.py`: 신규 14개 테스트 (TDD — 수정 전 9 FAILED).
  - DEFAULTS 9개 키 각각 초기화 검증 (`test_logout_resets_*`).
  - `symbol_modes` 독립 사본 검증 (`test_logout_symbol_modes_is_independent_copy`).
  - extra 키 3개 제거 검증 (`test_logout_removes_*`).
  - extra 키 없을 때 오류 없음 (`test_logout_no_error_when_extra_keys_absent`).
- 수정 전: 9 FAILED (mode·auto_enabled·kill_switch·pnl_kr_colors·symbol_modes·data_source·trade_ack_checked·_trade_ack_pending_message·_trade_ack_context 누출 확인).
- 수정 후: 14 passed (test_state_logout.py), 653 passed 전체 (기존 2 pre-existing 실패 불변).

## 리뷰

- `copy.copy()` 선택 근거: DEFAULTS 값이 모두 단순 타입(bool·str·None) 또는 빈 dict — copy.copy()로 충분. symbol_modes 중첩 값 없음.
- `_EXTRA_SESSION_KEYS` 상수화: 미래 extra 키 추가 시 한 곳만 수정.
- 기존 pre-existing 실패(test_top_bar_data_source.py 2개) 변동 없음 — 이 PR과 무관한 Streamlit AppTest runner 이슈.

실측 비용 (시간): ~0.3h (subagent)
실측 비용 (LLM 토큰): ~140k (subagent)

## Independent Audit

판정: 통과 — 수정 전 9 FAILED(누출 키 확인) → 수정 후 14 passed. 전체 653 passed (기존 2 pre-existing 불변). TDD(실패 테스트 선행) + spec reviewer(PASS) + code quality reviewer(APPROVED). 0 doc error. work_schema_gate pass, build_task_index OK, generate_views OK.
