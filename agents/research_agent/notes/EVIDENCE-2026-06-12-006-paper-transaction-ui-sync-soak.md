---
type: evidence
id: EVIDENCE-2026-06-12-006
status: 완료
author: QA + KIS API Engineer + UI/UX Designer (Codex)
created: 2026-06-12
created_at: 2026-06-12T13:29:42+09:00
tags: [qa, kis, paper, transaction, ui-sync, soak]
scope: KIS paper transaction and UI backend sync soak
applies_to: [Autofolio host]
related_task: TASK-036
---

# EVIDENCE-2026-06-12-006 — Paper Transaction UI Sync Soak

## Safety Boundary

- Environment resolved to `paper`.
- KIS base URL was verified as paper endpoint (`openapivts`).
- No prod trading, no prod environment switch, no secrets recorded.
- Quantity stayed at 1 share.
- Report records do not include account number, token, app key, app secret, or cash amounts.

## Reusable Artifacts

- Runner: `scripts/kis_paper_transaction_soak.py`
- Bounded loop runner: `scripts/kis_paper_transaction_loop.py`
- Buy-and-hold runner: `scripts/kis_paper_hold_basket.py`
- KIS fill reconciliation: `scripts/reconcile_paper_fills.py`
- Unit tests: `tests/unit/test_kis_paper_transaction_soak.py`
- Unit tests: `tests/unit/test_kis_paper_hold_basket.py`
- Unit tests: `tests/unit/test_reconcile_paper_fills.py`
- Unit tests: `tests/unit/test_top_bar_data_source.py`
- QA catalog: `agents/qa/test_cases/PAPER-TRANSACTION-UI-SYNC-SOAK.md`
- Related TASK: `agents/lead_engineer/tasks/TASK-036-paper-transaction-ui-sync-soak.md`

## Transaction Result

Command:

- `python scripts/kis_paper_transaction_soak.py`

Result:

- `ok=true`
- `env=paper`
- `paper_endpoint=true`
- filled market round-trip:
  - `069500` BUY MARKET 1 share: `FILLED`, order_log_id `3`, execution_log_id `3`
  - `069500` SELL MARKET 1 share: `FILLED`, order_log_id `4`, execution_log_id `4`
- unfilled/cancel transactions:
  - `005930` BUY LIMIT 1 share: `CANCELED`, order_log_id `5`, no execution log
  - `000660` BUY LIMIT 1 share: `CANCELED`, order_log_id `6`, no execution log
- post-run KIS open-like orders: `0`

Second command:

- `python scripts/kis_paper_transaction_soak.py --fill-symbol 005930 --unfilled-symbols 069500 000660 --qty 1`

Second result:

- `ok=true`
- filled market round-trip:
  - `005930` BUY MARKET 1 share: `FILLED`, order_log_id `7`, execution_log_id `5`
  - `005930` SELL MARKET 1 share: `FILLED`, order_log_id `8`, execution_log_id `6`
- unfilled/cancel transactions:
  - `069500` BUY LIMIT 1 share: `CANCELED`, order_log_id `9`
  - `000660` BUY LIMIT 1 share: `CANCELED`, order_log_id `10`
- post-run KIS open-like orders: `0`

Third command:

- `python scripts/kis_paper_transaction_soak.py --fill-symbol 000660 --unfilled-symbols 005930 069500 --qty 1`

Third result:

- `ok=true`
- filled market round-trip:
  - `000660` BUY MARKET 1 share: `FILLED`, order_log_id `11`, execution_log_id `7`
  - `000660` SELL MARKET 1 share: `FILLED`, order_log_id `12`, execution_log_id `8`
- unfilled/cancel transactions:
  - `005930` BUY LIMIT 1 share: `CANCELED`, order_log_id `13`
  - `069500` BUY LIMIT 1 share: `CANCELED`, order_log_id `14`
- post-run KIS open-like orders: `0`

Fourth command:

