---
type: task
id: TASK-028
status: 보류
owner: Backend Engineer
assignees: [Backend Engineer, KIS API Engineer, QA]
priority: Medium
difficulty: 상
est_hours: 8
est_tokens: 70000
tags: [qa, order-types, stop, trailing, ioc, fok, moo, moc]
gate: Owner approval required before broker/order_flow changes that can affect live order behavior
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-009
created: 2026-06-12
created_at: 2026-06-12T12:27:28+09:00
updated_at: 2026-06-12T12:27:28+09:00
---

# TASK-028 Advanced Order Types Test Support

작업 ID: TASK-028
상태: 보류
Owner: Backend Engineer
기록 시각: 2026-06-12T12:27:28+09:00

## 배경

카탈로그의 stop, stop-limit, trailing stop, market-on-open, market-on-close, IOC, FOK 케이스는 현재 실행 불가능하다. 현재 enum은 `LIMIT`와 `MARKET`만 가진다.

## 왜 아직 실행 못하는가

- `OrderType`/DB schema/order_flow/broker adapter가 고급 주문 유형을 표현하지 못한다.
- KIS/KRX 세션별 허용 주문유형과 취소/정정 정책이 반영되어야 한다.

## Done When

- 주문 유형별 state machine과 risk policy가 정의된다.
- mock tests가 각 order type trigger/cancel/reject path를 검증한다.
- KIS paper smoke는 별도 승인된 최소 주문으로만 실행한다.

## Verification

- advanced order type unit/integration tests
- generated scenario catalog rows promoted from catalog-only to executable
