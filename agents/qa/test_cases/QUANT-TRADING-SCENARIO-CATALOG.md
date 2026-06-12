---
type: test-case-catalog
id: QUANT-TRADING-SCENARIO-CATALOG
status: active
owner: QA
created: 2026-06-12
created_at: 2026-06-12T12:20:48+09:00
scope: paper/mock quant trading scenario coverage
automation:
  - tests/integration/test_quant_trading_scenario_catalog.py
  - tests/integration/test_paper_scenario_matrix.py
prod_boundary: no prod trading; no KIS live order in this catalog
---

# Quant Trading Scenario Catalog

이 카탈로그는 실전 전환 전까지 `mock`/`paper`에서 검증해야 하는 퀀트 트레이딩 동작 목록이다.
실제 KIS 주문을 내는 케이스는 별도 Owner 승인 전까지 포함하지 않는다.

## Research Basis

- KRX guide: regular session, off-hours, trading unit, tick size, daily price limit, quotation types, circuit breakers, VI, trading suspension.
- FIX order-state model: new, pending cancel, partial/fill, cancel reject, canceled, rejected/failed.
- QuantConnect/LEAN documentation: equities, futures, options, crypto/forex-style multi-asset thinking; order types; scheduled events; risk/portfolio/reality modeling.
- Autofolio current scope: KIS domestic cash stock/ETF style order flow with `LIMIT` and `MARKET`, mock/paper first, kill switch, whitelist, L0-L4 autonomy, amount limits, circuit breaker.

## Current Automated Coverage

| Family | Count | Stored In | Notes |
|--------|------:|-----------|-------|
| Supported asset x side x order type x size matrix | 96 | `test_quant_trading_scenario_catalog.py` | stock cheap/mid/high, equity ETF, bond ETF proxy, commodity ETN proxy |
| Repeated buy/sell churn | 1 scenario, 24 order/execution events | `test_quant_trading_scenario_catalog.py` | buy 100 then sell 100 repeated 12 cycles |
| Multi-asset rebalance basket proxy | 1 scenario, 3 legs | `test_quant_trading_scenario_catalog.py` | three active conditions processed in one tick |
| Order lifecycle terminal states | 3 | `test_quant_trading_scenario_catalog.py` | cancel reject disables auto; market pending then canceled/failed recorded |
| Timer entry | 1 | `test_quant_trading_scenario_catalog.py` | `run_paper_engine --dry-run --once --interval 1` processes a condition |
| Existing paper scenario matrix | 16 | `test_paper_scenario_matrix.py` | kill switch, auto off, L1, whitelist, amount limits, fallback, circuit breaker, UI reflection |

Minimum current executable breadth: 118+ scenario assertions/events without live KIS orders.

## Case Families To Keep

| ID Prefix | Area | Cases To Generate/Keep | Current Status |
|-----------|------|------------------------|----------------|
| QT-ASSET | Asset class | KRX stock, ETF, bond ETF proxy, ETN/commodity proxy, REIT/ELW proxy, bond, futures, options, FX futures, overseas equity | first four executable; others catalog-only until broker/risk support |
| QT-PRICE | Price band | <1,000; 1,000-5,000; 5,000-10,000; 10,000-50,000; 50,000-100,000; 100,000-500,000; >500,000 | executable via mock price bands |
| QT-SIZE | Quantity | 1 share, small lot, large lot, very large lot, block/basket-sized notional | executable except actual block/basket venue |
| QT-SIDE | Direction | buy, sell, buy-sell loop, sell-buy loop, rebalance multi-leg | executable for cash-like mock assets |
| QT-ORDER | Order type | market, limit, pending limit cancel, fallback market, stop, stop-limit, trailing stop, MOO/MOC, IOC/FOK, combo, option exercise | market/limit/fallback executable; rest pending model support |
| QT-STATE | Lifecycle | new, pending, filled, partial pending, canceled, cancel reject, rejected/failed, too-late-to-cancel | partially executable; FIX-style partial requires model extension |
| QT-TIME | Timer/session | pre-open, regular, close auction, after-hours, outside window, scheduled rebalance, end-of-day liquidation | dry-run one-shot executable; after-hours is R3/pending |
| QT-RISK | Safety | kill switch, auto off, L0/L1, whitelist, max order, daily amount, loss circuit breaker, disclosure block, halt/VI | most executable; disclosure/halt is UI/system-state only today |
| QT-PORT | Portfolio | equal weight, target weight rebalance, cash shortage, concentration, turnover/churn, tax/fee placeholder | rebalance/churn executable; cash/fee models pending |
| QT-DATA | Data quality | stale price, zero price, negative/NaN price, missing bar, holiday, split/dividend/corporate action | catalog-only unless data model extended |
| QT-STRAT | Strategy patterns | momentum entry, mean reversion entry, take-profit sell, stop-loss sell, DCA, pairs, volatility breakout, calendar rebalance | entry/take-profit style executable; stop-loss needs condition model extension |

## Catalog-Only Red Lines

These are intentionally not automated as live orders yet:

- Real `prod` KIS orders.
- Futures/options/margin/short/overseas order routing.
- After-hours order path.
- Stop/trailing/combo/option exercise order types.
- Actual block/basket venue submission.
- Any test that needs account number, secret, production data, or irreversible state.

## Gap Task Mapping

| Catalog Gap | Task |
|-------------|------|
| After-hours order/session path | `TASK-014` |
| Margin/short order path | `TASK-021` |
| Overseas stock order path | `TASK-022` |
| Direct KRX alternative products: direct bond/REIT/ELW/product-specific ETN | `TASK-026` |
| KRX derivatives: futures/options/FX futures | `TASK-027` |
| Advanced order types: stop/stop-limit/trailing/MOO/MOC/IOC/FOK | `TASK-028` |
| FIX-style partial fill/pending cancel/too-late lifecycle | `TASK-029` |
| Actual block/basket execution model | `TASK-030` |
| Halt/VI/disclosure engine risk gates | `TASK-031` |
| Stale/invalid data, holiday, corporate action gates | `TASK-032` |
| Cash/fee/slippage/concentration portfolio reality model | `TASK-033` |
| Scheduled strategy patterns: DCA/pairs/volatility/calendar/EOD | `TASK-034` |

## Next Expansion Rules

1. When a new broker order type is implemented, add it to `QT-ORDER` and create executable mock tests before paper smoke.
2. When a new asset class is implemented, add an explicit asset gate in risk policy first, then move its `QT-ASSET` rows from catalog-only to executable.
3. When schedule/rebalance logic gains a persistent scheduler, add deterministic clock tests for open, close, holiday, and missed-tick recovery.
4. When partial-fill support exists, add FIX-style partial fill, pending cancel, cancel reject, and too-late-to-cancel tests as first-class lifecycle tests.
