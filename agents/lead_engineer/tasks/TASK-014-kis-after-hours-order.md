---
type: task
id: TASK-014
status: 완료
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Medium
difficulty: 중
est_hours: 3
est_tokens: 50000
tags: [kis, order, after-hours]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
updated_at: 2026-06-17T09:03:57+09:00
gate: Owner approval received 2026-06-17; prod order execution remains hardguarded
---

# TASK-014 KIS 시간외 주문 (장전·장후 단일가)

작업 ID: TASK-014
상태: 완료
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

현재 `place_order`는 정규장 주문(ORD_DVSN 00/01)만 지원한다. 장전(08:30~09:00) 단일가(05)와 장후(15:40~16:00) 단일가(06) 주문을 지원하면 전략의 유연성이 높아진다. 거래시간 가드를 함께 조정해야 안전하다.

## 구현 범위

- ORD_DVSN 코드 확장: 05(장전 단일가), 06(장후 단일가)
- `place_order`에 `after_hours: bool` 파라미터 또는 `OrderType` enum 확장
- 거래시간 가드 로직 조정 — 시간외 창 (08:30~09:00, 15:40~16:00) 허용
- 리스크 게이트에서 시간외 주문 플래그 인식
- paper 모드에서 시간외 주문 smoke 테스트 시나리오 추가

## 완료 기준

- [ ] ORD_DVSN 05/06 주문 경로 구현
- [ ] 거래시간 가드 시간외 창 허용 확인 (단위 테스트)
- [ ] 리스크 게이트 연동 테스트
- [ ] `examples/kis/` 에 시간외 주문 payload 예제 추가

## 보류 기록

보류 시각: 2026-06-12T02:10:22+09:00

## 보류 사유

Autofolio `AGENTS.md §16`의 R3 surface에 해당한다.

- `app/brokers/kis/` 실주문 경로의 `place_order` 주문 파라미터를 바꿔야 한다.
- `app/risk/**` 안전 게이트와 거래시간 정책을 바꿔야 한다.
- 시간외 주문 정책은 실거래 안전 정책 변경에 해당한다.

Owner 승인 없이 코드 변경하지 않는다.

## 다음 조건

Owner가 TASK-014 진행을 명시 승인하면 다음 범위로 재개한다.

- `OrderType` 또는 주문 옵션 설계
- ORD_DVSN 05/06 payload 예제
- 거래시간/리스크 게이트 단위 테스트
- paper 시간외 smoke는 해당 시간대에 별도 수행

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