---
unit_id: UNIT-TASK-052-001
task_id: TASK-052
task_set_id: TASKSET-AUTOFOLIO-SAFETY-FIXES
project_id: PROJECT-AUTOFOLIO
status: worker_ready
horizon: unit
model_tier: worker_standard
escalation_triggers: [ambiguity, repeated_failure]
context: "trade.py의 lv_comply_ack 체크박스가 버튼 블록 안에서만 렌더되어 Streamlit 위젯 클린업 시 상태 소실 → caution_acknowledged=False 유지 → needs_acknowledgement 영구 루프. st.session_state로 ack 상태 분리 필요."
inputs:
  - agents/lead_engineer/tasks/TASK-052-fix-trade-ack-checkbox-loop.md
  - app/ui/views/trade.py
  - app/services/trading.py
target_files:
  - app/ui/views/trade.py
  - tests/unit/test_trade_view.py
scope: "app/ui/views/trade.py 의 lv_comply_ack 체크박스 렌더 로직만 수정. app/services/trading.py 변경 금지 (서비스 레이어는 이미 caution_acknowledged 파라미터 지원)."
acceptance:
  - "needs_acknowledgement=True 상태에서 체크박스 체크 → 재제출 → 루프 없이 정상 저장"
  - "lv_comply_ack를 st.session_state['trade_ack_checked']로 분리"
  - "python -m pytest tests/ -q green (기존 trade 화면 테스트 유지)"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_trade_view.py -q"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
handoff: "변경된 파일 목록, ack 상태 분리 방식, pytest 결과 보고."
stop_condition: "lv_comply_ack 체크박스 세션 상태 분리 수정 후 즉시 중단. 서비스 레이어, 다른 뷰 파일, UI 리팩터로 확장 금지."
depends_on: []
---

# UNIT-TASK-052-001 — trade 뷰 ack 체크박스 영구 루프 수정

## Context

`app/ui/views/trade.py`의 `lv_comply_ack` 체크박스가 버튼 블록(조건부 렌더 블록) 안에서만
렌더된다. Streamlit은 재렌더 사이클에서 해당 블록이 사라지면 위젯을 클린업한다.

이로 인해:
1. 조건 저장 → CAUTION → `needs_acknowledgement=True` → ack 체크박스 렌더
2. 체크박스 체크 → 버튼 블록 구조 변경 → Streamlit 위젯 클린업
3. 체크박스 상태 소실 → `caution_acknowledged=False` 유지
4. 재제출 → 다시 CAUTION → 무한 루프

`app/services/trading.py`의 `save_condition_with_gates(caution_acknowledged=...)`는
이미 파라미터를 지원하므로 **뷰 수정만 필요**.

## Inputs

- `agents/lead_engineer/tasks/TASK-052-fix-trade-ack-checkbox-loop.md` — 원본 버그 명세
- `app/ui/views/trade.py` — `lv_comply_ack` 렌더 로직
- `app/services/trading.py` — `save_condition_with_gates()` 서명 참조

## Target Files

- `app/ui/views/trade.py`
- `tests/unit/test_trade_view.py`

## Scope

In scope: `app/ui/views/trade.py` 내 `lv_comply_ack` 체크박스 렌더 로직 및 세션 상태 분리.

Out of scope: `app/services/trading.py` 변경, 다른 뷰 파일, 백엔드 API, UI 대개편 Phase 3 작업.

## Steps

1. `app/ui/views/trade.py`에서 `lv_comply_ack` 체크박스 렌더 블록 확인.
2. `st.session_state["trade_ack_checked"]` 변수로 ack 상태 분리.
3. 체크박스를 조건부 블록 밖 독립 위젯으로 렌더 (또는 Streamlit `key=` 안정화).
4. 재제출 시 `caution_acknowledged=st.session_state.get("trade_ack_checked", False)` 전달.
5. 기존 trade 화면 테스트 유지 확인.
6. 전체 pytest green 확인.

## Acceptance Criteria

- `needs_acknowledgement=True` 상태에서 체크박스 체크 → 재제출 → 루프 없이 정상 저장
- `lv_comply_ack`를 `st.session_state["trade_ack_checked"]`로 분리
- `python -m pytest tests/ -q` green (기존 trade 화면 테스트 유지)
- `python scripts/check_agent_docs.py` 0 error

## Verification

```powershell
python -m pytest tests/unit/test_trade_view.py -q
python -m pytest tests/ -q
python scripts/check_agent_docs.py
```

## Handoff

변경된 파일 목록, ack 상태 분리 구현 방식(session_state 키 이름 포함), pytest 결과 보고.

## Stop Boundary

`lv_comply_ack` 체크박스 세션 상태 분리 수정 후 즉시 중단.
`app/services/trading.py`, 다른 Streamlit 뷰 파일, Phase 3 API 레이어로 확장 금지.
