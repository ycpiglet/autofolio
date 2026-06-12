---
type: evidence
id: EVIDENCE-2026-06-12-003
status: 완료
author: QA + Research Agent + KIS API Engineer (Codex)
created: 2026-06-12
created_at: 2026-06-12T12:24:42+09:00
tags: [qa, quant, paper, scenario-catalog, research, engine]
scope: Autofolio paper/mock quant trading test case expansion
applies_to: [Autofolio host]
---

# EVIDENCE-2026-06-12-003 — Quant Scenario Catalog

## 요청

Owner 요청: "최대한 많은 테스트 케이스를 만들어줘... 실제로 퀀트 트레이딩에서 동작하는 모든 동작들을 리서치해서 테스트 케이스로 제작해서 보관해줘."

## Research Inputs

Primary/reference material used for scenario axes:

- KRX, "Guide to Trading in the Korean Stock Market": sessions, trading units, tick size, daily price limit, order/quotation availability, circuit breakers, VI, individual issue suspension.
  - `https://global.krx.co.kr/contents/GLB/01/0109/0109000000/guide_to_trading_in_the_korean_stock_market.pdf`
- FIX Trading Community, "Order State Changes": pending cancel, fill, cancel reject, canceled/rejected lifecycle states.
  - `https://www.fixtrading.org/online-specification/order-state-changes/`
- QuantConnect/LEAN docs, "Order Types" and "Scheduled Events": order type taxonomy, multi-asset scope, scheduled execution.
  - `https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-types`
  - `https://www.quantconnect.com/docs/v2/writing-algorithms/scheduled-events`

## Scope Control

- 실행: isolated temporary SQLite DB + `MockBrokerClient`.
- 실행하지 않음: prod 실전 주문, KIS paper 주문 대량 반복, 선물/옵션/해외/신용/공매도 실제 주문 경로.
- 보관 방식: 자동화 가능한 케이스는 pytest로 고정하고, 미구현/고위험 자산군은 QA catalog-only 케이스로 보관.

## Created Artifacts

- `agents/qa/test_cases/QUANT-TRADING-SCENARIO-CATALOG.md`
- `agents/qa/test_cases/INDEX.md`
- `tests/integration/test_quant_trading_scenario_catalog.py`

## Automated Case Breadth

| Family | Count | Result |
|--------|------:|--------|
| Supported asset x side x order type x size matrix | 96 | PASS |
| Repeated buy/sell churn | 1 scenario, 24 order/execution events | PASS |
| Multi-asset rebalance basket proxy | 1 scenario, 3 legs | PASS |
| Order lifecycle terminal states | 3 | PASS |
| Timer dry-run one-shot entry | 1 | PASS |
| Broad scenario file total | 103 pytest cases | PASS |

Coverage includes:

- Assets/proxies: cheap stock, mid stock, high-price stock, equity ETF, bond ETF proxy, commodity ETN proxy.
- Price/size: low price, mid price, high price, one share, small lot, large lot, very large lot.
- Side/order: BUY, SELL, LIMIT, MARKET.
- Strategy-like behavior: repeated churn, multi-asset rebalance, timer execution.
- Lifecycle: pending limit cancel reject, market pending then canceled, market pending then failed.

## Catalog-Only Backlog

Kept but not executed as live/paper orders:

- futures, options, FX futures, overseas equities, margin/short.
- stop, stop-limit, trailing stop, MOO/MOC, IOC/FOK, combo, option exercise.
- actual block/basket venue submission.
- real partial fill model, too-late-to-cancel, exchange halt/VI handling as first-class engine states.

Reason: current Autofolio order model supports domestic cash-like `LIMIT`/`MARKET` only. Extending broker order paths or `app/risk/**` for derivatives/short/overseas/after-hours is an Autofolio R3 surface and requires separate explicit approval.

## Verification

Commands:

- `pytest tests/integration/test_quant_trading_scenario_catalog.py -q` — 103 passed
- `pytest tests/integration/test_quant_trading_scenario_catalog.py tests/integration/test_paper_scenario_matrix.py tests/integration/test_mock_order_flow.py tests/integration/test_engine_e2e.py tests/unit/test_run_paper_engine_once.py -q` — 129 passed
- `pytest tests/unit -k "safety_checker or run_paper_engine_once or engine_market_fallback" -q` — 14 passed, 359 deselected
- `python -m py_compile tests\integration\test_quant_trading_scenario_catalog.py` — passed
- `python scripts/check_upstream_issues.py --warn` — OK
- `python scripts/generate_views.py --check` — OK: 24 TASK views up-to-date
- `python scripts/validate_task_schema.py` — OK
- `python scripts/check_agent_docs.py` — OK: 0 errors, 74 existing warnings
- `python scripts/doc_health_report.py` — Status G
- `python scripts/query_reports.py --kind BRIEF` — BRIEF-2026-06-12-003 indexed
- `git diff --check` — no whitespace errors; CRLF warnings only

## 판단

- 실전 전환 없이 대규모 mock/paper-safe 테스트 케이스를 보관했다.
- 현재 자동화 테스트는 코드가 실제로 지원하는 국내 현물/ETF/ETN 유사 `LIMIT`/`MARKET` 경로에 집중했다.
- 선물/옵션/채권 직접매매/복합주문은 카탈로그에 남겼고, 구현 전에는 자동 실행하지 않는다.
