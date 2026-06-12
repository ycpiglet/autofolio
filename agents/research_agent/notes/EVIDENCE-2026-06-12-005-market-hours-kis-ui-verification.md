---
type: evidence
id: EVIDENCE-2026-06-12-005
status: 완료
author: QA + KIS API Engineer + UI/UX Designer (Codex)
created: 2026-06-12
created_at: 2026-06-12T12:56:47+09:00
tags: [qa, kis, ui, paper, market-hours, verification]
scope: market-hours UI and KIS paper verification
applies_to: [Autofolio host]
related_task: TASK-035
---

# EVIDENCE-2026-06-12-005 — Market-Hours KIS/UI Verification

## Safety Boundary

- Environment stayed `paper`.
- KIS base URL was verified as paper endpoint (`openapivts`).
- No prod trading, no prod environment switch, no secrets recorded.
- The paper order smoke used the default below-market limit order + cancel path.

## Results

| Area | Result | Evidence |
|------|--------|----------|
| UI HTTP health | PASS | `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8501/` returned 200 |
| UI browser open | PASS | `Start-Process http://127.0.0.1:8501/` succeeded after GUI escalation |
| KIS paper read-only | PASS | 12/12 checks passed after using actual return fields |
| UI backend read-only | PASS | 10/10 checks passed after using actual `intraday_chart_df(time_unit=...)` signature |
| KIS WebSocket smoke | PASS | 3 events received: system, system, realtime quote |
| Paper order lifecycle | PASS | 005930 below-market limit buy 1 share accepted, status read, canceled; filled quantity 0 |
| Engine dry-run one-shot | PASS | processed 2, executed 0, errors 0; kill switch blocked both conditions |
| UI/KIS automated regression | PASS | 84 passed |
| Generated scenario regression | PASS | 119 passed |
| Post-order open-like check | PASS | KIS paper today orders summary returned open-like count 0 |
| Read-only/UI soak | PASS | 3/3 iterations passed |
| WebSocket longer smoke | PASS | 25 events received |
| Multi-symbol paper limit-cancel | PASS | 069500 and 000660 accepted/status/canceled, 0 filled |
| Engine dry-run repeated ticks | PASS | controlled timer loop reached 3 run ends; clean one-shot repeated 3/3 |
| Close-window check | PASS | 2026-06-12 15:16 KST dry-run one-shot: in_window=True, processed 2, executed 0, errors 0 |
| After-close engine check | PASS | 2026-06-12 15:53 KST dry-run one-shot: in_window=False, processed 2, executed 0, errors 0 |
| After-close UI/KIS sync | PASS | KIS available true, open-like 0, UI holdings 11, portfolio contains_holdings true |

## KIS Paper Read-Only Summary

Checked functions:

- `get_current_price("005930")`
- `get_prices_batch(["005930", "069500", "000660"])`
- `get_intraday_chart("005930", count=3)`
- `get_index_price("0001")`
- `get_sector_price("KOSPI_ELECTRONICS")`
- `get_order_book("005930")`
- `get_disclosures("005930", days=1)`
- `get_dividend_info("005930")`
- `get_fundamental("005930")`
- `get_positions()`
- `get_today_orders()`
- `get_account_summary()`

Result:

- 12/12 passed.
- Notable row counts: batch prices 3, intraday rows 3, order book levels 10, disclosures 40, positions 3, today orders 3 at first read.
- Account/cash values were not recorded.

## UI Backend Summary

Checked functions:

- `holdings_df()`
- `recent_fills()`
- `account_summary()`
- `watchlist()`
- `market_indices_df()`
- `sector_performance_df()`
- `order_book_df("005930")`
- `disclosures_df("005930", days=1)`
- `intraday_chart_df("005930", time_unit="1", count=3)`
- `kis_today_orders()`

Result:

- 10/10 passed.
- Representative rows: holdings 3, recent fills 2, watchlist 3, indices 3, sectors 9, order book 10, disclosures 40, intraday 3, today orders 3.

## Commands

