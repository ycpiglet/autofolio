---
type: task
id: TASK-029
status: 대기
owner: Backend Engineer
assignees: [Backend Engineer, QA]
priority: High
difficulty: 중
est_hours: 4
est_tokens: 45000
tags: [qa, order-lifecycle, partial-fill, fix, mock]
gate: mock/test harness first; live order_flow behavior changes require Owner review
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-009
created: 2026-06-12
created_at: 2026-06-12T12:27:28+09:00
updated_at: 2026-06-12T12:27:28+09:00
---

# TASK-029 FIX-Style Order Lifecycle Tests

작업 ID: TASK-029
상태: 대기
Owner: Backend Engineer
기록 시각: 2026-06-12T12:27:28+09:00

## 배경

카탈로그의 partial fill, pending cancel, too-late-to-cancel, cancel/replace race 케이스는 현재 일부만 실행된다. `PENDING`, `FILLED`, `CANCELED`, `FAILED`는 있으나 부분체결을 별도 지속 상태로 모델링하지 않는다.

## 왜 아직 실행 못하는가

- `OrderResult`와 DB log가 누적 체결/잔량/부분체결 상태를 충분히 표현하지 못한다.
- `OrderFlow`는 pending timeout 후 `ERROR`로 닫는 단순 모델이다.

## Done When

- mock broker가 scripted partial fill sequence를 제공한다.
- order/execution log가 누적 체결과 잔량을 검증한다.
- too-late-to-cancel/cancel-reject 경계 테스트가 추가된다.

## Verification

- `pytest tests/integration -k order_lifecycle`
- 기존 paper scenario matrix 회귀
