---
type: task
id: TASK-063
status: 대기
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
상태: 대기
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
