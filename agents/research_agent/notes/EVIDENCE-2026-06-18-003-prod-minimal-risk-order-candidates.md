---
type: evidence
id: EVIDENCE-2026-06-18-003
title: Prod minimal-risk order test candidates
created_at: 2026-06-18T14:14:57+09:00
owner: Research Agent
related_task: TASK-079
tags: [research, kis, prod-readiness, paper, risk-minimization]
status: pass
redaction: no raw account number, token, secret, cash amount, or broker payload recorded
---

# Prod minimal-risk order test candidates

## Decision

실전 첫 주문 테스트는 국내주식 소수점 매매가 아니라 **국내 KRX 저가 종목 1주**로 설계한다.

이유:

- 한국투자증권 미니스탁 공식 안내의 소수점 서비스는 "미국주식 천원부터"로 설명된다.
- KIS Open API 공식 샘플 repo는 국내주식, ETF/ETN, 해외주식 등 API 카테고리를 분리하며 국내주식은 시세/주문/잔고 카테고리다.
- 국내 Open API 주문 경로는 현재 Autofolio 구현상 정수 수량 1주 테스트가 가장 단순하고 paper/prod 전환 시 동일한 형태를 유지한다.

## Sources Checked

- 한국투자증권 Open API 서비스 안내: Open API는 시세수신, 주문송신, 잔고조회 통신 프로그램이며 실사용 전 모의투자 충분 테스트와 과도한 요청 차단 유의가 필요하다고 안내.
- KIS Developers/Open API portal: 국내주식/ETF/ETN 등 API 문서와 공지 확인.
- 한국투자증권 미니스탁 안내: 소수점 투자 천원부터 미국주식으로 안내.
- KIS official sample repo: `domestic_stock` and `etfetn` API categories 확인.
- 호가단위 자료: 2,000원 미만 국내 주식 호가단위 1원, ETF/ETN 호가단위 5원 유지 자료 확인.

## KIS Read-only Live Check

Checked at 2026-06-18T14:14:57+09:00 KST during regular session. Prices are snapshots and must be refreshed before any real order.

| Code | Name | Type | Paper price | Prod price | Paper/prod order book | Paper buying-power shape | Candidate |
|------|------|------|-------------|------------|------------------------|--------------------------|-----------|
| 006490 | 인스코비 | common | 292 | 292 | pass/pass | pass | Primary |
| 000040 | KR모터스 | common | 333 | 326 | pass/pass | pass | Primary |
| 004870 | 티웨이홀딩스 | common | 404 | 401 | pass/pass | pass | Primary |
| 001210 | 금호전기 | common | 512 | 509 | pass/pass | pass | Primary |
| 001520 | 동양 | common | 561 | 561 | pass/pass | pass | Primary |
| 015260 | 에이엔피 | common | 591 | 591 | pass/pass | pass | Primary |
| 027970 | 한국제지 | common | 604 | 604 | pass/pass | pass | Primary |
| 357430 | 마스턴프리미어리츠 | REIT | 651 | 651 | pass/pass | pass | Secondary |
| 093240 | 형지엘리트 | common | 674 | 674 | pass/pass | pass | Primary |
| 145270 | 케이탑리츠 | REIT | 772 | 772 | pass/pass | pass | Secondary |
| 014160 | 대영포장 | common | 804 | 804 | pass/pass | pass | Primary |
| 011000 | 진원생명과학 | common | 849 | 844 | pass/pass | pass | Primary |
| 090080 | 평화산업 | common | 870 | 870 | pass/pass | pass | Primary |
| 114800 | KODEX 인버스 | plain inverse ETF | 872 | 871 | pass/pass | pass | Exclude from first live smoke |

## Exclusion Rules

Exclude from the first live smoke:

- Leveraged or 2X inverse ETF/ETN, even if nominal price is tens of KRW.
- ETN/ELW/derivatives-style products.
- 신용, 공매도, 해외/FX, fractional overseas order.
- Extremely stale/illiquid names if order book is thin at test time.
- Any symbol where paper current price, order book, or buying-power shape fails immediately before the test.

