---
type: evidence
id: EVIDENCE-2026-06-12-002
status: 완료
author: QA + KIS API Engineer (Codex)
created: 2026-06-12
created_at: 2026-06-12T12:07:12+09:00
tags: [qa, paper, engine, risk, ui, scenario-matrix]
scope: Autofolio paper-mode scenario matrix, no prod trading
applies_to: [Autofolio host]
---

# EVIDENCE-2026-06-12-002 — Paper Scenario Matrix Validation

## 범위

- 포함: paper-mode 엔진/리스크/DB/UI backend 시나리오 매트릭스, KIS paper read-only 확인.
- 제외: prod 실전 주문, 신규 실전 전환, paper 주문 대량 반복.
- 원칙: Owner가 명시적으로 실전 투자 전환을 말하기 전까지 모든 검증은 모의투자 또는 격리 테스트 DB에서 수행한다.

## 시나리오 매트릭스

격리된 temporary DB와 `MockBrokerClient`로 다음 상황을 생성하고 검증했다.

| # | Scenario | Expected | Result |
|---|----------|----------|--------|
| 1 | BUY limit trigger | order FILLED, condition TRIGGERED | PASS |
| 2 | BUY limit not triggered | no order, condition ACTIVE | PASS |
| 3 | SELL limit trigger | order FILLED, condition TRIGGERED | PASS |
| 4 | kill switch active | no order, safety rejection | PASS |
| 5 | auto trading disabled | no order, safety rejection | PASS |
| 6 | global L1 mode | no order, manual-approval rejection | PASS |
| 7 | symbol L1 mode over global L2 | no order, manual-approval rejection | PASS |
| 8 | non-whitelisted symbol | no order, whitelist rejection | PASS |
| 9 | max order amount exceeded | no order, amount rejection | PASS |
| 10 | daily order amount exceeded | no new order, daily limit rejection | PASS |
| 11 | pending limit without fallback | cancel order, condition TRIGGERED | PASS |
| 12 | pending limit with market fallback | limit canceled then market FILLED | PASS |
| 13 | direct MARKET returns PENDING then FILLED | poll status, FILLED log | PASS after fix |
| 14 | direct MARKET stays PENDING | PENDING log, condition ERROR | PASS after fix |
| 15 | repeated broker failures | circuit breaker disables auto trading on next run | PASS |
| 16 | UI backend reflection after fill | holdings and recent fills reflect filled symbol | PASS |

## BUG-2026-06-12-005 — Direct MARKET PENDING treated as limit-pending cancel

| 육하원칙 | 내용 |
|----------|------|
| 누가 | Paper scenario matrix |
| 무엇을 | Direct `MARKET` order where broker returns `PENDING` like KIS |
| 언제 | 2026-06-12T12:04+09:00 |
| 어디서 | `app/engine/order_flow.py` |
| 왜 | `place_order()`가 `PENDING`이면 주문 종류와 무관하게 `_handle_pending_limit_order()`로 보내 취소 경로를 탔다 |
| 어떻게 | MARKET condition이 `Limit order canceled. Market fallback disabled.`로 처리되고 SQLite `order_status=CANCELED`가 됨 |

Severity: High in paper/prod readiness context. KIS real broker returns accepted orders as `PENDING`, so direct market orders must poll status instead of being canceled as if they were limit orders.

Fix:

- `OrderFlow.process_condition_once()`에서 `order_type == MARKET` and `result.status == PENDING`이면 `_poll_fill(..., fallback_label="Market order")`로 보낸다.
- 기존 LIMIT pending cancel/fallback behavior는 유지한다.

## Verification

Commands:

- `pytest tests/integration/test_paper_scenario_matrix.py -q` — 16 passed
- `pytest tests/integration/test_paper_scenario_matrix.py tests/integration/test_mock_order_flow.py tests/integration/test_engine_e2e.py tests/unit/test_engine_market_fallback.py tests/unit/test_run_paper_engine_once.py -q` — 31 passed
- `pytest tests/unit -k kis -q` — 118 passed, 255 deselected
- `pytest tests/unit -k "backend or view or beta_cycle001" -q` — 37 passed, 336 deselected
- `python -m py_compile app\engine\order_flow.py scripts\kis_paper_order_smoke.py scripts\run_paper_engine.py app\brokers\kis\kis_client.py app\ui\backend.py` — passed
- `python scripts/check_upstream_issues.py --warn` — OK: no unreported upstream bug signals
- `python scripts/generate_views.py --check` — OK: TASK views up-to-date
- `python scripts/validate_task_schema.py` — OK
- `python scripts/check_agent_docs.py` — OK: 0 errors, 74 existing warnings
- `python scripts/doc_health_report.py` — Status G
- `python scripts/query_reports.py --kind BRIEF` — BRIEF-2026-06-12-002 indexed
- `git diff --check` — no whitespace errors; CRLF warnings only

KIS paper read-only check:

- `env=paper`
- `paper_endpoint=true`
- safety state: `auto_trading_enabled=false`, `kill_switch_active=true`, `global_mode=L1`
- KIS positions are readable: `positions_count=3`, includes `069500`
- today's KIS paper orders are readable: `today_orders_count=3`
- UI/KIS account summary source: `kis`

## 판단

- 옵션/상황 매트릭스는 paper-safe 범위에서 통과했다.
- 실전 전환은 아직 하지 않는다.
- 다음 실전 전환 전에는 prod 전용 1주 절차와 별도 R3 승인, 장중 수동 관찰, HTS/app visual confirmation이 필요하다.