- `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8501/` — HTTP 200
- `Start-Process http://127.0.0.1:8501/` — browser open succeeded
- KIS paper read-only summary script — 12/12 passed
- UI backend read-only summary script — 10/10 passed
- KIS paper WebSocket smoke script — 3 events received
- `python scripts/kis_paper_order_smoke.py --symbol 005930 --qty 1` — OK, accepted/status/canceled
- `python scripts/run_paper_engine.py --dry-run --once` — processed 2, executed 0, errors 0
- `pytest tests/unit/test_home_market_indices_view.py tests/unit/test_trade_order_book_view.py tests/unit/test_analysis_intraday_view.py tests/unit/test_alerts_disclosure_view.py tests/unit/test_portfolio_dividend_view.py tests/unit/test_history_kis_view.py tests/unit/test_backend_market_indices.py tests/unit/test_backend_order_book.py tests/unit/test_backend_disclosures.py tests/unit/test_backend_fundamental.py tests/unit/test_backend_watchlist.py tests/unit/test_backend_holdings.py tests/unit/test_backend_kpis.py tests/unit/test_kis_index_price.py tests/unit/test_kis_sector_price.py tests/unit/test_kis_order_book.py tests/unit/test_kis_disclosures.py tests/unit/test_kis_dividend_info.py tests/unit/test_kis_fundamental.py tests/unit/test_kis_batch_price.py tests/unit/test_kis_intraday.py tests/unit/test_kis_ws_client.py tests/unit/test_run_paper_engine_once.py -q` — 84 passed
- `pytest tests/integration/test_quant_trading_scenario_catalog.py tests/integration/test_paper_scenario_matrix.py -q` — 119 passed
- KIS paper post-order today-orders summary — open-like count 0

## 13:09 KST Soak Addendum

Owner asked whether there was nothing useful to do before close. The answer is yes:
market-hours soak verification was added and executed under TASK-035 without changing
prod state.

Additional cases:

- `MH-SOAK-001`: KIS paper read-only repeated sampling.
- `MH-SOAK-002`: KIS paper WebSocket longer smoke.
- `MH-SOAK-003`: UI backend repeated read-only summaries.
- `MH-SOAK-004`: multiple-symbol paper limit-cancel smoke.
- `MH-SOAK-005`: engine dry-run repeated ticks.

Additional results:

- KIS read-only + UI backend soak: 3/3 iterations passed.
  - Each iteration checked current price, batch prices, KOSPI index, order book,
    account summary source, UI watchlist, UI indices, UI order book, and UI intraday rows.
- KIS WebSocket longer smoke:
  - 25 events received.
  - Event types: 3 system messages, 10 realtime quotes, 12 realtime trades.
- Multi-symbol paper limit-cancel:
  - `069500` accepted/status/canceled, filled quantity 0.
  - `000660` accepted/status/canceled, filled quantity 0.
  - Post-check: today order count 9, open-like count 0.
- Engine dry-run timer:
  - Controlled interval process reached 3 run markers and 3 `engine_run_end` records with no live paper order sent; process return code was nonzero because the test intentionally terminated the loop after observation.
  - Clean-exit confirmation: `python scripts/run_paper_engine.py --dry-run --once` repeated 3 times, all exited 0.

## Classification

- No Autofolio bug found in this run.
- No `agent_runtime` upstream bug found in this run.
- The in-app browser automation bootstrap failed with a local tool sandbox error; this is outside Autofolio and did not block UI verification because the Windows browser open and HTTP health path passed.

## Boundary Addendum

Close-window:

- Time: 2026-06-12 15:16 KST.
- Command: `python scripts/run_paper_engine.py --dry-run --once`.
- Result: `in_window=True`, processed 2, executed 0, errors 0.
- Both candidate conditions were rejected by kill switch.

After-close:

- Time: 2026-06-12 15:53 KST.
- Command: `python scripts/run_paper_engine.py --dry-run --once`.
- Result: `in_window=False`, processed 2, executed 0, errors 0.
- Dry-run intentionally still exercises `engine.run_once()` while using `MockBrokerClient`; no paper/prod order was sent.
- Both candidate conditions were rejected by kill switch.

After-close analysis:

- Command: `python scripts/analyze_paper_transactions.py --kis-retries 5 --kis-retry-sleep 3`.
- Result: KIS available true, paper_only true, no_open_like true.
- DB: order rows 34, execution rows 22, statuses `FILLED=22`, `CANCELED=12`.
- KIS: today order rows 53, open-like count 0, warnings 0.
- UI: holdings rows 11, order logs 34, recent fills 20.

After-close UI render:

- Command: `python scripts/verify_paper_ui_sync.py`.
- Result: ok true.
- Portfolio: `contains_holdings=true`; metrics include `평가금액 합`, `총 매입금액`, `총수익률`, `보유 종목`.
- Browser verification on `http://127.0.0.1:8502/portfolio` also showed live caption, holdings section, totals, PnL, return, and 11 holdings.

## Remaining

- None for TASK-035. Prod real-money trading remains out of scope until explicit future Owner approval.
