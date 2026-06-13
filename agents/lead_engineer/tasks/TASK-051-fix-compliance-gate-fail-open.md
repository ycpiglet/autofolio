---
type: task
id: TASK-051
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, Compliance Officer, QA]
priority: High
difficulty: 중
est_hours: 4
est_tokens: 30000
tags: [bug, safety, compliance, gate, fail-open, trading]
gate: safety bug — Phase 3 전 필수 수정
trigger_meeting: TASK-047 시작 전 완료 필수
audit_log: AUDIT-2026-06-13-007
created: 2026-06-13
created_at: 2026-06-13T01:33:29+09:00
updated_at: 2026-06-14T04:16:05+09:00
---

# TASK-051 fix: compliance 게이트 fail-open 버그

작업 ID: TASK-051
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-13
기록 시각: 2026-06-13T01:33:29+09:00
요청자: Owner
수행자: Lead Engineer
의도: compliance 게이트 fail-open 버그 수정 — agent 호출 오류 시 통과 오분류 및 compliance="passed" 오기록 방지
대상: app/services/trading.py save_condition_with_gates(), GateResult 클래스
방법: GateResult에 error 상태 추가, agent 오류 반환값 패턴 감지 후 fail-closed 처리로 변경
감사 로그: AUDIT-2026-06-13-007

## ⚠ 안전 버그 (High Priority — Phase 3 전 필수 수정)

**증상**: agent/compliance 호출이 오류를 반환해도 게이트가 통과로 분류되고, `compliance="passed"` 로 오기록된다.

## 버그 내용

`app/services/trading.py`의 `save_condition_with_gates()` verdict 결정 휴리스틱이 agent 호출 오류 문자열("호출 오류", "오류" 등)을 통과 케이스로 분류한다.

**문제**: agent 호출이 실패(타임아웃, 연결 오류, 예외)하면 반환값이 오류 문자열인데, 이 문자열이 "reject"/"거부"/"caution"/"주의" 키워드를 포함하지 않으므로 기본값 통과로 처리됨. 결과적으로 **fail-open** 동작 + `compliance="passed"` 오기록.

## 수정 방향

`GateResult` 에 `error` status 추가:

```python
class GateResult:
    status: Literal["saved", "blocked_disclosure", "rejected", "needs_acknowledgement", "error"]
    message: str
    compliance: Literal["passed", "caution_acked", "skipped", "error"] | None = None
```

status/compliance 결정 로직 수정:
- agent 호출이 예외/타임아웃이면 → `status="error"`, `compliance="error"`
- 반환값이 오류 문자열 패턴("오류", "호출 오류" 등)이면 → `status="error"`, `compliance="error"`
- `status="error"` 시 **fail-closed** 권장: 조건 저장 차단 또는 caution 처리

Phase 3 HTTP 매핑 예고:
- `status="rejected"` → HTTP 422
- `status="needs_acknowledgement"` → HTTP 409 + `ack_token`
- `status="error"` → HTTP 503 (게이트 오류) 또는 HTTP 422 (안전 차단)

## 완료 기준

- `GateResult.status` 에 `"error"` 상태 추가, `compliance` 에 `"error"` 값 추가
- agent 호출 오류 시 fail-closed 동작 확인 (통과 차단)
- `compliance="passed"` 오기록 방지 테스트 추가
- `python -m pytest tests/ -q` green

## 근거 경로

- `app/services/trading.py`: `save_condition_with_gates()`, `GateResult`
- Phase 3 게이트 설계: `docs/superpowers/specs/2026-06-13-ui-overhaul-design.md` §Phase 3

## Done When

- `GateResult.status` `"error"` + `compliance` `"error"` 추가
- fail-open → fail-closed 변경 확인 테스트 통과
- 전체 pytest green

## v1 이행 (파일럿)

이 태스크는 agent_runtime v0.2.0 work-item 스키마로 이행되었다.
실행 상세 명세는 v1 unit 스펙을 참고:

- Initiative: `agents/project/initiatives/INIT-AUTOFOLIO-SAFETY-FIXES.md`
- Taskset: `agents/project/initiatives/TASKSET-AUTOFOLIO-SAFETY-FIXES.md`
- Unit spec: `agents/lead_engineer/tasks/units/TASK-051/UNIT-TASK-051-001.md`

## 완료 기록

완료 시각: 2026-06-14T04:16:05+09:00
검토자: Backend Engineer + QA (Codex self-review)
감사 로그: AUDIT-2026-06-13-007

UNIT-TASK-051-001 완료: `GateResult`에 `"error"` 상태 추가, `save_condition_with_gates()`에 `"호출 오류"` 감지 후 fail-closed 처리 적용. `test_compliance_agent_call_error_fail_closed` 추가, 615 tests passed.

## 증거

- `app/services/trading.py`: `GateResult.status` Literal에 `"error"` 추가, `GateResult.compliance` Literal에 `"error"` 추가, verdict 로직에 `"호출 오류"` 감지 분기 추가 (fail-closed)
- `tests/unit/test_trading_gates.py`: `test_compliance_agent_call_error_fail_closed` 신규 추가 — `ask()` 오류 반환 시 `status="error"`, `compliance="error"`, `add_condition` 미호출 검증
- 수정 전: 신규 테스트 `AssertionError: expected 'error', got 'saved'` (fail-open 재현)
- 수정 후: 7 passed (test_trading_gates.py), 615 passed (전체)
- `check_agent_docs.py`: 0 error(s), 104 warning(s)

## 리뷰

- 오류 감지 패턴 `"호출 오류"` — `app/services/agents.py` line 166의 `f"[{agent_short}] 호출 오류: {exc}"` 센티넬과 정확히 일치.
- REJECT/CAUTION 검사 후, pass fall-through 전에 오류 분기 삽입 — 키워드 우선순위 보존.
- `status="error"` 반환 시 `add_condition` 미호출 — 조건 저장 차단 확인.
- trade.py dispatch의 `else` 분기가 `st.error()` 호출 후 stop — UI도 자동으로 fail-closed 처리됨 (view 수정 불필요).

## Independent Audit

판정: 통과 (TDD — 신규 테스트 수정 전 FAILED, 수정 후 PASSED. 전체 pytest 615 passed.)
