---
type: test-case-catalog
id: MARKET-HOURS-KIS-UI-VERIFICATION
status: active
owner: QA
created: 2026-06-12
created_at: 2026-06-12T12:44:22+09:00
scope: market-hours UI and KIS paper verification
automation:
  - scripts/kis_paper_order_smoke.py
  - scripts/run_paper_engine.py --dry-run --once
related_task: TASK-035
prod_boundary: paper-only; prod trading requires explicit future Owner approval
---

# Market-Hours KIS/UI Verification

이 catalog는 장중에만 의미 있는 UI + KIS paper 검증을 재실행 가능한 체크리스트로
보관한다. 실전 주문은 포함하지 않는다.

## Safety Rules

- `KIS_ENV`는 항상 paper로 해석되어야 한다.
- KIS base URL은 `openapivts` paper endpoint여야 한다.
- paper order smoke는 기본값인 below-market limit buy 1주 + cancel만 사용한다.
- `--market-test`는 별도 명시 승인 전 사용하지 않는다.
- 보고서에는 계좌번호, token, app key, app secret, 현금 금액을 기록하지 않는다.

## Immediate Market-Hours Cases

| ID | Area | Case | Expected |
|----|------|------|----------|
| MH-UI-001 | UI | Streamlit root HTTP health | 200 OK |
| MH-UI-002 | UI backend | holdings, fills, account summary, watchlist | returns summary without exception |
| MH-UI-003 | UI backend | indices, sector, order book, disclosures, intraday chart | returns rows/source summary without exception |
| MH-KIS-001 | KIS read-only | current price for 005930 | price > 0 |
| MH-KIS-002 | KIS read-only | batch prices for 005930/069500/000660 | at least one quote, all valid symbols reported |
| MH-KIS-003 | KIS read-only | intraday chart for 005930 | rows returned during regular session |
| MH-KIS-004 | KIS read-only | index price KOSPI/KOSDAQ/KOSPI200 | values returned or explicit broker message |
| MH-KIS-005 | KIS read-only | sector price | value returned or explicit broker message |
| MH-KIS-006 | KIS read-only | order book snapshot | bid/ask levels returned |
| MH-KIS-007 | KIS read-only | disclosures/news title | list returned, possibly empty |
| MH-KIS-008 | KIS account | positions, today orders, account summary | succeeds without logging sensitive values |
| MH-KIS-009 | KIS WebSocket | current price/order book subscription | events arrive or environment failure is recorded |
| MH-ORDER-001 | KIS paper order | below-market limit place/status/cancel | order accepted then canceled |
| MH-ENGINE-001 | Engine | dry-run one-shot | no prod, exits successfully |

## Market-Hours Soak Cases

| ID | Area | Case | Expected |
|----|------|------|----------|
| MH-SOAK-001 | KIS read-only | repeated current price/batch/index/order book/account summary sampling | all iterations pass without sensitive value logging |
| MH-SOAK-002 | KIS WebSocket | longer current price/order book stream | events continue to arrive or explicit timeout is recorded |
| MH-SOAK-003 | UI backend | repeated holdings/watchlist/indices/order book/intraday render data | all iterations return summaries without exception |
| MH-SOAK-004 | Paper order | multiple symbols below-market limit place/status/cancel | each accepted/canceled, no open-like order remains |
| MH-SOAK-005 | Engine timer | dry-run interval loop before close window | repeated ticks exit cleanly and do not send live orders |

## Boundary Cases

| ID | Area | Case | Trigger |
|----|------|------|---------|
| MH-TIME-001 | Trading window | engine one-shot near configured close window | 15:15-15:20 KST |
| MH-TIME-002 | Trading window | paper order rejection/skip after close | after 15:30 KST |
| MH-TIME-003 | UI | UI still renders after KIS market close | after 15:30 KST |

## Boundary Results

| ID | Result | Evidence |
|----|--------|----------|
| MH-TIME-001 | PASS | 2026-06-12 15:16 KST dry-run one-shot: in_window=True, processed 2, executed 0, errors 0, kill switch blocked |
| MH-TIME-002 | PASS | 2026-06-12 15:53 KST dry-run one-shot: in_window=False, processed 2, executed 0, errors 0, MockBroker dry-run, kill switch blocked |
| MH-TIME-003 | PASS | after-close `analyze_paper_transactions.py` KIS available true/open-like 0/UI holdings 11 and `verify_paper_ui_sync.py` portfolio contains_holdings true |

## Result Recording

- Store run evidence under `agents/research_agent/notes/EVIDENCE-YYYY-MM-DD-NNN-*.md`.
- Link the evidence from TASK-035 and the relevant BRIEF.
- Any WebSocket or KIS error must be classified before fixing:
  - upstream `agent_runtime` if stack/scope matches AGENTS §17.
  - Autofolio local if it is in `app/`, `scripts/`, or local docs.
  - external/environment if KIS rejects due session, permission, network, market phase, or account capability.
