---
type: evidence
id: EVIDENCE-2026-06-13-005
status: 완료
author: Research Agent + Lead Engineer + QA (Codex)
created: 2026-06-13
created_at: 2026-06-13T01:24:07+09:00
tags: [research, asset-universe, crypto, commodities, fx, real-estate, copyright, approval-record]
scope: multi-asset universe feasibility and approve/reject record for Autofolio
related_task: TASK-042
related_catalog: ASSET-UNIVERSE-DECISION-RECORD
prod_boundary: no product code, broker order path, custody, withdrawal, money movement, risk policy, DB schema, secret, or prod behavior changed
---

# Asset Universe Decision Research

## Question

개인 트레이더, 코인, 금, 은, 오일, 달러 환매/환전, 부동산, 저작권/음원 지분 등
여러 금융 자산과 상품 옵션을 Autofolio에 녹여낼 수 있는지 조사하고, 승인/기각
기록으로 남긴다.

## Source Basket

| Source | Evidence Used |
|--------|---------------|
| Korea Act on the Protection of Virtual Asset Users / FSC release | virtual asset definition, VASP custody/segregation, abnormal transaction monitoring, unfair-trade supervision |
| CFTC virtual currency advisory | crypto derivatives should use registered firms; cash crypto markets can be unregulated; wallet/platform fraud and loss risks |
| KRX market pages | KRX has equity products, bonds, gold market, petroleum market, emissions market, derivatives, USD futures/options, gold futures |
| KRX Korean stock market guide | Korean listed market sessions, alternative products, futures/options, block/basket, short-selling and market-suspension context |
| FINRA futures/commodities | commodities can be accessed by physical goods, futures, mutual funds, ETPs; physical delivery/storage and leveraged/inverse risks |
| CME Gold/Silver/WTI/FX pages | gold, silver, crude oil, FX futures/options are real tradable product families with margin/leverage and settlement implications |
| Bank of Korea FX system | KRW/USD basic exchange rate and customer rate reference model |
| FINRA options pages and Regulatory Notice 21-15 | options are complex, require brokerage approval and due diligence; account information and approval level matter |
| SEC Investor.gov REITs | REITs are a public securities path for real estate exposure; non-traded REITs carry liquidity/value transparency risks |
| FSC fractional investment / security-token releases | fractional real-estate, music-copyright and other rights are securities-style products requiring licensing, disclosure and investor protection |

Source URLs:

- https://www.fsc.go.kr/eng/pr010101/81217
- https://elaw.klri.re.kr/eng_mobile/viewer.do?hseq=63752&key=23&type=part
- https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/understand_risks_of_virtual_currency.html
- https://global.krx.co.kr/contents/GLB/02/0205/0205020203/GLB0205020203.jsp
- https://global.krx.co.kr/contents/GLB/02/0201/0201040901/GLB0201040901.jsp
- https://global.krx.co.kr/contents/GLB/01/0109/0109000000/guide_to_trading_in_the_korean_stock_market.pdf
- https://www.finra.org/investors/investing/investment-products/futures-and-commodities
- https://www.cmegroup.com/markets/metals/precious/gold.html
- https://www.cmegroup.com/markets/metals/precious/silver.html
- https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.html
- https://www.cmegroup.com/markets/fx.html
- https://www.bok.or.kr/eng/main/contents.do?menuNo=400186
- https://www.finra.org/investors/investing/investment-products/options
- https://www.finra.org/rules-guidance/notices/21-15
- https://www.investor.gov/introduction-investing/investing-basics/investment-products/real-estate-investment-trusts-reits
- https://www.fsc.go.kr/eng/pr010101/85243
- https://www.fsc.go.kr/eng/pr010101/79431

## Decision Vocabulary

| Decision | Meaning |
|----------|---------|
| 승인 | Autofolio에 넣어도 되는 범위. 기본은 read-only, manual, mock/backtest, reporting, capability matrix다. |
| 조건부 승인 | 넣을 수 있지만 공식/라이선스 데이터, read-only credential, explicit product flag, no-order guard가 필요하다. |
| 보류/R3 | 주문, 환전, 출금, custody, 외부 계좌, derivatives/margin, risk policy, DB schema가 걸려 Owner 승인 전 중지한다. |
| 기각 | 현재 MVP와 안전 원칙에 맞지 않아 구현하지 않는다. 다시 열려면 새 Owner 결정과 별도 task가 필요하다. |

## Approval / Rejection Record

