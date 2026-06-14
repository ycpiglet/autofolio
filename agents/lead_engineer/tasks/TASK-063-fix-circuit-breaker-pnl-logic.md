---
type: task
id: TASK-063
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, QA]
priority: High
difficulty: 중
est_hours: 4
est_tokens: 30000
tags: [bug, safety, circuit-breaker, pnl]
gate: safety bug — no live orders during fix
trigger_meeting: 즉시 처리 권고
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T00:00:00+09:00
---

# TASK-063 fix: 서킷브레이커 일손실 기준 로직 오류 (safety_checker.py)

작업 ID: TASK-063
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: Backend Engineer
의도: today_realized_pnl() 계산을 순현금흐름에서 실현손익 기준으로 수정
대상: app/trading/safety_checker.py today_realized_pnl(), app/database/repositories.py
방법: SELL 체결 기준 실현손익 계산 로직 재구현 + 순매수 일 미발동 단위테스트 + 실현 손실 초과 발동 검증
감사 로그: AUDIT-2026-06-14-001

## ⚠ 안전 버그 (High Priority)

**증상**: 순매수 포지션(매수만 많은 날)에 일손실 서킷브레이커가 오발동하여 정상 거래 중단.

## 버그 내용

`today_realized_pnl()`이 순 현금흐름(SELL 양수, BUY 음수)을 반환함.

**문제**: 매수 주문이 많은 날 SELL 체결 없이 BUY만 발생하면 대규모 음수값 → 일손실 서킷브레이커 임계치 초과 → 오발동.

**올바른 계산**: 실현 손익 = 매도 수익 - 매칭 매수 원가 (FIFO 또는 평균단가 기준).

## 수정 방향

1. `today_realized_pnl()` 계산 로직 수정:
   - SELL 체결 기준으로만 실현 손익 계산
   - 매칭 매수 원가 = 해당 종목 평균매입가 × 매도수량
   - 실현 손익 = (체결가 - 평균매입가) × 매도수량
2. 매수만 있는 날 → 실현 손익 = 0 (서킷브레이커 미발동)
3. 단위테스트: 순매수 일 미발동, 실현 손실 초과 시 발동

## 완료 기준

- 순매수 일에 서킷브레이커 미발동
- 실현 손실 기준 정상 발동
- 단위테스트 통과

## Done When

- 순매수 일에 서킷브레이커 미발동
- 실현 손실 기준 발동
- 단위테스트 통과

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`

## 완료 기록

완료 시각: 2026-06-14T10:06:23+09:00
검토자: Backend Engineer / QA

## 증거

- `app/database/repositories.py` `today_realized_pnl()`: 순현금흐름 SQL → SELL 체결 기준 실현손익 SQL로 수정.
  - WITH CTE로 종목별 avg_buy_price 계산 (전체 기간 BUY 가중평균).
  - KST 필터: `DATE(el.filled_at, '+9 hours') = DATE('now', '+9 hours')` — OS TZ 무관.
- `tests/unit/test_circuit_breaker.py`: 버그 행동을 assert하던 테스트 교체.
  - 신규: `test_buy_only_day_returns_zero` (버그 재현 → 수정 증거).
  - 신규: `test_buy_only_day_does_not_trip_circuit_breaker` (서킷브레이커 오발동 재현 → 수정 증거).
  - `test_sell_after_buy_profit`, `test_sell_after_buy_loss`, `test_avg_cost_weighted_correctly` 추가.
  - `test_daily_loss_trips_when_loss_exceeds_threshold`: BUY fill → SELL fill로 교체.
- 수정 전: `test_buy_only_day_returns_zero` FAILED (반환값 -700_000).
- 수정 후: 14 passed (test_circuit_breaker.py), 630 passed (전체).

## 리뷰

- 평균단가 근거: execution_logs 전체 BUY 기록 가중평균 (positions 테이블 없음).
- 안전 폴백: 매입 기록 없는 종목 SELL → avg_price = sell_price → realized = 0 (오발동 방지).
- TZ: `'+9 hours'` 고정, `'localtime'` 미사용.
