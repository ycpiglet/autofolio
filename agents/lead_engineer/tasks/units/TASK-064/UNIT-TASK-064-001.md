---
unit_id: UNIT-TASK-064-001
task_id: TASK-064
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "run_once()가 list_active_conditions() 후 process_condition_once() 사이 TOCTOU로 두 스레드가 같은 ACTIVE 조건을 동시 처리 → 중복 주문 위험. app/engine/live_trading_engine.py + app/database/repositories.py 수정 필요."
inputs:
  - agents/lead_engineer/tasks/TASK-064-fix-condition-toctou-race.md
  - app/engine/live_trading_engine.py
  - app/database/repositories.py
  - app/common/enums.py
  - app/database/schema.sql
target_files:
  - app/common/enums.py
  - app/database/repositories.py
  - app/engine/live_trading_engine.py
  - tests/unit/test_condition_toctou_cas.py
scope: "atomic_claim_condition() CAS 메서드 추가 + run_once() CAS 클레임 적용 + ConditionStatus.PROCESSING 추가. 다른 엔진 로직·스키마 마이그레이션 변경 금지."
acceptance:
  - "Repository.atomic_claim_condition(id) → bool 구현 완료"
  - "두 번째 atomic_claim_condition() 호출이 False 반환"
  - "run_once() 이 ACTIVE→PROCESSING CAS 클레임 성공 시에만 process_condition_once() 호출"
  - "미트리거 조건 PROCESSING→ACTIVE 복구 (재평가 가능)"
  - "예외 시 PROCESSING→ERROR 복구 (stuck 방지)"
  - "test_concurrent_claims_only_one_wins 통과"
  - "test_run_once_atomic_claim_prevents_double_order 통과"
  - "python -m pytest tests/ -q green (626 passed)"
  - "python scripts/check_agent_docs.py 0 error"
  - "python scripts/work_schema_gate.py --items --check findings=0"
verification:
  - "python -m pytest tests/unit/test_condition_toctou_cas.py -v"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
  - "python scripts/work_schema_gate.py --items --check"
  - "python scripts/build_task_index.py --check"
handoff: "변경 파일 목록, pytest 결과 (626 passed), CAS 구현 확인, threaded test 결과 보고."
stop_condition: "atomic_claim_condition() + run_once() CAS 배선 후 즉시 중단. 다른 엔진 기능·UI·스키마 마이그레이션으로 확장 금지."
depends_on: []
---

# UNIT-TASK-064-001 — 주문 조건 TOCTOU 레이스 제거 (atomic CAS claim)

## Context

`LiveTradingEngine.run_once()` (`app/engine/live_trading_engine.py`)가
`repo.list_active_conditions()` 조회 후 `order_flow.process_condition_once(condition)` 호출 전
상태 변경 없이 진행하므로, 두 스레드가 동시에 같은 ACTIVE 조건을 읽고 각자 처리 시작 가능.

**TOCTOU**: 조회(Check)와 처리(Use) 사이에 원자적 소유권 전환이 없음 → 중복 주문 위험.

## Inputs

- `agents/lead_engineer/tasks/TASK-064-fix-condition-toctou-race.md`
- `app/engine/live_trading_engine.py`
- `app/database/repositories.py`
- `app/common/enums.py`
- `app/database/schema.sql`

## Target Files

- `app/common/enums.py` — `ConditionStatus.PROCESSING` 추가
- `app/database/repositories.py` — `atomic_claim_condition()` 추가
- `app/engine/live_trading_engine.py` — `run_once()` CAS 클레임 배선
- `tests/unit/test_condition_toctou_cas.py` — 신규 테스트

## Scope

In scope: CAS 메서드 추가 + `run_once()` 배선 + `PROCESSING` 상태 추가.

Out of scope: 스키마 마이그레이션, UI, 다른 엔진 메서드, `process_condition_once()` 로직 변경.

## Steps

1. `app/common/enums.py` `ConditionStatus`에 `PROCESSING = "PROCESSING"` 추가.
2. `app/database/repositories.py`에 `atomic_claim_condition(id) -> bool` 추가.
   SQL: `UPDATE trade_conditions SET status='PROCESSING' WHERE id=? AND status='ACTIVE'`
   반환: `cursor.rowcount == 1`
3. `app/engine/live_trading_engine.py` `run_once()` 수정:
   - 각 condition 루프에 `if not self.repo.atomic_claim_condition(cid): continue` 추가.
   - `executed=False` 반환 시 상태가 아직 PROCESSING이면 ACTIVE로 복구 (재평가 허용).
   - 예외 핸들러에 `self.repo.update_condition_status(cid, ConditionStatus.ERROR.value)` (PROCESSING→ERROR).
4. `tests/unit/test_condition_toctou_cas.py` 신규 생성 (TDD 순서 준수).

## Acceptance Criteria

- `Repository.atomic_claim_condition()` 구현 완료
- 두 번째 claim 호출 False 반환
- `run_once()` CAS 클레임 통과 시에만 `process_condition_once()` 호출
- 미트리거 조건 PROCESSING→ACTIVE 복구 (다음 사이클 재평가 가능)
- 예외 시 ERROR 상태로 복구 (PROCESSING stuck 방지)
- 전체 pytest green (626 passed)

## Verification

```powershell
python -m pytest tests/unit/test_condition_toctou_cas.py -v
python -m pytest tests/ -q
python scripts/check_agent_docs.py
python scripts/work_schema_gate.py --items --check
python scripts/build_task_index.py --check
```

## Handoff

변경 파일 목록, pytest 전체 카운트, CAS + 엔진 배선 확인 보고.

## Stop Boundary

`atomic_claim_condition()` + `run_once()` 수정 후 즉시 중단.
UI, 마이그레이션, 인접 모듈 확장 금지.

## 완료 기록

완료 시각: 2026-06-14T09:35:04+09:00

**변경 내용:**
- `app/common/enums.py`: `ConditionStatus.PROCESSING = "PROCESSING"` 추가
- `app/database/repositories.py`: `atomic_claim_condition(condition_id) -> bool` 추가. `UPDATE trade_conditions SET status='PROCESSING' WHERE id=? AND status='ACTIVE'`, `rowcount==1` 반환.
- `app/engine/live_trading_engine.py`: `run_once()` 루프에 CAS 클레임 추가. 클레임 실패 시 skip (중복 주문 방지). `executed=False` + status=PROCESSING 시 ACTIVE 복구. 예외 시 ERROR 복구.
- `tests/unit/test_condition_toctou_cas.py`: 신규 생성 — 9개 테스트 (enum smoke, CAS primitive 4개, threaded race, old-path documentation, engine level 2개)

**검증 결과:**
- `python -m pytest tests/unit/test_condition_toctou_cas.py -v` → 9 passed
- `python -m pytest tests/ -q` → 626 passed
- `python scripts/check_agent_docs.py` → 0 error(s)
- `python scripts/work_schema_gate.py --items --check` → findings=0
- `python scripts/build_task_index.py --check` → OK
- `python scripts/generate_views.py --check` → OK (66 tasks / 6 views)