| Area | Decision | Approved Scope | Rejected Or Held Scope | Reason |
|------|----------|----------------|------------------------|--------|
| 개인 트레이더 profile | 승인 | 개인 계좌/전략/매매일지/위험성향/asset allocation 목표를 local metadata로 관리 | 타인 신호 자동 추종, copy trading, social feed 기반 자동 주문 | persona and journaling improve reporting; auto-follow creates suitability and order-risk issues |
| 국내 상장 주식/ETF/ETN/REIT/ELW proxy | 승인 | 현재 KIS/KRX read-only + 기존 paper/mock 경로에서 watchlist, portfolio, backtest, reporting | 새 product-specific live order routing | already closest to current broker scope; ELW/ETN risk labels required |
| 해외주식/글로벌 ETF | 조건부 승인 | manual/imported holdings, watchlist, FX valuation, broker capability flag | live overseas order, currency settlement automation | existing TASK-022 covers live order R3 |
| 코인 spot | 조건부 승인 | manual/read-only exchange position import, price watchlist, exposure/risk report, no withdrawal key | auto buy/sell, custody/withdrawal, staking/yield, DeFi, exchange transfer | VASP/custody and fraud/market-supervision risk; wallet keys are secrets |
| 코인 futures/options | 보류/R3 | catalog-only and risk education | live derivatives, leverage, liquidation-sensitive automation | derivatives and virtual-asset leverage require new broker/risk/custody gates |
| 금 | 조건부 승인 | KRX gold/commodity ETP/futures quote tracking, manual holdings, portfolio exposure, no physical delivery | physical vault/delivery, live futures/options, auto KRX gold orders | KRX/CME products exist, but trading/settlement/custody are outside current KIS stock path |
| 은 | 조건부 승인 | CME/ETP/manual exposure tracking and reporting | physical silver delivery, live futures/options | commodity leverage and storage/delivery risk |
| 오일 | 조건부 승인 | ETF/ETN/futures price watchlist, macro exposure, scenario/backtest assumptions | physical oil, live futures/options, leveraged/inverse auto trading | energy futures have storage/supply/roll/leverage risk |
| 달러 현금/환율/환매 | 조건부 승인 | KRW/USD reference rates, USD cash bucket, manual FX cashflow, overseas asset valuation | automatic FX conversion, remittance, fund redemption, FX futures/options execution | money movement and derivatives require external account/R3; read-only valuation is safe |
| KRX USD futures/options / CME FX | 보류/R3 | catalog, risk labels, delayed/historical data research | live futures/options trading, margin automation | derivatives account approval and margin needed |
| 부동산 listed exposure | 조건부 승인 | listed REITs/REIT ETFs/manual real-estate allocation bucket, liquidity labels | private real-estate purchase/sale, loan, rental operation, appraisal automation | public REITs are securities; private property is illiquid/legal/valuation-heavy |
| 부동산 조각투자 | 보류/R3 | licensed-platform catalog and manual position record only | platform execution, automated subscription/redemption/secondary trading | FSC treats fractional investment as securities-style licensed activity |
| 저작권/음원 royalty | 보류/R3 | manual position/royalty cashflow record, licensed-platform catalog, disclosure links | buy/sell automation, royalty collection automation, valuation guarantee | fractional copyright products sit in new securities/OTC regime with licensing constraints |
| 상품 옵션/options generally | 보류/R3 | education, payoff diagrams, scenario simulator, approval-level metadata | live options orders, uncovered writing, 0DTE, margin strategies | FINRA requires options approval/due diligence; options are complex and leveraged |
| leveraged/inverse ETPs | 기각 by default | optional risk education only | auto engine trading, default inclusion in screeners/backtests as normal assets | compounding/leverage risks make default inclusion unsafe |
| physical commodities logistics | 기각 | none, except manual note field if Owner insists | storage, delivery, insurance, warehousing, physical settlement operations | operational domain is not a software trading OS MVP |
| DeFi/P2P/yield/lending products | 기각 | none for MVP | protocol integration, lending, staking, yield farming, private credit | custody, counterparty, smart-contract, legal and liquidity risks exceed scope |

## What Can Be Folded Into Autofolio Safely

1. A universal asset taxonomy: `security`, `crypto`, `commodity`, `fx_cash`, `derivative`,
   `real_estate`, `fractional_right`, `copyright_royalty`, `cash`, `other`.
2. Capability flags per asset: `read_only`, `manual_only`, `mock_only`, `paper_only`,
   `r3_hold`, `unsupported`, `rejected`.
3. Read-only portfolio buckets: quantity, cost basis, valuation source, custody/location,
   liquidity tier, leverage flag, derivative flag, regulatory source, owner note.
4. Data ingestion guardrails: official/licensed source first, manual import fallback,
   no write/withdrawal credentials, no automatic money movement.
5. Reporting views: exposure by asset class, currency, broker/custodian, liquidity,
   derivative/leverage risk, unrealized/realized cashflow, and missing valuation warning.

## What Must Not Be Folded In Without R3 Approval

- Any order submit/modify/cancel path for new asset classes.
- Any external account write credential, withdrawal credential, wallet private key,
  bank transfer, remittance, or FX conversion.
- Any live derivatives/margin/options/futures execution.
- Any private real-estate, copyright, fractional/STO platform execution.
- Any valuation guarantee for illiquid assets.

## Implication

Autofolio can become a multi-asset personal portfolio OS if the first implementation is
metadata/read-only/reporting/capability-first. It should not become a multi-asset execution
engine by default. TASK-041 should absorb this decision record as the asset-universe capability
input; future implementation should add flags and UI/reporting first, not broker execution.

## Uncertainty

- Specific KIS availability for KRX gold, derivatives, FX, overseas and alternative products still
  needs official endpoint-level verification before any live support.
- Fractional investment and security-token rules are still evolving; this record is a
  2026-06-13 research snapshot.
- Private asset valuation for real estate/copyright remains inherently model-dependent and should
  be shown as user-provided, not market-confirmed.
