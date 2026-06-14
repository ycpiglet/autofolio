---
type: task
id: TASK-026
status: 보류
owner: KIS API Engineer
assignees: [KIS API Engineer, QA]
priority: Medium
difficulty: 상
est_hours: 5
est_tokens: 50000
tags: [kis, qa, asset-class, bond, reit, elw, etn]
gate: Owner approval required before any live broker/order-path support; mock catalog tests may be drafted first
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-009
created: 2026-06-12
created_at: 2026-06-12T12:27:28+09:00
updated_at: 2026-06-12T12:27:28+09:00
---

# TASK-026 KRX Alternative Products Test Support

작업 ID: TASK-026
상태: 보류
Owner: KIS API Engineer
기록 시각: 2026-06-12T12:27:28+09:00

## 배경

`QUANT-TRADING-SCENARIO-CATALOG`의 `QT-ASSET`에는 REIT, ELW, 직접 채권, ETN product-specific 케이스가 있다. 현재 자동화 테스트는 주식/ETF/채권 ETF proxy/원자재 ETN proxy를 cash-like mock asset으로만 검증한다.

## 왜 아직 실행 못하는가

- 직접 채권/ELW/REIT/ETN별 주문 가능 시간, 호가, 단위, 위험 정책이 별도 모델로 구현되어 있지 않다.
- KIS broker order path와 `app/risk/**` 정책에 닿을 수 있어 R3 surface다.

## Done When

- 각 상품군의 broker capability matrix와 risk gate가 문서화된다.
- mock 테스트가 상품별 tick/trading unit/price-limit/whitelist 정책을 검증한다.
- paper smoke는 Owner 승인 후 별도 1주 또는 최소 단위 절차로만 실행한다.

## Verification

- `pytest tests/integration/test_quant_trading_scenario_catalog.py -q`
- 상품군별 신규 pytest selector

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-R3-ORDER-SURFACE.md`
- Taskset: `agents/project/initiatives/TASKSET-R3-ORDER-SURFACE.md`