- `python scripts/kis_paper_transaction_soak.py --fill-symbol 069500 --unfilled-symbols 005930 000660 --qty 1`

Fourth result:

- `ok=true`
- filled market round-trip:
  - `069500` BUY MARKET 1 share: `FILLED`, order_log_id `15`, execution_log_id `9`
  - `069500` SELL MARKET 1 share: `FILLED`, order_log_id `16`, execution_log_id `10`
- unfilled/cancel transactions:
  - `005930` BUY LIMIT 1 share: `CANCELED`, order_log_id `17`
  - `000660` BUY LIMIT 1 share: `CANCELED`, order_log_id `18`
- post-run KIS open-like orders: `0`

Bounded loop dry-run:

- `python scripts/kis_paper_transaction_loop.py --cycles 3 --interval-sec 0 --dry-run`
- Result: `ok=true`, `env=paper`, `paper_endpoint=true`, 3-cycle rotation planned for `069500`, `005930`, `000660`.

Bounded loop execution:

- `python scripts/kis_paper_transaction_loop.py --cycles 1 --interval-sec 0`
- Result: `ok=true`, `env=paper`, `paper_endpoint=true`, `cycles_completed=1`.
- cycle 1 summary:
  - fill symbol: `069500`
  - filled records: 2
  - canceled records: 2
  - post-run KIS open-like orders: `0`

Second bounded loop execution:

- `python scripts/kis_paper_transaction_loop.py --cycles 1 --interval-sec 0`
- Result: `ok=true`, `env=paper`, `paper_endpoint=true`, `cycles_completed=1`.
- cycle 1 summary:
  - fill symbol: `069500`
  - filled records: 2
  - canceled records: 2
  - post-run KIS open-like orders: `0`

KIS direct analysis timeout hardening:

- Observation: one `python scripts/analyze_paper_transactions.py` run hit a KIS
  `ReadTimeout` while `backend.kis_today_orders()` still returned 45 rows and
  UI sync remained OK.
- Fix: `scripts/analyze_paper_transactions.py` now retries direct
  `get_today_orders()`, records redacted warnings, exposes `kis_available`,
  and exits nonzero if KIS direct remains unavailable.
- Unit tests added for retry success and unavailable failure.

Strict KIS today-orders mode:

- `KisClient.get_today_orders(suppress_errors=False)` was added so verification
  scripts can fail closed instead of treating broker transport errors as empty
  order history.
- UI/backend callers keep the default compatibility behavior.

Buy-and-hold basket command:

- `python scripts/kis_paper_hold_basket.py --symbols 035420 035720 005380 068270 105560 055550 102110 114260 --qty 1 --min-filled 5 --attempts 10 --sleep 1 --pause-between 0.5`

Buy-and-hold result:

- `ok=true`
- `env=paper`
- `paper_endpoint=true`
- holdings rows: 3 -> 11
- filled immediately with local order/execution logs:
  - `035420`, `035720`, `005380`, `068270`, `102110`, `114260`
- visible in holdings/today-orders after polling timeout:
  - `105560`, `055550`
- post-run KIS open-like orders: `0`

Portfolio UI visibility fix:

- Owner observed that the Autofolio UI did not clearly show what was held, how
  much was held, current PnL, and totals.
- Fix:
  - `app/ui/views/portfolio.py` now puts the holdings table on the first screen.
  - Portfolio metrics now include `평가금액 합`, `총 매입금액`, `평가손익`,
    `총수익률`, and `보유 종목`.
  - The holdings table focuses on `종목`, `티커`, `자산군`, `수량`, `평단`,
    `현재가`, `평가금액`, `평가손익`, `손익률`, and `비중`.
  - `app/ui/backend.py` added `holdings_df(include_dividends=False)` so first
    screen holdings/PnL can render without per-symbol dividend API latency.
  - `scripts/verify_paper_ui_sync.py` now recognizes `보유 현황` and portfolio
    metrics as holdings visibility evidence.

Portfolio UI verification:

