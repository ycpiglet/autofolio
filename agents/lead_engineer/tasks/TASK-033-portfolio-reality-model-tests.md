---
type: task
id: TASK-033
status: 대기
owner: Performance Analyst
assignees: [Performance Analyst, Backend Engineer, QA]
priority: Medium
difficulty: 중
est_hours: 5
est_tokens: 45000
tags: [qa, portfolio, cash, fees, slippage, concentration]
gate: no live orders; broker/risk integration requires review
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-009
created: 2026-06-12
created_at: 2026-06-12T12:27:28+09:00
updated_at: 2026-06-12T12:27:28+09:00
---

# TASK-033 Portfolio Reality Model Tests

작업 ID: TASK-033
상태: 대기
Owner: Performance Analyst
기록 시각: 2026-06-12T12:27:28+09:00

## 배경

카탈로그의 cash shortage, fees, slippage, concentration, tax placeholder 케이스는 현재 포트폴리오/브로커 모델에서 완전하게 실행되지 않는다.

## 왜 아직 실행 못하는가

- MockBroker는 현금 잔고, 수수료, 세금, 슬리피지, 매수가능금액 차감을 모델링하지 않는다.
- concentration/risk budget이 엔진 주문 차단 기준으로 연결되어 있지 않다.

## Done When

- mock portfolio ledger가 cash/fee/slippage를 계산한다.
- cash shortage와 concentration rejection tests가 추가된다.
- UI KPI/portfolio view와 execution log가 같은 값을 보여준다.

## Verification

- portfolio reality unit/integration tests
- UI backend KPI regression
