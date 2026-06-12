---
type: task
id: TASK-030
status: 보류
owner: Backend Engineer
assignees: [Backend Engineer, KIS API Engineer, QA]
priority: Low
difficulty: 상
est_hours: 8
est_tokens: 70000
tags: [qa, basket, block-trade, multi-leg, execution]
gate: Owner approval required before actual block/basket venue or broker submission support
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-009
created: 2026-06-12
created_at: 2026-06-12T12:27:28+09:00
updated_at: 2026-06-12T12:27:28+09:00
---

# TASK-030 Block/Basket Execution Tests

작업 ID: TASK-030
상태: 보류
Owner: Backend Engineer
기록 시각: 2026-06-12T12:27:28+09:00

## 배경

현재 테스트는 multi-asset rebalance를 여러 단일 조건으로 처리하는 basket proxy만 검증한다. KRX block/basket venue submission 자체는 구현되어 있지 않다.

## 왜 아직 실행 못하는가

- basket order id, leg-level fill, all-or-none/partial basket 정책, venue constraints가 없다.
- 실제 block/basket 제출은 주문 경로 R3 surface다.

## Done When

- basket intent와 leg execution model이 분리된다.
- mock basket fill/partial/reject 테스트가 추가된다.
- actual venue path는 Owner 승인 전까지 비활성이다.

## Verification

- basket mock integration tests
- order log and execution log leg consistency checks
