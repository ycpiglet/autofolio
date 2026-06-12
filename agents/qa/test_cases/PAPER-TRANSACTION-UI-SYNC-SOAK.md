---
type: test-case-catalog
id: PAPER-TRANSACTION-UI-SYNC-SOAK
status: active
owner: QA
created: 2026-06-12
created_at: 2026-06-12T13:20:04+09:00
scope: KIS paper transaction and UI backend sync soak
automation:
  - scripts/kis_paper_transaction_soak.py
  - scripts/kis_paper_transaction_loop.py
  - scripts/kis_paper_hold_basket.py
  - scripts/reconcile_paper_fills.py
  - scripts/analyze_paper_transactions.py
  - scripts/verify_paper_ui_sync.py
  - tests/unit/test_kis_paper_transaction_soak.py
  - tests/unit/test_kis_paper_transaction_loop.py
  - tests/unit/test_kis_paper_hold_basket.py
  - tests/unit/test_reconcile_paper_fills.py
  - tests/unit/test_top_bar_data_source.py
related_task: TASK-036
prod_boundary: paper-only; prod trading requires explicit future Owner approval
---

# Paper Transaction UI Sync Soak

이 catalog는 KIS paper 거래 트랜잭션과 UI 동기화를 반복 검증하기 위한 재사용
체크리스트다.

## Safety Rules

- Always resolve `KIS_ENV=paper`.
- KIS base URL must contain `openapivts`.
- Default quantity stays 1 share.
- Do not record account number, app key, app secret, token, or cash amounts.
- Market orders are used only for paper fill round-trip and should be paired
  BUY then SELL.
- Pending tests use below-market limit orders and must cancel.

## Cases

| ID | Area | Case | Expected |
|----|------|------|----------|
| PTX-001 | Guard | non-paper env/base URL | rejected before order |
| PTX-002 | Filled transaction | paper market BUY 1 share | FILLED or recorded failure |
| PTX-003 | Filled transaction | paper market SELL same filled quantity | FILLED when BUY filled |
| PTX-004 | Unfilled transaction | below-market LIMIT BUY | PENDING before cancel |
| PTX-005 | Cancel transaction | cancel pending LIMIT order | CANCELED |
| PTX-006 | DB sync | create `order_logs` rows | rows visible in `backend.list_order_logs()` |
| PTX-007 | DB sync | create `execution_logs` for fills | rows visible in `backend.recent_fills()` |
| PTX-008 | UI sync | home/trade/portfolio backend data access | no exception; backend rows visible |
| PTX-009 | Broker cleanup | post-run open-like orders | zero |
| PTX-010 | Reuse | output is redacted JSON summary | no account/secrets/cash values |
| PTX-011 | Analysis | redacted transaction summary | DB/KIS/UI counts are grouped for reuse |
| PTX-012 | Repetition | run multiple symbol combinations in one market session | counts increase monotonically and open-like remains zero |
| PTX-013 | Timer loop | bounded cycle runner with interval | paper guard, max cycle cap, qty=1, redacted summaries |
| PTX-014 | KIS transient | direct KIS today-orders ReadTimeout | retry; expose `kis_available`; fail if still unavailable |
| PTX-015 | Buy-and-hold | market BUY diversified paper basket and do not sell | holdings rows increase and remain visible in UI |
| PTX-016 | Reconcile | KIS fill visible but status polling timed out | create missing local order/execution logs from today-orders |
| PTX-017 | Portfolio UI | holdings/quantity/PnL/total visible on portfolio first screen | portfolio AppTest sees holdings table and summary metrics |
| PTX-018 | UI mode label | guest session switches data source to backend/live | top bar shows KIS paper/SQLite live caption, not mock caption |
| PTX-019 | Browser UI | latest Streamlit server renders portfolio in live mode | live caption, holdings section, totals, PnL, return, and holdings count visible |

## Reuse Command

```powershell
python scripts/kis_paper_transaction_soak.py
```

Optional:

```powershell
python scripts/kis_paper_transaction_soak.py --fill-symbol 069500 --unfilled-symbols 005930 000660 --qty 1
python scripts/kis_paper_transaction_soak.py --fill-symbol 005930 --unfilled-symbols 069500 000660 --qty 1
python scripts/kis_paper_transaction_soak.py --fill-symbol 000660 --unfilled-symbols 005930 069500 --qty 1
```

Analysis:

```powershell
python scripts/analyze_paper_transactions.py
```

UI sync:

```powershell
python scripts/verify_paper_ui_sync.py
```

Bounded loop dry-run:

```powershell
python scripts/kis_paper_transaction_loop.py --cycles 3 --interval-sec 0 --dry-run
```

Bounded loop execution:

```powershell
python scripts/kis_paper_transaction_loop.py --cycles 1 --interval-sec 0
```

Buy-and-hold basket:

```powershell
python scripts/kis_paper_hold_basket.py --symbols 035420 035720 005380 068270 105560 055550 102110 114260 --qty 1 --min-filled 5
```

Reconcile missed fills:

```powershell
python scripts/reconcile_paper_fills.py --symbols 055550 105560
```