- `python scripts/verify_paper_ui_sync.py`
- Result: `ok=true`
- portfolio:
  - `contains_holdings=true`
  - dataframes: 2
  - metrics: `평가금액 합`, `총 매입금액`, `총수익률`, `보유 종목`, `예상 연배당`, `배당수익률`
  - exceptions: none

Live top-bar and browser verification:

- Observation: in a guest session, selecting `라이브` data source still showed
  `데모 모드 — mock 데이터` in the top bar.
- Fix:
  - `app/ui/components/ui.py` now labels the top bar from `data_source`.
  - backend mode shows `라이브 데이터 — KIS paper · SQLite`.
  - demo mode keeps `데모 모드 — mock 데이터`.
- Test:
  - `tests/unit/test_top_bar_data_source.py` covers backend/demo captions.
- Local UI server:
  - `http://127.0.0.1:8502` was started with latest code because the existing
    8501 process still had older modules loaded.
  - The Streamlit first-run prompt was passed with blank stdin for this local server.
- Browser result on `http://127.0.0.1:8502/portfolio`:
  - live caption visible.
  - `보유 현황` visible.
  - `평가금액 합`, `총 매입금액`, `평가손익`, `총수익률`, `보유 종목` visible.
  - paper holdings count visible as 11.
- Transient note:
  - One browser attempt hit KIS `RemoteDisconnected` and showed the UI fallback
    warning. Re-running the same browser flow succeeded with KIS paper holdings
    count 11. The concurrent analysis command reported KIS available true and
    warnings 0.

Reconciliation command:

- `python scripts/reconcile_paper_fills.py --symbols 055550 105560`

Reconciliation result:

- `ok=true`
- reconciled count: 2
- reconciled symbols:
  - `055550` BUY MARKET 1 share, order_log_id `33`, execution_log_id `21`
  - `105560` BUY MARKET 1 share, order_log_id `34`, execution_log_id `22`

Close-window verification:

- Time: 2026-06-12 15:16 KST
- Command: `python scripts/run_paper_engine.py --dry-run --once`
- Result:
  - `in_window=True`
  - processed: 2
  - executed: 0
  - errors: 0
  - kill switch rejected both candidate conditions

After-close verification:

- Time: 2026-06-12 15:53 KST
- Command: `python scripts/run_paper_engine.py --dry-run --once`
- Result:
  - `in_window=False`
  - processed: 2
  - executed: 0
  - errors: 0
  - dry-run used `MockBrokerClient`
  - kill switch rejected both candidate conditions

## UI/Backend Sync Summary

Before:

- holdings rows: 3
- recent fills rows: 2
- order log rows: 2
- KIS today orders rows: 9
- order log statuses: `FILLED=2`

After:

- holdings rows: 3
- recent fills rows: 4
- order log rows: 6
- KIS today orders rows: 15
- order log statuses: `FILLED=4`, `CANCELED=2`
- sync checks:
  - filled_ok: true
  - canceled_ok: true
  - ui_sync_ok: true
  - no_open_like: true

After second run:

- holdings rows: 3
- recent fills rows: 6
- order log rows: 10
- order log statuses: `FILLED=6`, `CANCELED=4`
- KIS open-like orders: 0

## KIS Today Orders Pagination Fix

Observation:

- During the second transaction soak, local SQLite/UI sync increased from 6 to 10
  order log rows, but KIS today-orders stayed at 15 rows immediately after the run.
- Code inspection showed `KisClient.get_today_orders()` read only the first
  `inquire-daily-ccld` page, unlike `get_order_history()` which follows
  `tr_cont` and `CTX_AREA_*` pagination.

Fix:

- `app/brokers/kis/kis_client.py`
  - `get_today_orders()` now follows pagination up to `_MAX_HISTORY_PAGES`.
- `tests/unit/test_kis_order_history.py`
  - added `test_get_today_orders_paginates`.

Post-fix live verification:

