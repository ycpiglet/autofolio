---
type: task
id: TASK-025
status: 완료
owner: QA
assignees: [QA, Research Agent, KIS API Engineer]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 25000
tags: [qa, quant, paper, scenario-catalog, engine]
gate: paper/mock only; prod 실전 주문 전환 금지
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-008
created: 2026-06-12
created_at: 2026-06-12T12:24:42+09:00
updated_at: 2026-06-12T12:27:28+09:00
---

# TASK-025 Quant Trading Scenario Catalog

작업 ID: TASK-025
상태: 완료
Owner: QA
요청 시각: 2026-06-12T12:17:00+09:00
기록 시각: 2026-06-12T12:24:42+09:00

## 배경 및 목적

Owner 요청은 종목/자산군, 가격대, 매수/매도 수량, 반복 거래, 타이머 실행 등 실제 퀀트 트레이딩에서 필요한 동작을 최대한 많이 테스트 케이스로 만들고 보관하는 것이다.

## 범위

- 포함: research-backed scenario catalog, executable mock/paper-safe pytest cases.
- 제외: prod 실전 주문, KIS paper 주문 대량 반복, 선물/옵션/해외/신용/공매도 실제 주문 경로.

## 진행 기록

### 2026-06-12T12:24:42+09:00

- KRX/FIX/QuantConnect 자료를 기준으로 케이스 축을 정리.
- QA 카탈로그 작성:
  - `agents/qa/test_cases/QUANT-TRADING-SCENARIO-CATALOG.md`
  - `agents/qa/test_cases/INDEX.md`
- 자동화 테스트 추가:
  - `tests/integration/test_quant_trading_scenario_catalog.py`
- 자동화된 케이스:
  - 96개 asset/side/order/size matrix.
  - 12회 buy/sell churn, 총 24 order/execution events.
  - multi-asset rebalance basket proxy.
  - pending/cancel/failed lifecycle edge.
  - timer dry-run one-shot entry.

## 완료 기록

완료 시각: 2026-06-12T12:24:42+09:00
검토자: QA + Independent Auditor (Codex self-review)
감사 로그: AUDIT-2026-06-12-008
실측 비용 (시간): 약 0.35h
실측 비용 (LLM 토큰): unknown

- 원 요청: 최대한 많은 퀀트 트레이딩 테스트 케이스 제작/보관.
- 실제 작업: research-backed catalog와 103개 pytest 케이스 추가.
- 결과: 새 테스트 103 passed, 기존 paper/engine 회귀 포함 129 passed.
- 안전 경계: prod 미전환, KIS live order 없음, derivatives/short/overseas/after-hours는 catalog-only.
- 최종 게이트: upstream warning check OK, generated views/schema/docs/report gates OK, diff whitespace check OK.

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-12-003-quant-scenario-catalog.md`
- `agents/qa/test_cases/QUANT-TRADING-SCENARIO-CATALOG.md`
- `tests/integration/test_quant_trading_scenario_catalog.py`
- `agents/lead_engineer/reports/BRIEF-2026-06-12-003.md`

## 리뷰

- 현재 엔진이 지원하는 `LIMIT`/`MARKET` 현물형 경로는 자동화했다.
- 선물/옵션/해외/신용/공매도/after-hours는 주문 경로와 risk policy 변경이 필요해 R3 catalog-only로 보관했다.
- 반복 매매와 timer dry-run은 실제 운영 스케줄러/DB 오염 없이 임시 DB로 검증했다.

## Independent Audit

판정: pass
근거: executable tests are isolated from KIS/prod, cover broad current behavior, preserve unsupported high-risk surfaces as catalog-only, focused regressions passed, and documentation gates remained green.
