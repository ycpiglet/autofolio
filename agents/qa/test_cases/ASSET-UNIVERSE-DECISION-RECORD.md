---
type: decision-record
id: ASSET-UNIVERSE-DECISION-RECORD
status: active
owner: QA
created: 2026-06-13
created_at: 2026-06-13T01:24:07+09:00
scope: approve/reject record for multi-asset Autofolio integration
automation: []
prod_boundary: catalog only; no product code, live broker, custody, withdrawal, money movement, risk policy, schema, or prod mutation
---

# Asset Universe Decision Record

이 기록은 Autofolio가 여러 자산군을 "녹여낼 수 있는지"에 대한 승인/기각 표다.
승인은 투자 실행 승인이 아니라 제품 기능 범위 승인이다. 기본 전제는 read-only,
manual, mock/backtest, reporting, capability matrix다.

## Decision Matrix

| Asset / Product | Decision | Allowed In Autofolio | Not Allowed Without New Approval |
|-----------------|----------|----------------------|----------------------------------|
| 개인 트레이더 profile | 승인 | local profile, strategy notes, trading journal, risk budget, preference metadata | copy-trading auto-follow, third-party signal auto-order |
| 국내 상장 주식/ETF/ETN/REIT/ELW proxy | 승인 | current KIS/KRX read-only, paper/mock tests, reports, watchlists | new live order behavior outside existing approved path |
| 해외주식/글로벌 ETF | 조건부 승인 | manual/read-only holdings, FX valuation, capability flag | live order, settlement, currency conversion automation |
| 코인 spot | 조건부 승인 | manual/read-only exchange import, price watch, exposure report | auto trade, withdrawal/custody key, staking, yield, DeFi |
| 코인 futures/options | 보류/R3 | catalog and education only | leverage/liquidation-sensitive live execution |
| 금 | 조건부 승인 | KRX/CME/ETP price tracking, manual holding, exposure report | physical delivery/storage, live futures/options/order support |
| 은 | 조건부 승인 | CME/ETP/manual exposure tracking | physical delivery/storage, live futures/options/order support |
| 오일 | 조건부 승인 | ETF/ETN/futures quote tracking, macro scenario reporting | physical commodity, live futures/options, leveraged auto trading |
| 달러 현금/환율/환매 | 조건부 승인 | KRW/USD rate, USD cash bucket, manual cashflow, overseas valuation | automatic FX conversion, remittance, redemption, FX derivatives |
| FX futures/options | 보류/R3 | catalog, delayed/historical data, risk labels | live derivative trading and margin automation |
| 부동산 listed exposure | 조건부 승인 | listed REIT/REIT ETF and manual real-estate bucket | private property transaction, appraisal automation |
| 부동산 조각투자 | 보류/R3 | licensed-platform catalog and manual position record | platform execution/subscription/redemption/secondary trading |
| 저작권/음원 royalty | 보류/R3 | manual royalty cashflow and position record | buy/sell automation, royalty collection automation, valuation guarantee |
| 상품 옵션/options | 보류/R3 | education, payoff diagrams, scenario simulation, approval-level metadata | live options, uncovered writing, 0DTE, margin strategies |
| leveraged/inverse ETP | 기각 by default | risk education only | default inclusion or automated trading |
| physical commodities logistics | 기각 | none, except manual note field | storage, delivery, insurance, warehouse receipt operations |
| DeFi/P2P/yield/lending | 기각 | none for MVP | protocol integration, lending, staking, yield farming |

## Implementation Guardrails

1. Every asset class must have `decision`, `allowed_scope`, `blocked_scope`, `valuation_source`,
   `custody_source`, `liquidity_tier`, `leverage_flag`, and `execution_capability`.
2. UI may show a blocked asset only as read-only/manual if `execution_capability != supported`.
3. No connector may request write, trade, withdrawal, remittance, or private-key permissions under
   this record.
4. Illiquid/private assets must show valuation as user-provided or third-party reported, never
   market-confirmed unless a licensed source is attached.
5. Any transition from `조건부 승인` or `보류/R3` to execution support requires a new TASK,
   Owner approval, risk review, and focused paper/mock validation.

## Task Mapping

| Decision Area | Task |
|---------------|------|
| Universal asset taxonomy and capability matrix | TASK-041 |
| This research/decision record | TASK-042 |
| Portfolio reporting surface for approved read-only assets | TASK-040 |
| Watchlists/screeners/alerts for read-only assets | TASK-038 |
| Backtest/report assumptions for derivatives and commodities | TASK-039 |
| Overseas live order | TASK-022 |
| Alternative products | TASK-026 |
| Derivatives and options | TASK-027 / TASK-028 |
| Block/basket and market-structure risk | TASK-030 / TASK-031 |

## Evidence

- Research note: `agents/research_agent/notes/EVIDENCE-2026-06-13-005-asset-universe-decision-research.md`
- Owner BRIEF: `agents/lead_engineer/reports/BRIEF-2026-06-13-005.md`
