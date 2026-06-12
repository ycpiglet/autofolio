---
type: task
id: TASK-029
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, QA]
priority: High
difficulty: 중
est_hours: 4
est_tokens: 45000
tags: [qa, order-lifecycle, partial-fill, fix, mock]
gate: mock/test harness first; live order_flow behavior changes require Owner review
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-015
created: 2026-06-12
created_at: 2026-06-12T12:27:28+09:00
updated_at: 2026-06-12T23:51:57+09:00
---

# TASK-029 FIX-Style Order Lifecycle Tests

작업 ID: TASK-029
상태: 완료
Owner: Backend Engineer
기록 시각: 2026-06-12T12:27:28+09:00

## 배경

카탈로그의 partial fill, pending cancel, too-late-to-cancel, cancel/replace race 케이스는 현재 일부만 실행된다. `PENDING`, `FILLED`, `CANCELED`, `FAILED`는 있으나 부분체결을 별도 지속 상태로 모델링하지 않는다.

## 왜 아직 실행 못하는가

- `OrderResult`와 DB log가 누적 체결/잔량/부분체결 상태를 충분히 표현하지 못한다.
- `OrderFlow`는 pending timeout 후 `ERROR`로 닫는 단순 모델이다.

## 완료 기록

완료 시각: 2026-06-12T23:51:57+09:00
검토자: Backend Engineer + QA (Codex self-review)
감사 로그: AUDIT-2026-06-12-015
실측 비용 (시간): 약 0.25h
실측 비용 (LLM 토큰): unknown

- 원 요청: partial fill, pending cancel, too-late-to-cancel, cancel/replace race 계열 FIX-style order lifecycle gap을 mock/test-harness first 범위에서 실행 가능하게 만든다.
- 실제 작업:
  - `tests/integration/test_order_lifecycle.py`를 추가했다.
  - test-local `PendingThenStatusBroker`와 `PartialFillLedger` harness로 partial fill sequence, weighted average fill price, remaining quantity, pending-limit fill-before-cancel, cancel reject, too-late-to-cancel late fill 기록을 검증했다.
  - test fixture에서만 isolated SQLite risk limit을 높여 lifecycle path가 안전 게이트가 아니라 주문 lifecycle을 검증하게 했다.
- 결과:
  - `pytest tests/integration -k order_lifecycle -q` 기준 8 passed.
  - existing paper scenario matrix 16 passed.
  - production `OrderFlow`, KIS broker, risk policy, schema/migration은 변경하지 않았다.
- 남은 이슈:
  - production partial-fill persistent state와 cancel-replace race 처리는 여전히 Owner review가 필요한 order-flow behavior change다.
  - 이번 TASK는 "mock/test harness first" 완료로 닫고, live/order-flow semantics는 별도 R3 follow-up으로 남긴다.

## Done When

- mock broker가 scripted partial fill sequence를 제공한다.
- order/execution log가 누적 체결과 잔량을 검증한다.
- too-late-to-cancel/cancel-reject 경계 테스트가 추가된다.

## Verification

- `pytest tests/integration -k order_lifecycle -q` -> 8 passed.
- `pytest tests/integration/test_paper_scenario_matrix.py -q` -> 16 passed.
- `python -m py_compile tests/integration/test_order_lifecycle.py` -> OK.
- `git diff --check` -> OK.
