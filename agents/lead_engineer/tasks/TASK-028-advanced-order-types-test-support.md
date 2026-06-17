---
type: task
id: TASK-028
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, KIS API Engineer, QA]
priority: Medium
difficulty: 상
est_hours: 8
est_tokens: 70000
tags: [qa, order-types, stop, trailing, ioc, fok, moo, moc]
gate: Owner approval received 2026-06-17; prod order execution remains hardguarded
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-009
created: 2026-06-12
created_at: 2026-06-12T12:27:28+09:00
updated_at: 2026-06-17T09:03:57+09:00
---

# TASK-028 Advanced Order Types Test Support

작업 ID: TASK-028
상태: 완료
Owner: Backend Engineer
기록 시각: 2026-06-12T12:27:28+09:00

## 배경

카탈로그의 stop, stop-limit, trailing stop, market-on-open, market-on-close, IOC, FOK 케이스는 현재 실행 불가능하다. 현재 enum은 `LIMIT`와 `MARKET`만 가진다.

## 왜 아직 실행 못하는가

- `OrderType`/DB schema/order_flow/broker adapter가 고급 주문 유형을 표현하지 못한다.
- KIS/KRX 세션별 허용 주문유형과 취소/정정 정책이 반영되어야 한다.

## Done When

- 주문 유형별 state machine과 risk policy가 정의된다.
- mock tests가 각 order type trigger/cancel/reject path를 검증한다.
- KIS paper smoke는 별도 승인된 최소 주문으로만 실행한다.

## Verification

- advanced order type unit/integration tests
- generated scenario catalog rows promoted from catalog-only to executable

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-R3-ORDER-SURFACE.md`
- Taskset: `agents/project/initiatives/TASKSET-R3-ORDER-SURFACE.md`

## 완료 기록 (2026-06-17T09:03:57+09:00)

Owner가 "TASK-069 제외하고 모두 승인"을 명시해 R3 gate가 해제된 범위에서 구현했다.

구현 요약:
- `app/risk/order_policy.py`를 추가해 상품군, 주문유형, 거래정지/VI/공시 차단, stale quote, L3 요구조건, mock/paper/prod hardguard를 표준화했다.
- `OrderRequest`/`Position` 메타데이터를 확장하고 `OrderFlow`/`SafetyChecker`가 quote와 order_session/product_type/sell_type/market/currency를 검증하도록 연결했다.
- KIS domestic order path는 시간외 ORD_DVSN, SLL_TYPE, 고급 주문 유형 payload를 paper/mock 우선으로 지원하고 prod R3 surface는 명시 override 없이는 차단한다.
- KIS 해외주식 주문 payload builder와 paper TR 매핑을 추가하고 prod hardguard를 둔다.
- mock broker advanced order semantics, derivatives contract/margin validator, mock-only basket executor, 해외 포지션 KRW 평가를 추가했다.

검증:
- `python -m py_compile app/common/enums.py app/brokers/base.py app/risk/trading_window.py app/risk/order_policy.py app/risk/safety_checker.py app/engine/order_flow.py app/brokers/mock/mock_client.py app/brokers/kis/kis_client.py app/engine/basket_execution.py app/risk/derivatives.py tests/unit/test_r3_order_policy.py tests/unit/test_kis_r3_order_paths.py tests/integration/test_r3_basket_and_derivatives.py` -> OK.
- `pytest tests/unit/test_r3_order_policy.py tests/unit/test_kis_r3_order_paths.py tests/integration/test_r3_basket_and_derivatives.py -q` -> 15 passed.
- `pytest tests/integration/test_quant_trading_scenario_catalog.py -q` -> 103 passed.
- `pytest tests/unit/test_kis_client.py tests/unit/test_kis_failure_modes.py tests/unit/test_kis_client_failure_modes.py tests/unit/test_safety_checker.py tests/unit/test_safety_critical_boundaries.py tests/unit/test_engine_market_fallback.py tests/unit/test_order_flow_and_notification_failures.py tests/integration/test_paper_scenario_matrix.py -q` -> 94 passed, 1 warning.
- `pytest tests/unit/test_backend_holdings.py tests/api/test_portfolio.py -q` -> 21 passed, 1 warning.

남은 주의:
- 실전(prod) 주문 활성화가 아니다. R3 표면은 prod hardguard로 차단되어 있으며, 실제 계좌 주문은 별도 사람 승인/정규장 smoke/브로커 확인이 필요하다.