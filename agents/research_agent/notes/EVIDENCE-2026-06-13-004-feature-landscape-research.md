---
type: evidence
id: EVIDENCE-2026-06-13-004
status: 완료
author: Research Agent + Lead Engineer + QA (Codex)
created: 2026-06-13
created_at: 2026-06-13T00:53:23+09:00
tags: [research, feature-landscape, brokerage, exchange, quant-platform, backlog]
scope: external brokerage/exchange/quant-platform feature landscape for Autofolio backlog
related_task: TASK-037
related_catalog: FEATURE-LANDSCAPE-CATALOG
prod_boundary: no product code, broker order path, risk policy, DB schema, secret, or prod behavior changed
---

# Feature Landscape Research

## Question

기능적으로 더 구현할 것이 남아 있는지 확인하기 위해 실제 증권앱, 브로커 사이트, 거래소,
퀀트 트레이딩 플랫폼, 트레이딩 도구가 제공하는 기능군을 조사하고 Autofolio에 반영할
후보와 잠재 후보를 분리한다.

## Source Basket

| Source | Evidence Used |
|--------|---------------|
| Interactive Brokers order types and algos | broad advanced order, algo, basket, block, attached order, reporting/tool surface |
| Alpaca placing orders | bracket/OCO/OTO and broker order class constraints |
| Fidelity conditional orders help | OTO/OCO/OTOCO behavior and cancel/replace caveats |
| KRX guide to Korean stock market | Korean sessions, off-hours, quotation types, block/basket, short-sale, circuit breaker, VI, trading halt |
| Nasdaq trade halt codes | halt/resumption field model and halt reason taxonomy |
| NYSE order imbalances | auction imbalance as a real market-data product family |
| TradingView features | supercharts, screeners, alerts, Pine/backtesting style research workflow |
| Robinhood stock screeners | saved screeners/watchlists and filter families |
| Schwab thinkorswim paperMoney | paper/live parity, scanners, alerts, advanced charting, portfolio tracking |
| QuantConnect paper trading | live real-time data with simulated fills, asset classes, fees/slippage/fills model |
| QuantConnect order types and scheduled events | order-type taxonomy and deterministic scheduled event model |
| FIX Trading Community order-state changes | canonical order lifecycle states and transitions |
| Toss Securities investment-products page | Korea retail app reference; public page did not expose deep feature details in fetched HTML |

Source URLs:

- https://www.interactivebrokers.com/en/trading/ordertypes.php
- https://docs.alpaca.markets/us/docs/orders-at-alpaca
- https://www.fidelity.com/webcontent/ap002390-mlo-content/19.09/help/learn_trading_conditional.shtml
- https://global.krx.co.kr/contents/GLB/01/0109/0109000000/guide_to_trading_in_the_korean_stock_market.pdf
- https://nasdaqtrader.com/Trader.aspx?id=TradeHaltCodes
- https://www.nyse.com/data-products/catalog/imbalances
- https://www.tradingview.com/features/
- https://robinhood.com/us/en/support/articles/stock-screeners/
- https://www.schwab.com/trading/thinkorswim/paper-trading
- https://www.quantconnect.com/docs/v2/cloud-platform/live-trading/brokerages/quantconnect-paper-trading
- https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-types
- https://www.quantconnect.com/docs/v2/writing-algorithms/scheduled-events
- https://www.fixtrading.org/online-specification/order-state-changes/
- https://corp.tossinvest.com/en/investment-products

## Feature Families Observed

