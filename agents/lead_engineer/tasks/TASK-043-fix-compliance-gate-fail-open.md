---
type: task
id: TASK-043
status: 대기
owner: Backend Engineer
assignees: [Backend Engineer, Compliance Officer, QA]
priority: High
difficulty: 하
est_hours: 4
est_tokens: 30000
tags: [bug, safety, compliance, gate, fail-open, trading]
gate: safety bug — Phase 3 전 필수 수정
trigger_meeting: TASK-039 시작 전 완료 필수
audit_log: AUDIT-2026-06-13-001
created: 2026-06-13
created_at: 2026-06-13T01:33:29+09:00
updated_at: 2026-06-13T01:33:29+09:00
---

# TASK-043 fix: compliance 게이트 fail-open 버그

작업 ID: TASK-043
상태: 대기
Owner: Backend Engineer
기록 시각: 2026-06-13T01:33:29+09:00

## ⚠ 안전 버그 (High Priority — Phase 3 전 필수 수정)

**증상**: agent/compliance 호출이 오류를 반환해도 게이트가 통과로 분류되고, `compliance="passed"` 로 오기록된다.

## 버그 내용

`app/services/trading.py`의 `save_condition_with_gates()` verdict 결정 휴리스틱이 agent 호출 오류 문자열("호출 오류", "오류" 등)을 통과 케이스로 분류한다.

**문제**: agent 호출이 실패(타임아웃, 연결 오류, 예외)하면 반환값이 오류 문자열인데, 이 문자열이 "passed"/"caution"/"blocked" 키워드를 포함하지 않으므로 기본값 통과로 처리됨. 결과적으로 **fail-open** 동작 + `compliance="passed"` 오기록.

## 수정 방향

`GateResult` 에 `error` 상태 추가:

```python
class GateResult:
    verdict: Literal["passed", "caution", "blocked", "error"]
    message: str
    ...
```

verdict 결정 로직 수정:
- agent 호출이 예외/타임아웃이면 → `verdict="error"`
- 반환값이 오류 문자열 패턴이면 → `verdict="error"`
- `verdict="error"` 시 **fail-closed** 권장: 조건 저장 차단 또는 caution 처리

Phase 3 HTTP 매핑 예고:
- `verdict="blocked"` → HTTP 422
- `verdict="caution"` → HTTP 409 + `ack_token`
- `verdict="error"` → HTTP 503 (게이트 오류) 또는 HTTP 422 (안전 차단)

## 완료 기준

- `GateResult.verdict` 에 `"error"` 상태 추가
- agent 호출 오류 시 fail-closed 동작 확인 (통과 차단)
- `compliance="passed"` 오기록 방지 테스트 추가
- `python -m pytest tests/ -q` green

## 근거 경로

- `app/services/trading.py`: `save_condition_with_gates()`, `GateResult`
- Phase 3 게이트 설계: `docs/superpowers/specs/2026-06-13-ui-overhaul-design.md` §Phase 3

## Done When

- `GateResult` error 상태 추가
- fail-open → fail-closed 변경 확인 테스트 통과
- 전체 pytest green
