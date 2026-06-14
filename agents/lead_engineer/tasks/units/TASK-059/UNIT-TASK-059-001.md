---
unit_id: UNIT-TASK-059-001
task_id: TASK-059
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [security, repeated_failure]
context: "logout()가 DEFAULTS 3개 키(authed·user·demo)만 초기화. 나머지 6개 DEFAULTS 키(mode·auto_enabled·kill_switch·pnl_kr_colors·symbol_modes·data_source)와 trade ack 세션 키(trade_ack_checked·_trade_ack_pending_message·_trade_ack_context)가 다음 로그인으로 누출. app/ui/state.py line 30 수정 필요."
inputs:
  - agents/lead_engineer/tasks/TASK-059-fix-logout-incomplete-state-reset.md
  - app/ui/state.py
target_files:
  - app/ui/state.py
  - tests/unit/test_state_logout.py
scope: "app/ui/state.py logout() 함수만 수정. 다른 함수(init_state·login·activate_kill·release_kill) 변경 금지. DEFAULTS 딕셔너리 변경 금지."
acceptance:
  - "logout() 후 DEFAULTS 9개 키 전체 기본값으로 초기화"
  - "logout() 후 trade_ack_checked·_trade_ack_pending_message·_trade_ack_context 세션에서 제거"
  - "symbol_modes 초기화 값이 DEFAULTS['symbol_modes']와 독립 사본 (aliasing 없음)"
  - "extra 키 없는 세션에서 logout() 호출 시 오류 없음"
  - "python -m pytest tests/unit/test_state_logout.py -q → 14 passed"
  - "python -m pytest tests/ -q green (기존 실패 2개 외 신규 실패 없음)"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_state_logout.py -q"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
handoff: "변경 파일 목록, 누출된 키 목록, TDD 실패→성공 증거, pytest 결과, gate 결과 보고."
stop_condition: "logout() 수정 후 즉시 중단. init_state()·DEFAULTS·다른 state.py 함수 변경 금지."
depends_on: []
---

# UNIT-TASK-059-001 — logout() 완전 세션 초기화

## Context

`app/ui/state.py` `logout()` (line 30)가 DEFAULTS 9개 키 중 3개만 초기화한다.

누출되는 키:
- `mode` → 이전 세션 자율성 레벨 ("L4" 등) 유지
- `auto_enabled` → 이전 세션 자동매매 활성 상태 유지
- `kill_switch` → 이전 세션 킬스위치 상태 유지
- `pnl_kr_colors` → 표시 설정 유지
- `symbol_modes` → 종목별 자율성 설정 유지
- `data_source` → 브로커 선택 유지
- `trade_ack_checked`, `_trade_ack_pending_message`, `_trade_ack_context` → trade 뷰 ack 상태 유지

## Target Files

- `app/ui/state.py`
- `tests/unit/test_state_logout.py`

## Scope

In scope: `logout()` 함수 본체 수정, 관련 단위테스트 신규 작성.

Out of scope: DEFAULTS 내용, init_state(), login(), activate_kill(), release_kill(), 다른 뷰/서비스 파일.

## Fix Approach

```python
import copy

_EXTRA_SESSION_KEYS: tuple[str, ...] = (
    "trade_ack_checked",
    "_trade_ack_pending_message",
    "_trade_ack_context",
)

def logout() -> None:
    for key, value in DEFAULTS.items():
        st.session_state[key] = copy.copy(value)
    for key in _EXTRA_SESSION_KEYS:
        st.session_state.pop(key, None)
```

## Acceptance Criteria

- `logout()` 후 DEFAULTS 9개 키 전체 기본값 초기화
- 3개 extra 키 세션에서 제거
- `symbol_modes` 독립 사본 (aliasing 없음)
- `python -m pytest tests/unit/test_state_logout.py -q` → 14 passed
- `python -m pytest tests/ -q` → 기존 2개 pre-existing 실패 외 신규 실패 없음
- `python scripts/check_agent_docs.py` 0 error

## 완료 기록

완료 시각: 2026-06-14T12:01:21+09:00

**변경 내용:**
- `app/ui/state.py`: `import copy` 추가, `_EXTRA_SESSION_KEYS` 모듈 상수 정의, `logout()` 전체 교체 (DEFAULTS 전체 순회 + copy.copy + extra 키 pop).
- `tests/unit/test_state_logout.py`: 신규 파일 14개 테스트. DEFAULTS 9개 키 각각 초기화 검증, symbol_modes 독립 사본 검증, extra 키 3개 제거 검증, extra 키 없을 때 오류 없음 검증.

**TDD 증거:**
- 수정 전: 9 FAILED (mode·auto_enabled·kill_switch·pnl_kr_colors·symbol_modes·data_source·trade_ack_checked·_trade_ack_pending_message·_trade_ack_context 누출)
- 수정 후: 14 passed (test_state_logout.py), 653 passed 전체 (기존 2 pre-existing 실패 불변)

**검증 결과:**
- `python -m pytest tests/unit/test_state_logout.py -q` → 14 passed
- `python -m pytest tests/ -q` → 653 passed, 2 pre-existing failures (test_top_bar_data_source.py)
- `python scripts/check_agent_docs.py` → 0 error, 85 warnings (pre-existing)
- `python scripts/work_schema_gate.py --items --check` → pass, findings=0
- `python scripts/build_task_index.py --check` → OK
- `python scripts/generate_views.py --check` → OK (66 tasks / 6 views)
