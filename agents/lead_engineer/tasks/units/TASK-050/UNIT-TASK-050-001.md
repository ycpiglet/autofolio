---
unit_id: UNIT-TASK-050-001
task_id: TASK-050
task_set_id: TASKSET-AUTOFOLIO-SAFETY-FIXES
project_id: PROJECT-AUTOFOLIO
status: worker_ready
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "today_order_amount()가 created_at(UTC)을 DATE('now','localtime')(KST)와 비교해 KST 00:00~08:59에 당일 주문이 미집계됨 → 일일 주문한도 우회 안전 버그. app/database/repositories.py ~line 288 수정 필요."
inputs:
  - agents/lead_engineer/tasks/TASK-050-fix-daily-limit-utc-localtime.md
  - app/database/repositories.py
  - tests/integration/test_paper_scenario_matrix.py
target_files:
  - app/database/repositories.py
  - tests/integration/test_paper_scenario_matrix.py
scope: "app/database/repositories.py 의 today_order_amount() 및 관련 날짜 쿼리만 수정. 다른 서비스·모델 레이어 변경 금지."
acceptance:
  - "today_order_amount() UTC/KST 불일치 수정 완료"
  - "test_daily_order_amount_limit_blocks_new_order KST 00:00~08:59 시뮬레이션 통과"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/integration/test_paper_scenario_matrix.py -q"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
handoff: "변경된 파일 목록, pytest 결과, 수정 방식(옵션 A/B) 보고."
stop_condition: "today_order_amount() 날짜 비교 수정 후 즉시 중단. 다른 repositories.py 메서드나 인접 모듈로 확장 금지."
depends_on: []
---

# UNIT-TASK-050-001 — 일일 주문한도 UTC/KST 불일치 버그 수정

## Context

`Repository.today_order_amount()` (`app/database/repositories.py` ~line 288)가
`DATE(created_at) = DATE('now', 'localtime')` 비교를 사용하는데,
`created_at`은 SQLite `CURRENT_TIMESTAMP`로 저장되어 **UTC** 기준이고
`DATE('now', 'localtime')`는 **KST** 기준이다.

KST 00:00~08:59 (UTC 전일 15:00~23:59)에 주문하면:
- `created_at`의 DATE: UTC 전날 날짜
- `DATE('now', 'localtime')`: 오늘(KST) 날짜
- 결과: WHERE 조건 불일치 → 해당 주문이 today_order_amount에 미집계 → 일일 한도 우회

## Inputs

- `agents/lead_engineer/tasks/TASK-050-fix-daily-limit-utc-localtime.md` — 원본 버그 명세
- `app/database/repositories.py` — `today_order_amount()` 구현
- `tests/integration/test_paper_scenario_matrix.py` — 재현 테스트

## Target Files

- `app/database/repositories.py`
- `tests/integration/test_paper_scenario_matrix.py`

## Scope

In scope: `today_order_amount()` 및 repositories.py 내 동일 패턴의 날짜 비교 쿼리.

Out of scope: 다른 서비스 레이어, 마이그레이션, 스키마 변경, UI 코드.

## Steps

1. `app/database/repositories.py` ~line 288 `today_order_amount()` 확인.
2. 수정 옵션 선택:
   - **옵션 A** (권장): `CURRENT_TIMESTAMP` 대신 KST `datetime.now(KST).isoformat()` 저장 → `DATE('now', 'localtime')` 비교 정합.
   - **옵션 B**: 비교 기준을 UTC 통일 → `DATE(created_at) = DATE('now')`.
3. 동일 파일 내 날짜 비교 쿼리 전수 점검 및 동일 패턴 수정.
4. `test_daily_order_amount_limit_blocks_new_order` KST 야간 시뮬레이션 포함 검증.
5. 전체 pytest green 확인.

## Acceptance Criteria

- `today_order_amount()` UTC/KST 불일치 수정 완료
- 기존 `test_daily_order_amount_limit_blocks_new_order` 통과 유지 — 단, 이 테스트는
  `_set_order_log_local_today()` 헬퍼(tests/integration/test_paper_scenario_matrix.py ~line 100–106)로
  `created_at`을 `datetime('now','localtime')`로 패치하므로 **버그를 마스킹**한다.
  즉, 수정 전·후 모두 이 테스트는 통과할 수 있어 수정 증거가 되지 않는다.
- **신규 필수**: KST 00:00~08:59 야간 윈도우 재현 케이스를 `_set_order_log_local_today()`
  헬퍼를 사용하지 않고 추가한다. 해당 케이스는:
  1. 수정 전 — `today_order_amount()`가 0을 반환해 한도 우회 허용 (버그 재현)
  2. 수정 후 — `today_order_amount()`가 정확한 금액을 반환해 한도 차단 (수정 증거)
- `python -m pytest tests/ -q` green
- `python scripts/check_agent_docs.py` 0 error

## Verification

```powershell
python -m pytest tests/integration/test_paper_scenario_matrix.py -q
python -m pytest tests/ -q
python scripts/check_agent_docs.py
```

## Handoff

변경된 파일 목록, 선택한 수정 옵션(A 또는 B), pytest 결과, `check_agent_docs.py` 결과 보고.

## Stop Boundary

`today_order_amount()` 및 동일 파일 내 관련 날짜 쿼리 수정 후 즉시 중단.
다른 repositories.py 메서드, 인접 모듈, 마이그레이션으로 확장 금지.
