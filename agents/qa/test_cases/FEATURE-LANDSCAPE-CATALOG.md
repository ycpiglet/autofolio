---
type: feature-catalog
id: FEATURE-LANDSCAPE-CATALOG
status: active
owner: QA
created: 2026-06-13
created_at: 2026-06-13T00:53:23+09:00
scope: external feature landscape to Autofolio backlog mapping
automation: []
prod_boundary: catalog only; no product code, live broker, order path, risk policy, schema, or prod mutation
---

# Feature Landscape Catalog

이 카탈로그는 실제 증권앱, 브로커, 거래소, 퀀트 플랫폼, 트레이딩 도구에서 관찰되는
기능군을 Autofolio 현재 상태와 비교해 "반영할 만한 것"과 "잠재/보류로 남길 것"으로
분리한다.

## Classification Rubric

| Class | Meaning | Default Handling |
|-------|---------|------------------|
| covered | 이미 구현 또는 검증 기록이 충분함 | 회귀 테스트와 문서만 유지 |
| reflect-now | R1/R2로 구현 가능한 읽기전용, UI, 문서, mock/backtest 기능 | 신규 대기 TASK로 등록 |
| r3-hold | KIS 주문, `OrderFlow`, `app/risk/**`, DB schema/migration, prod safety 정책 경계 | 기존 보류 TASK에 매핑 |
| potential | MVP 밖이거나 가치/비용이 아직 약함 | Owner가 범위 변경할 때까지 catalog-only |

## Feature Family Matrix

| Family | Examples In Real Platforms | Autofolio State | Class | Mapping |
|--------|----------------------------|-----------------|-------|---------|
| Basic orders | market, limit, cancel, order history | paper order smoke, cancel, order history, UI sync done | covered | TASK-023/035/036 |
| Advanced orders | stop, stop-limit, trailing, bracket, OCO, OTO, OTOCO, IOC/FOK, MOO/MOC | catalog/test knowledge only | r3-hold | TASK-028 |
| After-hours/session orders | pre-open, after-hours, closing price, periodic call auction | dry-run/session checks; no order-path mutation | r3-hold | TASK-014 |
| Margin/short | borrowing, short-sale, uptick/rule restrictions | no live support | r3-hold | TASK-021 |
| Overseas/multi-market | US/foreign equities, FX/currency, market calendars | no live support | r3-hold | TASK-022 |
| Derivatives/alternative products | futures, options, ELW, bonds, product-specific ETN/ETF rules | proxy/mock coverage only | r3-hold | TASK-026/027 |
| Basket/block | multi-leg and negotiated-size execution | mock multi-condition coverage only | r3-hold | TASK-030 |
| Halt/VI/circuit breaker | halt reason codes, resumption time, VI, market-wide CB | catalog and some system-state checks | r3-hold | TASK-031 |
| Data quality/corporate actions | stale quote, missing OHLCV, holiday, split/dividend | validator/fixture done; no order-flow hook | r3-hold | TASK-032 |
| Screeners/watchlists | saved screens, filters by price/volume/sector/fundamental/dividend/disclosure | raw data exists; saved workflow thin | reflect-now | TASK-038 |
| Alerts | price/drawing/script/condition alerts, delivery channels | Notifier and alerts tab exist; rules can expand safely | reflect-now | TASK-038 |
| Backtest/research reports | strategy report, parameters, fills/slippage assumptions, benchmark, drawdown | backtest and scheduled mock patterns exist; reporting thin | reflect-now | TASK-039 |
| Portfolio analytics | holdings, P&L, fees, cash, slippage, attribution, tax-lot style views | holdings UI and mock portfolio model exist; analysis can deepen | reflect-now | TASK-040 |
| Broker capability matrix | per-broker asset/order/session/account feature flags | KIS focused; no explicit parity matrix | reflect-now | TASK-041 |
| Education/social/community | paper tutorials, idea sharing, chat rooms, public community | not core to personal OS | potential | catalog-only |
| Mobile/account operations | push notifications, account transfer, documents, tax statements | outside current local Streamlit MVP | potential | catalog-only |
| AI copilot narrative | trade/exposure explanation, research summarization | internal agents create reports, no end-user copilot | potential | catalog-only |

## Reflect-Now Backlog

| Task | Scope | Done When |
|------|-------|-----------|
| TASK-038 | Watchlist/screener/alert rule expansion | saved screeners/watchlists and non-order alert rules are visible in UI and tested without order submission |
| TASK-039 | Backtest/research report hardening | each backtest has benchmark, parameters, fills/fee/slippage assumptions, drawdown, trades, and paper/live caveat |
| TASK-040 | Portfolio performance/tax-lot style reporting | read-only performance attribution, realized/unrealized P&L, fees/slippage/cashflow, and tax-lot placeholders are visible |
| TASK-041 | Broker capability/feature parity matrix | unsupported asset/order/session features are documented and testable before UI exposes them |

## Potential Backlog Rules

1. Do not create duplicate R3 tasks when an existing held TASK already covers the surface.
2. Any feature that can submit, modify, cancel, or block real orders must stay in R3 until Owner approves scope.
3. Add mock/backtest/read-only coverage first, then paper smoke, then production-path design only after explicit approval.
4. Capability flags should precede UI affordances for unsupported brokers, assets, sessions, and order types.

## Evidence

- Research note: `agents/research_agent/notes/EVIDENCE-2026-06-13-004-feature-landscape-research.md`
- Owner BRIEF: `agents/lead_engineer/reports/BRIEF-2026-06-13-004.md`
