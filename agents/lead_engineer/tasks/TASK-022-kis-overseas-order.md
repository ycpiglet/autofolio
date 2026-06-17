---
type: task
id: TASK-022
status: 완료
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 상
est_hours: 8
est_tokens: 50000
tags: [kis, overseas, us-stocks]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
updated_at: 2026-06-17T09:03:57+09:00
---

# TASK-022 KIS 해외주식 주문 (미국·홍콩 등)

작업 ID: TASK-022
상태: 완료
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

US 에셋(S&P500 구성종목 등)을 화이트리스트에 포함하려면 해외주식 전용 TR셋이 필요하다. KIS는 해외주식 전용 API (`/uapi/overseas-stock/v1/trading/order`, TR `TTTT1002U`)를 별도로 제공한다. 환율 처리가 포함되어 국내주식 대비 복잡도가 높다.

## 구현 범위

- `KisClient.place_overseas_order(symbol, market, side, qty, price)` 구현
- market 파라미터: 'NASD'(나스닥), 'NYSE', 'AMEX', 'SEHK'(홍콩) 등
- TR: `TTTT1002U`(실전 매수), `TTTT1006U`(실전 매도), `VTTT1002U`(paper)
- 환율 처리: KRW→USD 환산, 주문 통화 파라미터 처리
- US 에셋 화이트리스트 지원 (`app/config.py` 확장)
- 해외주식 잔고 조회 및 포트폴리오 통합 (KRW 환산 표시)

## 보류 기록

- 보류 시각: 2026-06-12T09:04:51+09:00
- 사유: 신규 해외주식 주문 경로(`place_overseas_order`), KIS 해외 주문 TR, 환율/주문 통화 처리, 화이트리스트 및 포트폴리오 통합을 포함한다. 주문 실행 surface와 안전 정책에 닿는 R3 변경이다.
- 결정: Owner 명시 승인 전에는 코드 변경하지 않고 보류한다.
- 재개 조건: Owner가 해외주식 주문 경로 변경을 명시 승인하고, paper-only smoke와 prod 하드가드 검증 계획을 확정한다.

## 완료 기준

- [ ] `place_overseas_order()` 구현 및 단위 테스트
- [ ] 환율 처리 로직 검증 (USD/KRW 변환)
- [ ] paper 모드 해외주식 smoke 테스트
- [ ] 포트폴리오 화면 해외주식 잔고 KRW 환산 표시

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