- direct KIS today orders rows: 21
- backend `kis_today_orders()` rows: 21
- backend order log rows: 10
- backend recent fills rows: 6
- post-open-like count: 0

## Reusable Analysis Summary

Runner:

- `scripts/analyze_paper_transactions.py`

After the buy-and-hold basket and reconciliation:

- checks:
  - paper_only: true
  - ui_reads_order_logs: true
  - ui_reads_recent_fills: true
  - no_open_like: true
- DB:
  - order rows: 34
  - execution rows: 22
  - order statuses: `FILLED=22`, `CANCELED=12`
  - order symbols include `035420`, `035720`, `005380`, `068270`, `105560`, `055550`, `102110`, `114260`
  - order types: `LIMIT=13`, `MARKET=21`
  - filled quantity includes one share each for the buy-and-hold basket symbols
- KIS:
  - today order rows: 53
  - filled row count: 21
  - canceled rows: 16
  - open-like count: 0
  - warnings: 0
- UI:
  - holdings rows: 11
  - KIS today orders rows: 53
  - order log rows: 34
  - recent fills rows: 20

## Reusable UI Sync Script

Runner:

- `scripts/verify_paper_ui_sync.py`

Result after the buy-and-hold basket and reconciliation:

- `ok=true`
- home:
  - no exceptions
  - metrics rendered: KOSPI, KOSDAQ, KOSPI200, total asset cards
  - dataframes: 2
  - recent fills label visible
- portfolio:
  - no exceptions
  - holdings label visible
  - dataframes: 2
- trade:
  - no exceptions
  - order controls visible
  - dataframes: 4

## UI Render Verification

Streamlit AppTest rendered backend mode views after the paper transactions:

| View | Result | Evidence |
|------|--------|----------|
| home | PASS | metrics rendered, 2 dataframes, recent fill label visible |
| portfolio | PASS | holdings label visible, 2 dataframes |
| trade | PASS | order book metrics, 4 dataframes, engine/KIS refresh buttons visible |

Also fixed one UI sync gap:

- `app/ui/views/home.py` now uses `backend.holdings_df()` when `data_source=backend`.
- This prevents demo holdings from hiding post-trade backend sync on the home page.

Also fixed one warning encountered during AppTest:

- `app/ui/views/trade.py` changed KIS today-orders table from deprecated
  `use_container_width=True` to `width="stretch"`.

## Verification Commands

