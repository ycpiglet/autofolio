---
type: task
id: TASK-024
status: 완료
owner: QA
assignees: [QA, KIS API Engineer]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 20000
tags: [paper, qa, scenario-matrix, engine, risk, ui]
gate: paper-only; prod 실전 주문 전환 금지
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-007
created: 2026-06-12
created_at: 2026-06-12T12:07:12+09:00
updated_at: 2026-06-12T12:12:42+09:00
---

# TASK-024 Paper Scenario Matrix Validation

작업 ID: TASK-024
상태: 완료
Owner: QA
요청 시각: 2026-06-12T12:02:40+09:00
기록 시각: 2026-06-12T12:07:12+09:00

## 배경 및 목적

Owner 요청: "여러가지 옵션과 상황들을 생성한다음에, 그게 제대로 동작하는지 확인해줘. 명시적으로 실전 투자로 넘어가자는 말 없는한은, 계속해서 모의투자로 진행해. 테스트가 완벽하게 되면 실전으로 넘어갈거야."

목적은 실전 전환 전 paper-safe 방식으로 엔진, 리스크, DB 로그, UI backend 반영의 주요 상황을 생성하고 검증하는 것이다.

## 범위

- 포함: 격리 temporary DB + `MockBrokerClient` 기반 옵션/상황 매트릭스, KIS paper read-only 상태 확인.
- 제외: prod 실전 주문, prod 설정 변경, paper 주문 대량 반복.

## 진행 기록

### 2026-06-12T12:07:12+09:00

- `tests/integration/test_paper_scenario_matrix.py` 추가.
- 16개 시나리오를 생성/검증:
  - BUY/SELL trigger
  - not-triggered condition
  - kill switch
  - auto disabled
  - global/symbol L1 manual gate
  - whitelist rejection
  - max order amount
  - daily order amount
  - pending limit cancel
  - pending limit market fallback
  - direct market PENDING then FILLED
  - direct market still PENDING
  - repeated failures and circuit breaker
  - UI backend holdings/recent fills reflection
- 발견/수정:
  - direct MARKET 주문이 KIS처럼 `PENDING`을 반환하면 limit pending cancel 경로로 잘못 들어가는 버그를 발견.
  - `app/engine/order_flow.py`에서 `MARKET + PENDING`은 `_poll_fill()`로 보내도록 수정.
- KIS paper read-only 확인:
  - endpoint paper 확인
  - safety state `auto=false`, `kill=true`, `global_mode=L1`
  - KIS positions/today orders/account summary 조회 가능

## 완료 기록

완료 시각: 2026-06-12T12:07:12+09:00
검토자: QA + Independent Auditor (Codex self-review)
감사 로그: AUDIT-2026-06-12-007
실측 비용 (시간): 약 0.25h
실측 비용 (LLM 토큰): unknown

- 원 요청: paper 범위에서 여러 옵션/상황을 만들고 제대로 동작하는지 확인.
- 실제 작업: paper-safe scenario matrix 추가, 주문 상태 처리 버그 수정, 회귀 테스트와 KIS paper read-only 확인.
- 결과: matrix 16개 통과. 엔진/리스크/UI/KIS selector 회귀 통과. prod는 미전환.
- 최종 게이트: focused engine 31 passed, KIS selector 118 passed, UI/backend selector 37 passed, py_compile passed, upstream warning check OK, task views/schema/docs/report gates OK, git diff whitespace check OK.

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-12-002-paper-scenario-matrix.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-12-002.md`
- `tests/integration/test_paper_scenario_matrix.py`
- `app/engine/order_flow.py`

## 리뷰

- 실제 KIS paper 주문은 추가로 반복하지 않고 read-only 확인만 수행했다.
- 시나리오 실행은 isolated temporary DB를 사용해 운영 DB와 paper 계좌 상태를 오염시키지 않았다.
- `MARKET + PENDING` 수정은 KIS broker behavior와 맞추는 좁은 주문 상태 처리 변경이다.

## Independent Audit

판정: pass
근거: scenario matrix, focused engine tests, KIS selector, UI/backend selector, py_compile, and KIS paper read-only checks all passed. Prod trading remained untouched.
