---
unit_id: UNIT-TASK-051-001
task_id: TASK-051
task_set_id: TASKSET-AUTOFOLIO-SAFETY-FIXES
project_id: PROJECT-AUTOFOLIO
status: worker_ready
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, security, repeated_failure]
context: "save_condition_with_gates()의 verdict 휴리스틱이 agent 호출 오류 문자열('호출 오류' 등)을 reject/거부 키워드 미포함으로 통과 처리 → compliance='passed' 오기록. GateResult에 error 상태 추가 후 fail-closed 처리 필요."
inputs:
  - agents/lead_engineer/tasks/TASK-051-fix-compliance-gate-fail-open.md
  - app/services/trading.py
target_files:
  - app/services/trading.py
  - tests/unit/test_compliance_gate.py
scope: "app/services/trading.py 의 GateResult 클래스 및 save_condition_with_gates() verdict 로직만 수정. Phase 3 HTTP 매핑은 이 유닛에서 구현하지 않음."
acceptance:
  - "GateResult.status에 'error' 상태 추가"
  - "GateResult.compliance에 'error' 값 추가"
  - "agent 호출 오류 시 fail-closed 동작 (통과 차단) 확인"
  - "compliance='passed' 오기록 방지 테스트 추가 및 통과"
  - "python -m pytest tests/ -q green"
verification:
  - "python -m pytest tests/unit/test_compliance_gate.py -q"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
handoff: "변경된 파일 목록, GateResult 변경 내용, fail-closed 테스트 결과 보고."
stop_condition: "GateResult + save_condition_with_gates() verdict 로직 수정 후 즉시 중단. Phase 3 HTTP 엔드포인트, UI 변경, 다른 서비스로 확장 금지."
depends_on: []
---

# UNIT-TASK-051-001 — compliance 게이트 fail-open 버그 수정

## Context

`app/services/trading.py`의 `save_condition_with_gates()` verdict 결정 휴리스틱이
agent 호출 오류 문자열("호출 오류", "오류" 등)을 "reject"/"거부"/"caution"/"주의"
키워드를 포함하지 않는 것으로 보고 기본값 **통과**로 처리한다.

결과: agent 호출이 실패(타임아웃·연결 오류·예외)해도 compliance="passed"로 오기록되어
**fail-open** 동작 발생 — Phase 3 전 필수 수정.

## Inputs

- `agents/lead_engineer/tasks/TASK-051-fix-compliance-gate-fail-open.md` — 원본 버그 명세
- `app/services/trading.py` — `GateResult`, `save_condition_with_gates()` 구현

## Target Files

- `app/services/trading.py`
- `tests/unit/test_compliance_gate.py`

## Scope

In scope: `GateResult` 클래스 status/compliance 확장, `save_condition_with_gates()` 오류 분기.

Out of scope: Phase 3 HTTP 엔드포인트 매핑 (`status="error"` → HTTP 503/422), UI 변경,
다른 서비스 레이어, 인증·권한 변경.

## Steps

1. `app/services/trading.py`에서 `GateResult` 클래스 및 `save_condition_with_gates()` 확인.
2. `GateResult.status`에 `"error"` 리터럴 추가.
3. `GateResult.compliance`에 `"error"` 값 추가.
4. `save_condition_with_gates()` verdict 로직 수정:
   - agent 호출이 예외/타임아웃이면 → `status="error"`, `compliance="error"`, fail-closed.
   - 반환값이 오류 문자열 패턴("오류", "호출 오류")이면 → 동일 처리.
5. `test_compliance_gate.py` (또는 신규) 에 fail-closed 테스트 추가.
6. 전체 pytest green 확인.

## Acceptance Criteria

- `GateResult.status`에 `"error"` 상태 추가
- `GateResult.compliance`에 `"error"` 값 추가
- agent 호출 오류 시 fail-closed 동작 (통과 차단) 확인
- `compliance="passed"` 오기록 방지 테스트 추가 및 통과
- `python -m pytest tests/ -q` green

## Verification

```powershell
python -m pytest tests/unit/test_compliance_gate.py -q
python -m pytest tests/ -q
python scripts/check_agent_docs.py
```

## Handoff

변경된 파일 목록, `GateResult` 변경 diff 요약, fail-closed 테스트 명세, pytest 결과 보고.

## Stop Boundary

`GateResult` + `save_condition_with_gates()` verdict 로직 수정 후 즉시 중단.
Phase 3 HTTP 매핑(`/api/conditions` 엔드포인트), UI 코드, 다른 서비스로 확장 금지.
