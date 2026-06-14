---
type: task
id: TASK-041
status: 완료
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
updated_at: 2026-06-14T17:28:16+09:00
---

# TASK-041 Broker Capability Feature Parity Matrix

작업 ID: TASK-041
상태: 완료
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

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-RESEARCH-REPORTING.md`
- Taskset: `agents/project/initiatives/TASKSET-RESEARCH-REPORTING.md`

## 완료 기록

완료 시각: 2026-06-14T17:28:16+09:00
검토자: Lead Engineer / KIS API Engineer / QA (self-review)

- 원 요청: 브로커/플랫폼 capability parity matrix 작성 — KIS/mock/paper vs 참조 플랫폼 비교.
- 실제 작업:
  - `ASSET-UNIVERSE-DECISION-RECORD`(자산군 승인/조건부/R3/기각) 흡수.
  - `EXTERNAL-APP-API-DECISION-RECORD`(커넥터 권한 클래스) 흡수.
  - `FEATURE-LANDSCAPE-CATALOG` feature family 분류 반영.
  - `app/brokers/`, `app/common/enums.py`, `app/risk/` 코드 실측 기반 데이터 입력.
  - 13개 섹션 capability matrix 작성 (`docs/BROKER-CAPABILITY-PARITY-MATRIX.md`).
  - 구조 gate 테스트 10개 작성 (`tests/integration/test_capability_matrix.py`).
  - UNIT-TASK-041-001.md 작성.
  - TASK-041 stub 완료 처리, INDEX.md 갱신.
- 결과:
  - UI/전략이 참조할 수 있는 단일 capability vocabulary 확립.
  - SUPPORTED/MOCK-ONLY/PAPER-ONLY/CONDITIONAL/R3-HOLD/REJECTED/NOT-IMPL 7개 label 정의.
  - R3 태스크(014/021/022/026/027/028/030/031/032) 모두 blocked 기능과 매핑.
  - 레버리지/인버스 ETP, DeFi 등 기각 자산 명시.

## 증거

- `docs/BROKER-CAPABILITY-PARITY-MATRIX.md` — 주요 capability matrix 산출물 (13섹션)
- `tests/integration/test_capability_matrix.py` — 구조 gate 테스트 (10 tests)
- `agents/lead_engineer/tasks/units/TASK-041/UNIT-TASK-041-001.md` — 유닛 스펙
- 입력 근거:
  - `agents/qa/test_cases/ASSET-UNIVERSE-DECISION-RECORD.md`
  - `agents/qa/test_cases/EXTERNAL-APP-API-DECISION-RECORD.md`
  - `agents/qa/test_cases/FEATURE-LANDSCAPE-CATALOG.md`

## 리뷰

- KIS TR ID 및 `OrderType` enum은 코드 실측값 사용 (추정 없음).
- `trading_window.py` 09:10–15:20 KST 창은 SafetyChecker 실측값.
- Mock fee/slippage 기본값(0.0)은 코드에서 직접 확인.
- CONDITIONAL 자산은 read-only/manual 범위로만 허용 — UI 실행 버튼 금지 규칙 명시.

실측 비용 (시간): ~0.7h
실측 비용 (LLM 토큰): unknown