`114800 KODEX 인버스` is read-only eligible but excluded from first live smoke because inverse exposure adds product semantics that are unnecessary for an order-path smoke.

## Recommended Test Basket

Primary one-share candidates:

1. `006490 인스코비`: lowest snapshot price among common-stock candidates.
2. `000040 KR모터스`: low nominal price, order book read available.
3. `004870 티웨이홀딩스`: low nominal price, order book read available.
4. `001520 동양`: slightly higher but still below 1,000 KRW snapshot.
5. `014160 대영포장`: below 1,000 KRW snapshot, common stock.

Secondary candidates:

1. `357430 마스턴프리미어리츠`
2. `145270 케이탑리츠`

REITs are acceptable as low-notional order-path smoke backups, but common stocks are simpler for the first test.

## Test Cases

### TC-PAPER-LOW-001: Paper one-share market buy and sell

- Env: paper only.
- Symbol: one primary candidate, refresh price before execution.
- Steps:
  1. Run read-only smoke.
  2. Run paper market buy 1 share.
  3. Poll order status until filled or terminal.
  4. Verify SQLite/order log/UI holdings reflect fill.
  5. Run paper market sell 1 share.
  6. Verify no unexpected open-like order remains.
- Pass:
  - buy order accepted/filled in paper;
  - sell order accepted/filled in paper;
  - KIS today-orders open-like count returns 0;
  - no raw account/token/cash recorded.

### TC-PAPER-LOW-002: Paper below-market limit cancel

- Env: paper only.
- Symbol: one primary candidate.
- Steps:
  1. Use a below-market valid tick limit buy 1 share.
  2. Confirm order accepted and pending.
  3. Cancel.
  4. Confirm direct status or same-ODNO open-like count 0.
- Pass:
  - cancel response is canceled;
  - confirmation shows open-like 0.

### TC-PROD-LOW-RO-001: Prod readiness read-only

- Env: prod read-only.
- Symbol: same candidate selected for live smoke.
- Steps:
  1. `kis_capability_smoke.py --env prod --json`.
  2. Current price, order book, account summary shape, today orders, buying-power shape check.
- Pass:
  - read-only checks pass;
  - no order action occurs.

### TC-PROD-LOW-001: Prod one-share manual buy and immediate sell readiness

- Env: prod.
- Preconditions:
  - Owner explicitly approves prod one-share manual test.
  - Auto-trading remains OFF.
  - Kill switch/risk state is not weakened.
  - Selected symbol current price is still low and order book is not stale.
  - No leveraged/inverse/ETN/ELW product.
- Steps:
  1. Place manual market buy 1 share.
  2. Poll status.
  3. Verify position exists.
  4. Place manual market sell 1 share.
  5. Poll status and confirm no open-like order remains.
- Max expected notional:
  - About the live price of 1 share plus fees/taxes/slippage. For the primary list, snapshot notional was under 1,000 KRW per share.
- Pass:
  - buy/sell complete;
  - no lingering open-like order;
  - no auto-trading ON;
  - logs/evidence record only redacted counts/statuses.

## Recommended Sequence

1. Pick `006490` if still liquid and below the risk cap at test time.
2. If spread/liquidity looks poor, use `000040`, `004870`, or `001520`.
3. Repeat paper TC-PAPER-LOW-001 and TC-PAPER-LOW-002 with the selected symbol.
4. Run prod read-only TC-PROD-LOW-RO-001.
5. Only after Owner approval, run prod one-share TC-PROD-LOW-001.

## Watch

- Nominal price is not risk quality. Low-priced names can have poor liquidity, large spreads, trading halts, or corporate-action risk.
- Prices can change before the actual test. Refresh immediately before order.
- Domestic fractional trading should not be assumed for Autofolio KIS Open API. Keep the first live smoke to integer 1-share domestic stock.
- Market buy creates immediate fill risk. If the objective is only order/cancel plumbing, use below-market limit cancel in paper first; for prod, the cleanest asset-impacting round trip is explicit buy 1 + sell 1 after approval.
