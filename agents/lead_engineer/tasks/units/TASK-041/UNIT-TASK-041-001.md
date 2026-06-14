---
unit_id: UNIT-TASK-041-001
task_id: TASK-041
task_set_id: TASKSET-RESEARCH-REPORTING
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "브로커/플랫폼 capability parity matrix 작성. KIS/mock/paper/current Autofolio vs reference platforms 비교. ASSET-UNIVERSE-DECISION-RECORD + EXTERNAL-APP-API-DECISION-RECORD 흡수. R3 태스크 매핑. UI 노출 규칙 정의."
inputs:
  - agents/lead_engineer/tasks/TASK-041-broker-capability-feature-parity-matrix.md
  - agents/qa/test_cases/ASSET-UNIVERSE-DECISION-RECORD.md
  - agents/qa/test_cases/EXTERNAL-APP-API-DECISION-RECORD.md
  - agents/qa/test_cases/FEATURE-LANDSCAPE-CATALOG.md
  - app/brokers/base.py
  - app/brokers/kis/kis_client.py
  - app/brokers/mock/mock_client.py
  - app/common/enums.py
  - app/risk/safety_checker.py
  - app/risk/trading_window.py
target_files:
  - docs/BROKER-CAPABILITY-PARITY-MATRIX.md
  - tests/integration/test_capability_matrix.py
  - agents/lead_engineer/tasks/TASK-041-broker-capability-feature-parity-matrix.md
  - agents/lead_engineer/tasks/INDEX.md
scope: "docs/BROKER-CAPABILITY-PARITY-MATRIX.md 작성 + 테스트. 제품 코드 변경 없음. 주문 경로, risk policy, schema migration, secret 변경 없음."
acceptance:
  - "docs/BROKER-CAPABILITY-PARITY-MATRIX.md 존재"
  - "13개 섹션 모두 포함 (Asset Class, Session, Order Type, Lifecycle, Fee/Fill, Data, Alert, Connector, Margin, Microstructure, Reference, UI Rules, Task Cross-Ref)"
  - "status legend에 SUPPORTED/MOCK-ONLY/PAPER-ONLY/CONDITIONAL/R3-HOLD/REJECTED/NOT-IMPL 정의"
  - "레버리지/인버스 ETP REJECTED 표시"
  - "R3-HOLD 태스크 (014/021/022/028/030/031/032) 참조"
  - "test_capability_matrix.py 전체 PASS"
  - "pytest tests/ -q green"
  - "check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/integration/test_capability_matrix.py -q"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
  - "python scripts/generate_views.py --check"
  - "python scripts/build_task_index.py --check"
handoff: "매트릭스 경로, 섹션 수, pytest 결과, gate 결과 보고."
stop_condition: "doc + test 작성 후 즉시 중단. 제품 코드, 브로커 구현, risk policy 변경 금지."
depends_on: []
---

# UNIT-TASK-041-001 — Broker Capability Parity Matrix

## Context

TASK-041 scope: KIS/mock/paper/current Autofolio와 참조 플랫폼 기능군을 비교하는
capability matrix 작성. `ASSET-UNIVERSE-DECISION-RECORD`의 승인/조건부/보류/R3/기각
상태와 `EXTERNAL-APP-API-DECISION-RECORD`의 커넥터 권한 클래스를 흡수.
UI·전략 코드가 지원되지 않는 기능을 노출하지 않도록 명시적 status label 정의.

## Target Files

- `docs/BROKER-CAPABILITY-PARITY-MATRIX.md` — 주요 산출물
- `tests/integration/test_capability_matrix.py` — 구조 gate 테스트

## Scope

In scope: capability matrix doc 작성, 가벼운 구조 테스트.

Out of scope: 브로커 구현, `place_order`, `cancel_order`, `OrderFlow`, `app/risk/**` 변경,
secret, 계정, prod 데이터 접근.

## Steps

1. `ASSET-UNIVERSE-DECISION-RECORD` 자산군 상태 흡수 → 섹션 1 (Asset Class Capability).
2. KIS 세션/TR ID, `trading_window.py` 분석 → 섹션 2 (Trading Session).
3. `OrderType` enum, KIS `ORD_DVSN` 상수 → 섹션 3 (Order Type).
4. `OrderStatus` enum, `order_flow.py` 흐름 → 섹션 4 (Order Lifecycle).
5. `mock_client.py` fee/slippage 파라미터 → 섹션 5 (Fee / Slippage / Fill Model).
6. KIS TR ID 목록 → 섹션 6 (Data Source).
7. `alerts.py`, Notifier, TASK-038/039/040 → 섹션 7 (Alert / Backtest Feature Flags).
8. `EXTERNAL-APP-API-DECISION-RECORD` 권한 클래스 → 섹션 8 (External Connector).
9. TASK-021/022 R3 → 섹션 9 (Margin / Short).
10. `kis_client.py` 틱사이즈, `SafetyChecker` → 섹션 10 (Market Microstructure).
11. 참조 플랫폼 비교 → 섹션 11 (Reference Platform Comparison).
12. UI 노출 규칙 요약 → 섹션 12 (UI Exposure Rules).
13. TASK 교차 참조 표 → 섹션 13 (Task Cross-Reference).
14. `tests/integration/test_capability_matrix.py` 작성 및 green 확인.

## Acceptance Criteria

- `docs/BROKER-CAPABILITY-PARITY-MATRIX.md` 존재
- 13개 필수 섹션 포함
- status legend에 7개 레이블(SUPPORTED/MOCK-ONLY/PAPER-ONLY/CONDITIONAL/R3-HOLD/REJECTED/NOT-IMPL) 정의
- 레버리지/인버스 ETP → REJECTED 표시, SUPPORTED 아님
- R3-HOLD 태스크 014/021/022/028/030/031/032 모두 참조
- `pytest tests/integration/test_capability_matrix.py -q` PASS
- `pytest tests/ -q` green (기존 테스트 모두 통과)
- `check_agent_docs.py` 0 error

## Verification

```
python -m pytest tests/integration/test_capability_matrix.py -q
python -m pytest tests/ -q
python scripts/check_agent_docs.py
python scripts/generate_views.py --check
python scripts/build_task_index.py --check
```

## Handoff

변경 파일 목록, pytest 결과, gate 결과 보고.
TASK-041 stub 완료 기록 작성.

## Stop Boundary

doc + test 작성 후 즉시 중단. 제품 코드, 브로커 구현, risk policy, schema migration 변경 금지.

## 완료 기록

완료 시각: 2026-06-14T17:28:16+09:00

**변경 내용:**
- `docs/BROKER-CAPABILITY-PARITY-MATRIX.md`: 13개 섹션 capability matrix 작성.
  - 자산군 19개 (승인/조건부/R3/기각 상태 포함)
  - 거래 세션 7개 (정규장 SUPPORTED; 시간외/해외 R3-HOLD)
  - 주문 유형 11개 (limit/market SUPPORTED; 나머지 R3-HOLD)
  - 주문 생명주기 11개 상태
  - fee/slippage 모델 (mock 파라미터 기반)
  - 데이터 소스 14개 KIS TR ID 매핑
  - 알림/백테스트 feature flags 15개
  - 외부 커넥터 권한 클래스 12개 + 앱별 상태 10개
  - TASK 교차 참조 14개
- `tests/integration/test_capability_matrix.py`: 구조 gate 테스트 (10개 test).

**검증 결과:** (run 후 기재)
