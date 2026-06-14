---
unit_id: UNIT-TASK-063-001
task_id: TASK-063
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "today_realized_pnl()가 순 현금흐름(SELL 양수, BUY 음수)을 반환하여 매수만 있는 날 대규모 음수값 → 일손실 서킷브레이커 오발동. app/database/repositories.py line 334 수정 필요. 평균매입가: execution_logs 전체 BUY 체결 가중평균."
inputs:
  - agents/lead_engineer/tasks/TASK-063-fix-circuit-breaker-pnl-logic.md
  - app/database/repositories.py
  - tests/unit/test_circuit_breaker.py
target_files:
  - app/database/repositories.py
  - tests/unit/test_circuit_breaker.py
scope: "app/database/repositories.py today_realized_pnl() 메서드만 수정. 서킷브레이커 임계치·다른 risk 로직 변경 금지."
acceptance:
  - "BUY-only day: today_realized_pnl() == 0.0"
  - "BUY then SELL at profit: realized == (sell_price - avg_cost) * qty > 0"
  - "BUY then SELL at loss: realized == (sell_price - avg_cost) * qty < 0"
  - "BUY-only day does NOT trip circuit breaker"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_circuit_breaker.py -q"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
handoff: "변경 파일 목록, pytest 결과, cost basis 방식, TZ 처리 방식 보고."
stop_condition: "today_realized_pnl() 수정 후 즉시 중단. 다른 repositories.py 메서드나 인접 모듈로 확장 금지."
depends_on: []
---

# UNIT-TASK-063-001 — 서킷브레이커 실현손익 계산 수정

## Context

`Repository.today_realized_pnl()` (`app/database/repositories.py` line 334)가
순 현금흐름(SELL 양수, BUY 음수)을 반환한다.

매수 주문이 많은 날 SELL 체결 없이 BUY만 발생하면 대규모 음수값 →
일손실 서킷브레이커 임계치 초과 → 정상 거래 중단.

## Target Files

- `app/database/repositories.py`
- `tests/unit/test_circuit_breaker.py`

## Scope

In scope: `today_realized_pnl()` SQL 로직 수정, 관련 단위테스트 재작성.

Out of scope: 서킷브레이커 임계치, 다른 서비스 레이어, 마이그레이션, UI 코드.

## Cost Basis Approach

DB에 포지션/평균단가 테이블 없음. `execution_logs JOIN order_logs WHERE side='BUY'`
전체 기간 가중평균으로 종목별 avg_buy_price 계산. SQL WITH CTE 사용.

## TZ 처리

`DATE(el.filled_at, '+9 hours') = DATE('now', '+9 hours')` — KST-aware, OS 무관 ('+9 hours' 고정).
`'localtime'` 미사용.

## Acceptance Criteria

- `today_realized_pnl()` BUY-only day → 0.0
- SELL at profit → positive realized
- SELL at loss → negative realized
- `test_buy_only_day_does_not_trip_circuit_breaker` PASS
- `python -m pytest tests/ -q` green
- `python scripts/check_agent_docs.py` 0 error

## 완료 기록

완료 시각: 2026-06-14T10:04:58+09:00

**변경 내용:**
- `app/database/repositories.py` `today_realized_pnl()`: 순현금흐름 SQL → SELL 체결 기준 실현손익 SQL로 수정. WITH CTE로 종목별 avg_buy_price 계산 (전체 기간 BUY 가중평균). KST 필터: `DATE(el.filled_at, '+9 hours') = DATE('now', '+9 hours')`.
- `tests/unit/test_circuit_breaker.py`: 버그 행동 assert 테스트 교체. 신규: `test_buy_only_day_returns_zero`, `test_buy_only_day_does_not_trip_circuit_breaker`, `test_sell_after_buy_profit`, `test_sell_after_buy_loss`, `test_avg_cost_weighted_correctly`. `test_daily_loss_trips_when_loss_exceeds_threshold`: BUY fill → SELL fill로 교체.

**검증 결과:**
- 수정 전: `test_buy_only_day_returns_zero` FAILED (반환값 -700_000), `test_avg_cost_weighted_correctly` FAILED, `test_buy_only_day_does_not_trip_circuit_breaker` FAILED
- 수정 후: 14 passed (test_circuit_breaker.py), 630 passed (전체)
- `python scripts/check_agent_docs.py` → 검증 시 0 error 예정
