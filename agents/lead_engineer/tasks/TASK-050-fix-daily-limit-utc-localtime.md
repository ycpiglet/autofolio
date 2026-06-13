---
type: task
id: TASK-050
status: 대기
owner: Backend Engineer
assignees: [Backend Engineer, QA]
priority: High
difficulty: 중
est_hours: 3
est_tokens: 25000
tags: [bug, safety, daily-limit, utc, localtime, database]
gate: safety bug — no live orders during fix
trigger_meeting: 즉시 처리 권고
audit_log: AUDIT-2026-06-13-007
created: 2026-06-13
created_at: 2026-06-13T01:33:29+09:00
updated_at: 2026-06-13T01:33:29+09:00
---

# TASK-050 fix: 일일 주문한도 UTC/KST 불일치 버그

작업 ID: TASK-050
상태: 대기
Owner: Backend Engineer
요청 시각: 2026-06-13
기록 시각: 2026-06-13T01:33:29+09:00
요청자: Owner
수행자: Lead Engineer
의도: KST 새벽 시간대(00:00~08:59) 일일 주문한도 미적용 UTC/KST 불일치 버그 수정
대상: app/database/repositories.py ~line 288 today_order_amount(), tests/integration/test_paper_scenario_matrix.py
방법: created_at 저장을 KST datetime으로 통일하거나 비교 기준을 UTC로 일원화하여 날짜 불일치 해소
감사 로그: AUDIT-2026-06-13-007

## ⚠ 안전 버그 (High Priority)

**증상**: KST 00:00~08:59 사이(UTC 전일)에 주문한 당일 주문금액이 일일 한도 집계에 미적용됨. 이 시간대에 일일 주문한도가 우회될 수 있다.

## 버그 내용

`Repository.today_order_amount()` (`app/database/repositories.py` ~line 288)가 다음과 같이 구현됨:

```sql
SELECT COALESCE(SUM(COALESCE(order_price, current_price, 0) * quantity), 0) AS amount
FROM order_logs
WHERE DATE(created_at) = DATE('now', 'localtime')
  AND order_status IN ('REQUESTED', 'FILLED', 'PENDING')
```

**문제**: `created_at`은 SQLite `CURRENT_TIMESTAMP`로 저장되며 **UTC** 기준. 반면 비교 대상 `DATE('now', 'localtime')`는 **로컬 시간(KST)** 기준.

KST 00:00~08:59 (UTC 전일 15:00~23:59)에 주문하면:
- `created_at`의 DATE: UTC 전날 날짜
- `DATE('now', 'localtime')`: 오늘(KST) 날짜
- 결과: WHERE 조건 불일치 → 해당 주문이 today_order_amount에 미집계

## 재현

`tests/integration/test_paper_scenario_matrix.py::test_daily_order_amount_limit_blocks_new_order`가 KST 00:00~08:59에 실행되면 실패한다.

## 수정 방향

둘 중 하나로 통일:

**옵션 A** (권장): `created_at`을 KST로 저장 (`CURRENT_TIMESTAMP`를 KST `datetime.now(KST).isoformat()`으로 교체) → `DATE('now', 'localtime')` 비교 정합

**옵션 B**: 비교를 UTC로 통일 → `DATE(created_at) = DATE('now')` (하지만 표시용 날짜가 KST가 아닌 UTC로 표시될 수 있음)

`app/database/repositories.py`의 `today_order_amount()` 및 관련 날짜 쿼리 전수 점검 권장.

## 완료 기준

- 수정 후 `test_daily_order_amount_limit_blocks_new_order` KST 00:00~08:59 시뮬레이션 통과
- `python -m pytest tests/ -q` green
- `python scripts/check_agent_docs.py` 0 error

## 근거 경로

- `app/database/repositories.py` ~line 288: `today_order_amount()`
- `tests/integration/test_paper_scenario_matrix.py::test_daily_order_amount_limit_blocks_new_order`

## Done When

- `today_order_amount()` KST/UTC 불일치 수정
- 재현 테스트 KST 야간 시간대 시뮬레이션 통과
- 전체 pytest green

## v1 이행 (파일럿)

이 태스크는 agent_runtime v0.2.0 work-item 스키마로 이행되었다.
실행 상세 명세는 v1 unit 스펙을 참고:

- Initiative: `agents/project/initiatives/INIT-AUTOFOLIO-SAFETY-FIXES.md`
- Taskset: `agents/project/initiatives/TASKSET-AUTOFOLIO-SAFETY-FIXES.md`
- Unit spec: `agents/lead_engineer/tasks/units/TASK-050/UNIT-TASK-050-001.md`
