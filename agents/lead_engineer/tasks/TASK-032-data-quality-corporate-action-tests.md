---
type: task
id: TASK-032
status: 보류
owner: Data Engineer
assignees: [Data Engineer, QA]
priority: Medium
difficulty: 중
est_hours: 5
est_tokens: 45000
tags: [qa, data-quality, corporate-actions, holiday, stale-data]
gate: no live orders; risk integration requires review
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-13-002
created: 2026-06-12
created_at: 2026-06-12T12:27:28+09:00
updated_at: 2026-06-13T00:14:24+09:00
---

# TASK-032 Data Quality and Corporate Action Tests

작업 ID: TASK-032
상태: 보류
Owner: Data Engineer
기록 시각: 2026-06-12T12:27:28+09:00

## 배경

카탈로그의 stale price, zero/negative/NaN price, missing bar, holiday, split/dividend/corporate action 케이스는 아직 실행 불가능하다.

## 왜 아직 실행 못하는가

- 데이터 freshness/quality contract가 엔진 입력으로 명시되어 있지 않다.
- corporate action adjustment와 holiday calendar가 표준화되어 있지 않다.

## 진행 기록

### 2026-06-12T23:32:49+09:00

- 추가:
  - `app/data/quality.py`
    - `validate_price_quote()`로 zero/negative/NaN/stale/future quote를 판정.
    - `validate_ohlcv_bars()`로 missing business bar, holiday calendar, invalid OHLCV range를 판정.
    - `CorporateAction`, `validate_corporate_actions()`, `apply_split_adjustment()`로 split/dividend mock fixture contract를 추가.
  - `PriceQuote.as_of`/`PriceQuote.source` optional metadata.
  - `tests/unit/test_data_quality.py` data-quality/corporate-action fixture tests.
- 검증:
  - `python -m py_compile app/brokers/base.py app/data/quality.py tests/unit/test_data_quality.py` -> OK.
  - `pytest tests/unit/test_data_quality.py` -> 10 passed.
  - `pytest tests/unit/test_data_quality.py tests/unit/test_quant_data_loader.py -q` -> 19 passed.
- 남은 항목:
  - engine no-order behavior는 아직 미완료. `app/engine/order_flow.py` 변경은 Autofolio R3 surface라 무승인 production hook을 남기지 않았다.
  - 다음 단계는 Owner/Lead review 하에 invalid market data가 주문 제출 전에 skip되는 경로를 `OrderFlow` 또는 `LiveTradingEngine`에 연결하고, 해당 no-order regression을 추가하는 것이다.

### 2026-06-13T00:14:24+09:00

- 상태 변경: `진행 중` -> `보류`.
- 이유:
  - non-R3 범위인 validator/fixture contract는 구현 및 검증 완료.
  - 남은 Done When인 no-order behavior 고정은 주문 제출 전 차단 경로에 연결해야 하며, `app/engine/order_flow.py` 또는 동등한 order/safety 경로 변경이 필요하다.
  - 해당 경로는 AGENTS.md Autofolio R3 surface라 Owner 명시 승인 없이 production hook을 추가하지 않는다.
- 재개 조건:
  - Owner가 invalid market data no-order integration의 변경 위치(`OrderFlow` 또는 `LiveTradingEngine`)와 허용 범위를 승인한다.
  - 승인 후 no-order regression을 추가하고 data-quality validator를 주문 제출 전 경로에 연결한다.

## Done When

- data quality validator가 stale/missing/invalid price를 차단하거나 명시적으로 fallback한다.
- holiday/missing-bar/corporate-action mock fixtures가 추가된다.
- no-order behavior가 테스트로 고정된다.

## Verification

- `pytest tests/unit/test_data_quality.py tests/unit/test_quant_data_loader.py -q` -> 19 passed.
- `python -m py_compile app/brokers/base.py app/data/quality.py tests/unit/test_data_quality.py` -> OK.
- engine no-order tests for invalid market data -> 보류, R3 Owner approval required.