| Family | Real-World Pattern | Autofolio Current Coverage | Gap |
|--------|--------------------|----------------------------|-----|
| Broker order entry | market, limit, stop, stop-limit, trailing stop, MOO/MOC, IOC/FOK, bracket, OCO, OTO, OTOCO, basket/block | cash stock/ETF style MARKET/LIMIT, paper order smoke, cancel, order history, scenario tests | advanced order and live order-path work is R3; existing TASK-014/028/030 |
| Order lifecycle | pending, partial, filled, canceled, rejected, cancel reject, too-late-to-cancel | mock lifecycle tests in TASK-029; paper lifecycle smoke | production lifecycle semantics require R3 order-flow review |
| Market sessions | regular, opening/closing auction, pre/after-hours, holiday, cutoff windows | regular and close/after-close dry-run checks; TASK-014 on hold | after-hours ordering remains R3 |
| Market structure and halts | halt code taxonomy, resumption quote/trade time, VI/circuit breaker, auction imbalance | KRX/FIX/QuantConnect scenario catalog; disclosure UI/system-state block; TASK-031 hold | engine risk gates need Owner approval |
| Research and charting | multi-timeframe charts, drawing/indicator alerts, scriptable alerts, screeners, saved lists | intraday OHLCV, sector, fundamentals, dividend, disclosure, order book, basic analysis pages | saved screeners/watchlist and richer alert rules are implementable without order path |
| Backtest and strategy research | scheduled events, strategy reports, paper/live parity, overfit checks | backtest/analysis UI exists; scheduled strategy mock tests in TASK-034 | report quality and experiment traceability can be improved without live execution |
| Portfolio analytics | performance, fees, slippage, buying power, holdings, cashbook, tax/reporting | paper holdings sync, mock cash/fee/slippage/concentration model in TASK-033 | read-only performance attribution/tax-lot style reporting remains |
| Data quality and corporate actions | stale quotes, missing bars, splits/dividends, data source disclaimers | validator/fixture in TASK-032, dividend/fundamental reads | engine no-order hook is R3; reporting/display can remain read-only |
| Broker/platform capability model | per-broker support matrix for assets, order types, sessions, fees, fills | KIS-focused code and docs; scenario catalog maps gaps | versioned capability matrix would prevent UI from promising unsupported features |
| Education/collaboration/social | paper practice, education links, idea sharing/chat, notes | agent reports and QA evidence; no user-facing education/social layer | low priority for personal OS; potential only |

## Reflect Now

These are useful and remain outside Autofolio R3 surfaces because they can be implemented as
read-only, mock/backtest, docs/config, or UI-only work.

| Candidate | Why It Matters | Task |
|-----------|----------------|------|
| Watchlist, screener, and alert rule expansion | Actual apps expose saved filters, lists, and rich alert conditions; Autofolio already has price, sector, fundamental, dividend, disclosure, and order-book data to support this without placing orders. | TASK-038 |
| Backtest and research report hardening | Quant platforms make strategy evidence portable through reports, scheduled-event semantics, fills/fees/slippage assumptions, and paper/live parity notes. | TASK-039 |
| Portfolio performance and tax-lot style read-only reporting | Trading platforms surface P&L, attribution, cash/fees/slippage, and reporting views so the user can see what they hold and why performance changed. | TASK-040 |
| Broker capability and feature parity matrix | Advanced features differ by broker, asset, session, and account type; a capability map prevents unsupported order types or asset classes from leaking into UI. | TASK-041 |

## Keep As Potential Or R3-Hold

No new duplicate R3 tasks are needed. The following potential features map to existing held tasks:

| Potential Feature | Existing Task | Reason |
|-------------------|---------------|--------|
| After-hours order entry | TASK-014 | KIS `place_order` and order policy boundary |
| Margin/short and short-sale rules | TASK-021 | order path and risk policy boundary |
| Overseas equities and FX/currency handling | TASK-022 | new broker/order/portfolio integration boundary |
| KRX alternative products beyond current proxies | TASK-026 | product-specific order/risk support boundary |
| Futures/options/derivatives | TASK-027 | derivatives routing and risk boundary |
| Stop, trailing, MOO/MOC, IOC/FOK, bracket/OCO/OTO/OTOCO | TASK-028 | advanced order semantics and live order behavior boundary |
| Block/basket venue submission | TASK-030 | venue/broker submission boundary |
| Halt/VI/circuit-breaker engine no-order gates | TASK-031 | `app/risk/**` or live order-blocking policy boundary |
| Invalid-data no-order hook | TASK-032 | `OrderFlow`/safety path integration boundary |

Long-term product ideas kept as potential only: mobile push, account-transfer workflows, tax
document ingestion, community/social research, multi-broker aggregation, options Greeks, auction
imbalance feed integration, and AI narrative copilot. They are not near-term Autofolio MVP work unless
Owner changes scope.

## Implication

Autofolio still has meaningful feature depth to add, but the safe next layer is not more live-order
surface. The next implementable lane is read-only research/discovery/reporting/capability UX. Live
broker expansion and advanced order behavior should stay behind Owner approval and existing R3 tasks.

## Uncertainty

- Toss Securities public page did not expose a deep feature list through fetched HTML, so Korean retail
  app comparison remains shallow unless manual/app-store/interactive review is requested.
- Broker pages change over time; this evidence is a 2026-06-13 research snapshot.
- KIS-specific support for several advanced features still requires official KIS endpoint verification
  before any R3 task is approved.
