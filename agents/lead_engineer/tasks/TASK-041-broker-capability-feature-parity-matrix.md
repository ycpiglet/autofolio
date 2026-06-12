---
type: task
id: TASK-041
status: 대기
owner: Lead Engineer
assignees: [Lead Engineer, KIS API Engineer, QA]
priority: Medium
difficulty: 중
est_hours: 3
est_tokens: 35000
tags: [feature-landscape, broker-capability, parity, docs, qa]
gate: docs/config/test-only; no broker order implementation, order path, risk policy, schema migration, secret, or prod mutation
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-13-004
created: 2026-06-13
created_at: 2026-06-13T00:53:23+09:00
updated_at: 2026-06-13T00:53:23+09:00
---

# TASK-041 Broker Capability Feature Parity Matrix

작업 ID: TASK-041
상태: 대기
Owner: Lead Engineer
요청 시각: 2026-06-12
기록 시각: 2026-06-13T00:53:23+09:00

## 배경 및 목적

브로커와 퀀트 플랫폼은 지원 자산, 주문유형, 세션, account type, fee/fill/slippage model이
다르다. Autofolio가 KIS 중심에서 기능을 확장할 때, UI나 전략이 지원되지 않는 기능을
노출하지 않도록 명시적 capability matrix가 필요하다.

## 범위

- 포함:
  - `docs/` 또는 `agents/qa/test_cases/`의 capability matrix.
  - KIS/mock/paper/current Autofolio vs reference platforms 비교.
  - asset class, session, order type, lifecycle, fees/slippage/fill model, data source, alert/backtest feature flags.
  - `ASSET-UNIVERSE-DECISION-RECORD`의 승인/조건부 승인/보류/R3/기각 상태를 capability vocabulary로 흡수.
  - `EXTERNAL-APP-API-DECISION-RECORD`의 connector/API permission class를 external capability vocabulary로 흡수.
  - "supported / mock-only / paper-only / r3-hold / unsupported" 상태 정의.
  - tests that fail if unsupported feature labels are marked as supported without evidence.
- 제외:
  - 브로커 구현 추가.
  - `place_order`, `cancel_order`, `OrderFlow`, `app/risk/**` 변경.
  - secret, account, production data access.

## Done When

1. capability matrix가 KIS/mock/paper/current Autofolio와 reference feature families를 비교한다.
2. asset universe decision record를 반영해 asset class별 `approved / conditional / r3-hold / rejected` 상태를 표시한다.
3. unsupported/r3-hold/rejected 기능이 UI에서 supported로 표시되지 않도록 테스트가 있다.
4. 기존 TASK-014/021/022/026/027/028/030/031/032/042/043과 연결된다.
5. docs/schema gates가 통과한다.
