---
type: evidence
id: EVIDENCE-2026-06-18-005
title: Tomorrow KIS minimal smoke scripts
created_at: 2026-06-18T15:05:34+09:00
owner: QA
related_task: TASK-081
tags: [kis, paper, prod, live-smoke, tomorrow-runbook]
status: pass
redaction: no raw account number, token, secret, cash amount, full order id, or broker payload recorded
---

# Tomorrow KIS minimal smoke scripts

## What Changed

Added:

- `scripts/kis_minimal_order_smoke.py`
- `scripts/kis_paper_minimal_live_smoke.py`
- `scripts/kis_prod_minimal_live_smoke.py`
- `tests/unit/test_kis_minimal_order_smoke.py`

Updated:

- `README.md`
- `agents/project/NEXT-SESSION-POINTER.yml`

## Safety Contract

| Contract | State |
|----------|-------|
| paper/prod entrypoints are env-locked | pass |
| prod execution requires `--execute` plus `--i-understand-this-places-real-orders` | pass |
| prod execution requires same-day paper pass by default | pass |
| blocked/dry-run paper results do not update latest paper evidence | pass |
| `.autofolio/kis_smoke/latest_paper.json` is gitignored local state | pass |
| raw account, token, secret, cash amount, full order id excluded from output | pass |

## Tomorrow Commands

Run these on 2026-06-19 KST after the regular session opens.

Paper first:

```powershell
.venv\Scripts\python.exe scripts\kis_paper_minimal_live_smoke.py --expected-date 2026-06-19 --execute --request-timeout 15 --max-retries 1
```

If paper passes, it writes `.autofolio/kis_smoke/latest_paper.json`.

Prod read-only plan:

```powershell
.venv\Scripts\python.exe scripts\kis_prod_minimal_live_smoke.py --expected-date 2026-06-19
```

Prod minimal live smoke:

```powershell
.venv\Scripts\python.exe scripts\kis_prod_minimal_live_smoke.py --expected-date 2026-06-19 --execute --i-understand-this-places-real-orders
```

## Runtime Behavior

The runner:

1. checks KST date and regular-session window;
2. resolves the correct KIS environment and endpoint;
3. selects a whitelisted low-notional candidate;
4. checks current price, order book, and buying power shape;
5. when `--execute` is present, places market buy, polls status, sells filled/delta quantity, places below-market limit buy, cancels it, then confirms open-like count;
6. prints and stores redacted JSON.

Default caps:

- max quantity: 5 shares;
- max notional estimate: 5,000 KRW;
- min order-book levels: 5;
- regular session guard: 09:00-15:20 KST.

## Verification

| Command | Result |
|---------|--------|
| `.venv\Scripts\python.exe -m pytest tests\unit\test_kis_minimal_order_smoke.py -q` | 7 passed |
| `.venv\Scripts\python.exe -m py_compile scripts\kis_minimal_order_smoke.py scripts\kis_paper_minimal_live_smoke.py scripts\kis_prod_minimal_live_smoke.py tests\unit\test_kis_minimal_order_smoke.py` | pass |
| `scripts\kis_paper_minimal_live_smoke.py --help` | pass |
| `scripts\kis_prod_minimal_live_smoke.py --help` | pass |
| prod read-only dry-run with no paper evidence requirement | dry-run pass, selected `004870`, no order |
| paper read-only dry-run after 15:00 with short timeout | blocked by paper endpoint timeouts, no latest paper promotion |

## Watch

The KIS paper endpoint was timing out after 15:00 on 2026-06-18. Tomorrow's first step must be paper execution. If it blocks again, do not run prod live smoke until paper pass evidence exists.
