---
type: task
id: TASK-033
status: 완료
owner: Performance Analyst
assignees: [Performance Analyst, Backend Engineer, QA]
priority: Medium
difficulty: 중
est_hours: 5
est_tokens: 45000
tags: [qa, portfolio, cash, fees, slippage, concentration]
gate: no live orders; broker/risk integration requires review
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-014
created: 2026-06-12
created_at: 2026-06-12T12:27:28+09:00
updated_at: 2026-06-12T23:44:23+09:00
---

# TASK-033 Portfolio Reality Model Tests

작업 ID: TASK-033
상태: 완료
Owner: Performance Analyst
기록 시각: 2026-06-12T12:27:28+09:00

## 배경

카탈로그의 cash shortage, fees, slippage, concentration, tax placeholder 케이스는 현재 포트폴리오/브로커 모델에서 완전하게 실행되지 않는다.

## 왜 아직 실행 못하는가

- MockBroker는 현금 잔고, 수수료, 세금, 슬리피지, 매수가능금액 차감을 모델링하지 않는다.
- concentration/risk budget이 엔진 주문 차단 기준으로 연결되어 있지 않다.

## 완료 기록

완료 시각: 2026-06-12T23:44:23+09:00
검토자: Performance Analyst + Backend Engineer + QA (Codex self-review)
감사 로그: AUDIT-2026-06-12-014
실측 비용 (시간): 약 0.4h
실측 비용 (LLM 토큰): unknown

- 원 요청: cash shortage, fees, slippage, concentration, tax placeholder 등 portfolio reality model gap을 mock/paper-safe 테스트로 실행 가능하게 만든다.
- 실제 작업:
  - `MockBrokerClient`에 optional cash ledger, fee, slippage, concentration rejection을 추가했다. 기본값은 기존 legacy fill 동작을 유지한다.
  - `Repository.list_order_logs()`가 read-only join으로 execution 평균체결가/체결수량/체결시각을 같이 반환하게 했다.
  - `backend.recent_fills()`가 MARKET 주문의 `order_price=None` 대신 execution log의 `filled_price`/`filled_quantity`를 우선 표시하도록 정렬했다.
  - cash shortage, concentration rejection, fee/slippage cash accounting, UI KPI/recent fills consistency regression을 추가했다.
- 결과:
  - mock portfolio ledger가 cash/fee/slippage를 계산하고, cash shortage/concentration overweight를 no-execution failure로 고정했다.
  - UI recent fills와 KPI cash/holdings 합계가 execution log와 같은 체결가/수량을 사용한다.
  - live KIS, prod 주문, `app/risk/**`, DB schema/migration은 변경하지 않았다.
- 남은 이슈:
  - tax placeholder는 별도 세무 정책/브로커 수수료표가 필요해 이번 TASK에서는 placeholder gap으로 남긴다.
  - real broker buying-power/risk-budget enforcement는 R3 surface라 Owner review 후 별도 TASK로 진행한다.

## Done When

- mock portfolio ledger가 cash/fee/slippage를 계산한다.
- cash shortage와 concentration rejection tests가 추가된다.
- UI KPI/portfolio view와 execution log가 같은 값을 보여준다.

## Verification

- `pytest tests/unit/test_mock_portfolio_ledger.py tests/integration/test_portfolio_reality_model.py -q` -> 9 passed.
- `pytest tests/unit/test_backend_kpis.py tests/unit/test_backend_holdings.py tests/integration/test_paper_scenario_matrix.py::test_ui_backend_reflects_filled_scenario -q` -> 19 passed.
- `pytest tests/integration/test_quant_trading_scenario_catalog.py tests/integration/test_paper_scenario_matrix.py -q` -> 119 passed.
- `pytest tests/unit/test_engine_market_fallback.py tests/integration/test_mock_order_flow.py -q` -> 7 passed.
- `python -m py_compile app/brokers/mock/mock_client.py app/database/repositories.py app/ui/backend.py tests/unit/test_mock_portfolio_ledger.py tests/integration/test_portfolio_reality_model.py` -> OK.
