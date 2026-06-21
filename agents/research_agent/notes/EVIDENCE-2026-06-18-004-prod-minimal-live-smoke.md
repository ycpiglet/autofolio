---
type: evidence
id: EVIDENCE-2026-06-18-004
title: Prod minimal live smoke
created_at: 2026-06-18T14:47:04+09:00
owner: QA
related_task: TASK-080
tags: [kis, prod, live-smoke, order-lifecycle, risk-minimization]
status: pass-with-watch
redaction: no raw account number, token, secret, cash amount, full order id, or broker payload recorded
---

# Prod minimal live smoke

## Boundary

Owner explicitly requested immediate progression after depositing funds. Execution was limited to a technical order-path smoke:

- prod domestic stock only;
- ordinary cash KRX order only;
- no auto-trading enablement;
- no leverage, inverse, ETN/ELW, margin, short, overseas, FX, fractional order;
- candidate whitelist only;
- max 5 shares and estimated notional under 5,000 KRW;
- position-delta cleanup after buy;
- redacted output only.

## Paper Precheck

Paper order/cancel could not be fully completed in the remaining window:

| Symbol | Result |
|--------|--------|
| `006490` | paper limit-buy rejected as not tradable in mock investment |
| `000040` | paper order request timed out |
| `004870` | paper order request timed out |
| fallback sequential scan | command-level timeout before a success record |

Follow-up paper cleanup probe:

- candidate hits: none when the paper today-orders call succeeded after the first timeout set;
- later paper position and today-orders calls timed out again;
- no prod decision used paper hidden state.

Watch: KIS paper server was unstable during this window, so paper order/cancel parity for the selected symbol is not considered verified today.

## Prod Readiness

Prod read-only checks before the live smoke:

| Item | State | Notes |
|------|-------|-------|
| prod endpoint guard | pass | URL resolved to `openapi.koreainvestment.com` |
| account summary shape | pass | summary keys present; cash positive; total positive |
| candidate price/order book | pass | selected symbol had current price and 10 order-book levels |
| buying-power raw fields | pass | `ord_psbl_cash` positive; `max_buy_qty`/`nrcvb_buy_qty` sufficient |
| app `get_buying_power()` | watch then fixed | method read `psbl_qty` only, while live KIS output used `max_buy_qty`/`nrcvb_buy_qty` |

Selected:

| Symbol | Name | Price snapshot | Planned qty | Est. notional | Order-book levels |
|--------|------|----------------|-------------|---------------|-------------------|
| `004870` | 티웨이홀딩스 | 387 | 5 | 1,935 | 10 |

## Prod Live Smoke Result

Redacted live run result:

| Step | State | Evidence |
|------|-------|----------|
| BUY market 5 shares | pass | accepted then FILLED; position delta +5; open-like 0 |
| SELL market 5 shares | pass | accepted then FILLED; final position delta 0; open-like 0 |
| BUY below-market limit 1 share | pass | accepted as pending |
| Cancel limit order | pass | cancel returned CANCELED; open-like 0 |

Redacted order tails observed in command output:

- market buy: `***7700`
- market sell: `***8600`
- limit-cancel order: `***9700`

No full order id, account number, token, secret, cash amount, or raw broker payload is recorded.

## Final Prod Residue Check

Post-check at 2026-06-18T14:44:40+09:00:

| Item | State |
|------|-------|
| selected symbol position quantity | 0 |
| selected symbol today-order open-like count | 0 |
| selected symbol related rows | 4 redacted rows, all open-like false |

## Bug Fixed During Smoke

Issue:

- `KisClient.get_buying_power()` returned `max_quantity=0` because it only parsed `psbl_qty`.
- Live KIS prod `inquire-psbl-order` returned useful quantity in `max_buy_qty` and `nrcvb_buy_qty`.

Patch:

- `app/brokers/kis/kis_client.py`: `max_quantity = max(psbl_qty, max_buy_qty, nrcvb_buy_qty)`.
- `tests/unit/test_kis_buying_power.py`: regression for `max_buy_qty` fallback.

Verification:

```text
.venv\Scripts\python.exe -m pytest tests\unit\test_kis_buying_power.py -q
3 passed
```

Live read-only recheck after patch:

| Item | State |
|------|-------|
| prod `get_buying_power("004870")` max quantity positive | pass |
| prod `get_buying_power("004870")` cash positive | pass |

## Decision

The minimal prod order path is verified for ordinary domestic KRX cash orders:

- prod market buy/sell works;
- prod cancel works;
- redacted status/today-orders reconciliation works;
- no position/order residue remains.

Keep auto-trading OFF until a separate readiness gate covers broader strategy, risk, monitoring, and rollback behavior.