- `python -m py_compile scripts/kis_paper_transaction_soak.py app/ui/views/home.py tests/unit/test_kis_paper_transaction_soak.py tests/unit/test_home_market_indices_view.py` — OK
- `pytest tests/unit/test_kis_paper_transaction_soak.py tests/unit/test_home_market_indices_view.py tests/unit/test_backend_kpis.py tests/unit/test_backend_holdings.py -q` — 21 passed
- `python scripts/kis_paper_transaction_soak.py` — OK
- Streamlit AppTest backend live render for home/portfolio/trade — OK
- `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8501/` — HTTP 200
- `pytest tests/unit/test_kis_paper_transaction_soak.py tests/unit/test_home_market_indices_view.py tests/unit/test_trade_order_book_view.py tests/unit/test_backend_kpis.py tests/unit/test_backend_holdings.py tests/unit/test_run_paper_engine_once.py -q` — 24 passed
- `pytest tests/integration/test_quant_trading_scenario_catalog.py tests/integration/test_paper_scenario_matrix.py -q` — 119 passed
- `pytest tests/unit/test_kis_order_history.py tests/unit/test_kis_paper_transaction_soak.py tests/unit/test_home_market_indices_view.py -q` — 13 passed
- KIS paper post-pagination live summary — direct/backend today orders 21 rows, open-like 0
- `pytest tests/unit/test_verify_paper_ui_sync.py tests/unit/test_analyze_paper_transactions.py tests/unit/test_kis_paper_transaction_soak.py -q` — 6 passed
- `python scripts/kis_paper_transaction_soak.py --fill-symbol 000660 --unfilled-symbols 005930 069500 --qty 1` — OK
- `python scripts/analyze_paper_transactions.py` — OK, redacted summary generated
- `python scripts/verify_paper_ui_sync.py` — OK, home/portfolio/trade backend views rendered
- `python scripts/kis_paper_transaction_soak.py --fill-symbol 069500 --unfilled-symbols 005930 000660 --qty 1` — OK
- `python scripts/analyze_paper_transactions.py` — OK after fourth run, redacted summary generated
- `python scripts/verify_paper_ui_sync.py` — OK after fourth run, home/portfolio/trade backend views rendered
- `python scripts/kis_paper_transaction_loop.py --cycles 3 --interval-sec 0 --dry-run` — OK, no orders
- `pytest tests/unit/test_kis_paper_transaction_loop.py -q` — 6 passed
- `python -m py_compile scripts/kis_paper_transaction_loop.py tests/unit/test_kis_paper_transaction_loop.py` — OK
- `python scripts/kis_paper_transaction_loop.py --cycles 1 --interval-sec 0` — OK
- `python scripts/analyze_paper_transactions.py` — OK after bounded loop, redacted summary generated
- `python scripts/verify_paper_ui_sync.py` — first retry timeout at 124s, second retry OK with 240s timeout
- `python scripts/kis_paper_transaction_loop.py --cycles 1 --interval-sec 0` — OK, second bounded loop
- `pytest tests/unit/test_analyze_paper_transactions.py -q` — 5 passed
- `python -m py_compile scripts/analyze_paper_transactions.py tests/unit/test_analyze_paper_transactions.py` — OK
- `python scripts/analyze_paper_transactions.py --kis-retries 3 --kis-retry-sleep 2` — OK after retry hardening, KIS warnings 0
- `python scripts/verify_paper_ui_sync.py` — OK after second bounded loop
- `pytest tests/unit/test_kis_paper_hold_basket.py tests/unit/test_analyze_paper_transactions.py tests/unit/test_kis_client.py tests/unit/test_kis_order_history.py -q` — 36 passed
- `python scripts/kis_paper_hold_basket.py --symbols 035420 035720 005380 068270 105560 055550 102110 114260 --qty 1 --min-filled 5 --attempts 10 --sleep 1 --pause-between 0.5` — OK
- `pytest tests/unit/test_reconcile_paper_fills.py tests/unit/test_kis_paper_hold_basket.py -q` — 4 passed
- `python scripts/reconcile_paper_fills.py --symbols 055550 105560` — OK
- `python scripts/analyze_paper_transactions.py --kis-retries 5 --kis-retry-sleep 3` — OK, KIS warnings 0
- `python scripts/verify_paper_ui_sync.py 300` — OK after larger holdings, home/portfolio/trade backend views rendered
- `pytest tests/unit/test_backend_holdings.py tests/unit/test_backend_kpis.py tests/unit/test_portfolio_dividend_view.py tests/unit/test_home_market_indices_view.py tests/unit/test_verify_paper_ui_sync.py -q` — 22 passed
- `python -m py_compile app/ui/backend.py app/ui/views/portfolio.py app/ui/views/home.py scripts/verify_paper_ui_sync.py` — OK
- `python scripts/verify_paper_ui_sync.py` — OK, portfolio contains_holdings true
- `python scripts/run_paper_engine.py --dry-run --once` — OK in 15:15-15:20 close-window
- `python scripts/run_paper_engine.py --dry-run --once` — OK after 15:30, `in_window=False`, executed 0
- `pytest tests/unit/test_top_bar_data_source.py -q` — 2 passed
- `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8502/` — HTTP 200
- browser verification on `http://127.0.0.1:8502/portfolio` — live caption and portfolio holdings/totals visible

## Remaining

- None for TASK-036. Further paper transaction loops can be run as a new verification cycle if needed.
- Prod real-money trading remains out of scope until explicit future Owner approval.
