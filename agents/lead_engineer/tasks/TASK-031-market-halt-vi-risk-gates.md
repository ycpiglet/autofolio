---
type: task
id: TASK-031
status: 보류
owner: Compliance Officer
assignees: [Compliance Officer, Backend Engineer, QA]
priority: High
difficulty: 중
est_hours: 5
est_tokens: 50000
tags: [qa, risk, compliance, halt, vi, disclosure]
gate: Owner approval required before app/risk or live order-blocking policy changes
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-009
created: 2026-06-12
created_at: 2026-06-12T12:27:28+09:00
updated_at: 2026-06-12T12:27:28+09:00
---

# TASK-031 Market Halt/VI Risk Gates

작업 ID: TASK-031
상태: 보류
Owner: Compliance Officer
기록 시각: 2026-06-12T12:27:28+09:00

## 배경

카탈로그의 halt, VI, disclosure block 케이스는 현재 일부 UI/system_state 수준만 있다. 엔진 주문 차단 risk gate로는 완전하지 않다.

## 왜 아직 실행 못하는가

- KRX VI/거래정지 상태를 엔진 입력으로 표준화하지 않았다.
- `app/risk/**` 변경은 Autofolio R3 surface다.

## Done When

- halt/VI/disclosure state source와 stale policy가 정의된다.
- mock engine tests가 주문 차단/해제/기록을 검증한다.
- UI와 engine이 같은 차단 사유를 표시한다.

## Verification

- compliance/risk pytest selector
- UI/backend disclosure gate regression
