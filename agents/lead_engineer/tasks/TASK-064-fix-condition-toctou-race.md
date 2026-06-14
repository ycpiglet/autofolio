---
type: task
id: TASK-064
status: 대기
owner: Backend Engineer
assignees: [Backend Engineer, QA]
priority: Critical
difficulty: 상
est_hours: 8
est_tokens: 60000
tags: [bug, safety, race-condition, database, order-flow]
gate: safety bug
trigger_meeting: 즉시 처리 권고
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T00:00:00+09:00
---

# TASK-064 fix: 주문 조건 TOCTOU 레이스 (order_flow.py + repositories.py)

작업 ID: TASK-064
상태: 대기
Owner: Backend Engineer
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: Backend Engineer
의도: repositories.py에 atomic CAS로 TOCTOU 레이스 조건 제거
대상: app/trading/order_flow.py, app/database/repositories.py list_active_conditions(), update_condition_status()
방법: atomic CAS UPDATE 구현(ACTIVE→PROCESSING) + 동시 run_once() 이중 주문 방지 통합테스트 추가
감사 로그: AUDIT-2026-06-14-001

## ⚠ 안전 버그 (Critical)

**증상**: 같은 주문 조건이 중복 실행되어 의도치 않은 이중 주문 발생 가능.

## 버그 내용

`list_active_conditions()` 조회 후 `update_condition_status(TRIGGERED)` 업데이트 사이에 두 번의 동시 `run_once()` 호출이 발생하면 같은 조건이 두 번 처리될 수 있음.

**Time-Of-Check-To-Time-Of-Use (TOCTOU)**: 두 스레드/프로세스가 동시에 `status='ACTIVE'` 조건을 읽고 각자 처리 시작.

## 수정 방향

1. `repositories.py`에 atomic CAS(Compare-And-Swap) 구현:
   ```sql
   UPDATE order_conditions
   SET status = 'PROCESSING'
   WHERE id = ? AND status = 'ACTIVE'
   ```
   - rowcount == 1이면 처리 진행, 0이면 이미 다른 호출이 선점 → skip

2. `list_active_conditions()` → CAS atomic 업데이트 → 처리 → `TRIGGERED` 업데이트 흐름으로 변경

3. 동시성 통합 테스트:
   - 두 스레드가 동시에 `run_once()` 호출
   - 하나만 처리되고 하나는 skip 확인
   - 이중 주문 발생 없음 확인

## 완료 기준

- condition 상태 atomic CAS 구현
- 동시 호출 시 하나만 처리 보장
- 동시성 통합 테스트 통과

## Done When

- condition 상태 atomic CAS 구현
- 동시 호출 시 하나만 처리 보장
- 동시성 통합 테스트

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`
