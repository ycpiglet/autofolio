---
type: task
id: TASK-064
status: 완료
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
updated_at: 2026-06-14T09:35:04+09:00
---

# TASK-064 fix: 주문 조건 TOCTOU 레이스 (order_flow.py + repositories.py)

작업 ID: TASK-064
상태: 완료
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
- Unit spec: `agents/lead_engineer/tasks/units/TASK-064/UNIT-TASK-064-001.md`

## 완료 기록

완료 시각: 2026-06-14T09:35:04+09:00
검토자: Backend Engineer + QA (Codex self-review)
감사 로그: AUDIT-2026-06-14-001

UNIT-TASK-064-001 완료: `ConditionStatus.PROCESSING` 추가, `Repository.atomic_claim_condition()` CAS 메서드 구현, `LiveTradingEngine.run_once()` CAS 클레임 배선 + 미트리거 복구. 신규 테스트 9개 추가, 626 passed.

## 증거

- `app/common/enums.py`: `ConditionStatus.PROCESSING = "PROCESSING"` 추가
- `app/database/repositories.py`: `atomic_claim_condition(condition_id) -> bool` 추가 — `UPDATE trade_conditions SET status='PROCESSING', updated_at=CURRENT_TIMESTAMP WHERE id=? AND status='ACTIVE'`, `rowcount==1` 반환
- `app/engine/live_trading_engine.py`: `run_once()` 루프에 CAS 클레임 추가 — 클레임 실패 시 skip (중복 주문 방지); `executed=False` + status=PROCESSING 시 ACTIVE 복구; 예외 시 ERROR 복구
- `tests/unit/test_condition_toctou_cas.py`: 신규 생성 — 9개 테스트 (enum smoke, CAS primitive 4개, threading.Barrier 동시성 테스트, old-path 버그 문서화, engine level 2개)
- 수정 전: `test_cas_claim_second_caller_loses` FAILED (두 번째 claim도 rowcount==1 반환)
- 수정 후: 9 passed (CAS 테스트 파일), 626 passed (전체)
- `check_agent_docs.py`: 0 error(s)
- `work_schema_gate.py --items --check`: findings=0
- `build_task_index.py --check`: OK
- `generate_views.py --check`: OK

## 리뷰

- `trade_conditions.status` 컬럼이 TEXT + 기본값, CHECK 제약 없음 → 'PROCESSING' 추가 스키마 변경 불필요
- `process_condition_once()`의 성공 분기 (`_mark_condition_triggered()`)가 TRIGGERED로 덮어쓰고, 실패 분기들이 ERROR로 덮어씀 → PROCESSING stuck 없음
- 미트리거 조건(가격 불충족, 안전 차단)은 PROCESSING→ACTIVE 복구하여 다음 run_once() 사이클에 재평가됨
- 엔진 예외 핸들러가 PROCESSING→ERROR 복구 → unhandled exception에서도 조건 복구됨
- `list_active_conditions()`는 `WHERE status='ACTIVE'`만 반환 → PROCESSING 행은 다음 run에 자동 제외 (경쟁 caller silently skips)

## Independent Audit

판정: 통과 (TDD — CAS 테스트 수정 전 FAILED, 수정 후 PASSED. 전체 pytest 626 passed. 기존 paper_scenario_matrix 17 tests 포함 회귀 없음.)
