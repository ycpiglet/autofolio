---
type: evidence
id: EVIDENCE-2026-06-12-001
status: 완료
author: QA + KIS API Engineer (Codex)
created: 2026-06-12
created_at: 2026-06-12T11:13:15+09:00
tags: [qa, ui, kis, paper, validation, bug]
scope: Autofolio 정규장 UI + KIS paper 조회성 검증, 주문 발주 제외
applies_to: [Autofolio host]
---

# EVIDENCE-2026-06-12-001 — Live UI + KIS Paper Validation

## 범위

- 포함: Streamlit UI 기동, HTTP health, UI AppTest 회귀, KIS paper 토큰, KIS paper 조회성 API, UI backend read-only 함수, paper engine dry-run one-shot, 문서 게이트.
- 제외: `kis_paper_order_smoke.py --market-test`, `run_paper_engine.py --once` non-dry-run, UI의 엔진 실행 버튼 클릭, 실전(prod) 주문, HTS/앱 교차확인.
- 이유: TASK-023은 "사람이 paper 주문 실행·HTS/앱 교차확인"을 보류 해제 조건으로 둔다. 이번 세션에서는 외부 주문 발주 없이 조회성/비파괴 검증만 수행했다.

## 실행 환경

| 항목 | 결과 |
|------|------|
| 검증 시각 | 2026-06-12T10:53:39+09:00 ~ 2026-06-12T11:13:15+09:00 |
| 정규장 여부 | KST 09:00~15:30 범위 안 |
| KIS_ENV | paper |
| KIS paper credentials | present로만 확인, 값 미출력 |
| UI URL | http://127.0.0.1:8501 |
| Browser | 내장 Browser는 Windows sandbox `spawn setup refresh`로 실패. 기본 브라우저에 URL 오픈 후 AppTest/HTTP/API로 검증 |

## 검증 결과

| 검증 | 결과 | 증거 |
|------|------|------|
| Streamlit server | PASS | 로그: `URL: http://127.0.0.1:8501`, `Uvicorn server started on 127.0.0.1:8501` |
| HTTP health | PASS | `Invoke-WebRequest http://127.0.0.1:8501/` -> 200 OK |
| UI AppTest smoke | PASS | `pytest tests/unit/test_beta_cycle001_ui_smoke.py tests/unit/test_home_market_indices_view.py tests/unit/test_trade_order_book_view.py tests/unit/test_analysis_intraday_view.py tests/unit/test_history_kis_view.py tests/unit/test_alerts_disclosure_view.py tests/unit/test_portfolio_dividend_view.py -q` -> 8 passed |
| KIS unit/contract regression | PASS | `pytest tests/unit/test_kis_client.py ... tests/unit/test_kis_ws_client.py -q` -> 75 passed |
| KIS paper token | PASS | `python scripts/kis_token_smoke.py --env paper --json` -> status ok, token_len 346 |
| KIS paper read-only API | PARTIAL | 14/15 checks passed; `get_cash_balance()` failed |
| UI backend read-only API | PASS with watch | 13/13 checks returned; KPI cash path falls back to 0 if cash lookup fails |
| Paper engine dry-run | PASS | `python scripts/run_paper_engine.py --dry-run --once` -> 2 conditions processed, 0 executed, kill switch blocked both |
| Docs gate | PASS | `python scripts/check_agent_docs.py` -> 0 errors, 77 warnings |
| Doc health | PASS | `python scripts/doc_health_report.py` -> Status G, findings 0 |

## KIS Paper Read-Only API Detail

| Surface | Result |
|---------|--------|
| current price 005930 | ok, price present |
| batch prices 005930/069500/000660 | ok, 3/3 returned |
| positions | ok, count 3 |
| cash balance | fail, `AttributeError: 'list' object has no attribute 'get'` |
| intraday chart 005930 | ok, rows 5 |
| daily price history 005930 | ok, rows 5 |
| KOSPI index | ok, price present |
| order book 005930 | ok, 10 levels; current_price missing in snapshot |
| fundamental 005930 | ok, PER/PBR/EPS/market_cap keys present |
| dividend 005930 | ok, dividend keys present |
| disclosures 005930 | ok, rows 40, blocked_rows 0 |
| today orders | ok, rows 0 |
| order history 7d | ok, rows 9 |

## UI Backend Detail

| Surface | Result |
|---------|--------|
| env | paper |
| whitelist | ok, rows 3 |
| kpis | ok, expected keys returned |
| holdings_df | ok, rows 3 |
| watchlist | ok, 3 price values |
| market_indices_df | ok, rows 3 |
| sector_performance_df | ok, rows 9, non_null_prices 9 |
| order_book_snapshot | ok, 10 levels; current_price missing |
| disclosures_df | ok, rows 40 |
| intraday_chart_df | ok, rows 30 |
| kis_today_orders | ok, rows 0 |
| kis_order_history_7d | ok, rows 9 |
| account_summary | ok, source `estimated` |

## Bugs / Issues

### BUG-2026-06-12-001 — KIS cash balance direct call fails on paper response shape

| 육하원칙 | 내용 |
|----------|------|
| 누가 | KIS paper read-only validation |
| 무엇을 | `KisClient.get_cash_balance()` 호출 |
| 언제 | 2026-06-12T11:xx+09:00, 정규장 |
| 어디서 | `app/brokers/kis/kis_client.py:1064-1077` |
| 왜 | `_request(... _PATH_BALANCE ...)`의 `output2`가 list인 응답에서 `.get("dnca_tot_amt")`를 호출해 AttributeError 발생 |
| 어떻게 | direct call -> `data.get("output2", {}).get(...)` -> `'list' object has no attribute 'get'` |

Severity: Medium. UI `backend.kpis()`는 예외를 잡고 cash=0으로 폴백하므로 화면 전체는 죽지 않지만 현금비중/총자산이 부정확해질 수 있다.

### BUG-2026-06-12-002 — QA E2E reference path missing

| 육하원칙 | 내용 |
|----------|------|
| 누가 | QA start protocol |
| 무엇을 | `agents/qa/references/e2e.md` 로드 |
| 언제 | 2026-06-12 검증 준비 중 |
| 어디서 | `agents/qa/SKILL.md:15-16`, `agents/qa/SKILL.md:94` |
| 왜 | SKILL.md는 E2E/스크린샷 지침 파일을 참조하지만 해당 파일이 repo에 없음 |
| 어떻게 | `Get-Content -Raw -LiteralPath agents\qa\references\e2e.md` -> file not found |

Severity: Low/Medium. 검증은 AppTest/HTTP/API로 대체했지만, 시각 증거 수집 표준이 비어 있다.

### BUG-2026-06-12-003 — Upstream issue warning script referenced but missing

| 육하원칙 | 내용 |
|----------|------|
| 누가 | AGENTS.md §17 SessionStart warning rule |
| 무엇을 | `python scripts/check_upstream_issues.py --warn` 실행 |
| 언제 | 2026-06-12 검증 중 |
| 어디서 | `AGENTS.md:398` |
| 왜 | AGENTS.md가 script를 canonical check로 지시하지만 `scripts/check_upstream_issues.py`가 repo에 없음 |
| 어떻게 | Python 실행 -> `[Errno 2] No such file or directory` |

Severity: Low/Medium. upstream bug reporting 규칙 자체는 있으나 세션 시작 경고 자동화가 실제로 동작하지 않는다.

## 해결 및 후속 검증

시각: 2026-06-12T11:30:06+09:00

| Issue | 판정 | 조치 | 검증 |
|-------|------|------|------|
| BUG-2026-06-12-001 | Autofolio local KIS/UI bug | `KisClient.get_cash_balance()`가 `output2` dict/list 양쪽을 처리하도록 정규화하고, `get_account_summary()`와 UI `account_summary()`를 KIS 요약 소스로 연결 | `pytest tests/unit/test_kis_client_cash.py tests/unit/test_backend_kpis.py scripts/test_check_upstream_issues.py -q` -> 21 passed; live KIS paper smoke에서 numeric cash balance와 `source=kis` account summary 반환 |
| BUG-2026-06-12-002 | agent_runtime template origin | upstream template에도 `agents/qa/SKILL.md`가 `references/e2e.md`를 참조하지만 파일이 없음을 확인. 기존 agent_runtime Issue #19에 Autofolio 재현 코멘트 추가. Autofolio에는 로컬 QA E2E reference 작성 | GitHub comment id `4686771665`; `python scripts/check_agent_docs.py` 재검증 예정 |
| BUG-2026-06-12-003 | Autofolio local overlay bug | `scripts/check_upstream_issues.py`를 추가해 evidence/AUDIT/.remember의 미보고 upstream 신호를 session-start에서 경고하도록 구현 | `python scripts/check_upstream_issues.py --warn` -> OK: no unreported upstream bug signals |

추가 정적 검증:

- `python -m py_compile app\brokers\kis\kis_client.py app\ui\backend.py scripts\check_upstream_issues.py` — passed

최종 회귀 검증(2026-06-12T11:35:48+09:00):

- `pytest tests/unit/test_kis_client_cash.py tests/unit/test_backend_kpis.py scripts/test_check_upstream_issues.py -q` — 21 passed
- `pytest tests/unit -k kis -q` — 116 passed, 255 deselected
- `pytest tests/unit -k "backend or view or beta_cycle001" -q` — 37 passed, 334 deselected
- live KIS paper read-only smoke — `cash_numeric=true`, `summary_source=kis`, `has_raw=false`
- `python -m py_compile app\brokers\kis\kis_client.py app\ui\backend.py scripts\check_upstream_issues.py` — passed
- `python scripts/check_upstream_issues.py --warn` — OK
- `python scripts/check_agent_docs.py` — 0 errors, 74 warnings
- `python scripts/doc_health_report.py` — Status G, findings 0
- `python scripts/generate_views.py --check` — OK
- `python scripts/validate_task_schema.py` — OK
- `python scripts/query_reports.py --kind BRIEF` — BRIEF-2026-06-12-001 listed
- `git diff --check` — no whitespace errors; CRLF conversion warnings only

## Owner-Approved Paper Order E2E

시각: 2026-06-12T11:41:17+09:00 ~ 2026-06-12T11:53:44+09:00

승인: Owner가 "전부 진행 승인"을 명시해 TASK-023 paper 주문 E2E의 R3 실행 게이트를 해제했다. 범위는 KIS paper 계좌 주문 테스트이며 prod 실전 주문 전환은 포함하지 않았다.

### BUG-2026-06-12-004 — paper smoke limit price outside KIS daily band

| 육하원칙 | 내용 |
|----------|------|
| 누가 | KIS paper order lifecycle smoke |
| 무엇을 | `python scripts/kis_paper_order_smoke.py --symbol 005930 --qty 1` |
| 언제 | 2026-06-12T11:41+09:00 |
| 어디서 | `scripts/kis_paper_order_smoke.py` |
| 왜 | 미체결 의도 가격을 현재가의 50%로 계산해 KIS 일일 상/하한가 범위를 벗어남 |
| 어떻게 | KIS가 `40270000 모의투자 상/하한가 오류`로 주문 접수 거부 |

조치: 현재가의 90%를 KRX 호가단위로 내림한 유효 지정가를 사용하도록 smoke 가격 계산을 수정했다.

검증:

- `python -m py_compile scripts\kis_paper_order_smoke.py` — passed
- `pytest tests/unit/test_kis_paper_order_smoke.py tests/unit/test_run_paper_engine_once.py tests/unit/test_kis_client_cash.py tests/unit/test_backend_kpis.py scripts/test_check_upstream_issues.py -q` — 25 passed

### Paper order lifecycle smoke

Command:

```powershell
python scripts/kis_paper_order_smoke.py --symbol 005930 --qty 1
```

Result:

- paper endpoint hard guard passed.
- limit BUY 005930 1 share at valid below-market price was accepted as `PENDING`.
- status check returned `PENDING`, filled quantity 0.
- cancel request returned `CANCELED`.
- script exited 0 with "주문→조회→취소 생애주기 검증 완료".
- Broker order id recorded in terminal output: `0000023016`.

### Engine one-shot paper fill

Controlled setup:

- Existing ACTIVE conditions held temporarily: `[1, 3]`.
- Previous safety state captured: `auto_trading_enabled=false`, `kill_switch_active=true`, `global_mode=L1`.
- Test condition created: `condition_id=4`, symbol `069500`, side `BUY`, quantity `1`, order type `MARKET`, created by `TASK-023-OWNER-APPROVED`.
- Engine safety state temporarily set to `auto_trading_enabled=true`, `kill_switch_active=false`, `global_mode=L2`.

Command:

```powershell
python scripts/run_paper_engine.py --once
```

Result:

- one paper engine tick processed 1 condition.
- condition 4 executed true with message `Pending order filled.`
- engine summary: processed 1, executed 1, errors 0.
- restored state after run: `auto_trading_enabled=false`, `kill_switch_active=true`, `global_mode=L1`.
- restored existing conditions `[1, 3]` to `ACTIVE`.

SQLite verification:

- `order_logs.id=2`, `condition_id=4`, symbol `069500`, side `BUY`, order type `MARKET`, quantity `1`, KIS order id `0000023154`, status `FILLED`.
- `execution_logs.id=2`, `order_log_id=2`, symbol `069500`, filled quantity `1`, raw status `Order filled.`

KIS/UI verification:

- KIS paper `get_positions()` returned `069500` position present.
- UI backend `holdings_df()` returned `069500` portfolio row present.
- UI backend `recent_fills(5)` contains `069500`.
- UI backend `account_summary()` returned `source=kis`.
- Streamlit HTTP health after order: `http://127.0.0.1:8501/` -> 200 OK.
- Final safety state: `auto_trading_enabled=false`, `kill_switch_active=true`, `global_mode=L1`; test condition 4 status `TRIGGERED`.
- Final gates: focused pytest 25 passed; KIS selector 118 passed; UI/backend selector 37 passed; `check_agent_docs.py` 0 errors; `doc_health_report.py` Status G; task views/schema/report query OK; `git diff --check` no whitespace errors.

HTS/app note:

- The agent environment cannot visually inspect the Owner's KIS HTS/mobile app session.
- Broker-side cross-check was performed with KIS paper API order status, execution log, and live positions instead.

## TASK-023 판단

- 이번 검증으로 UI/KIS 조회성 경로와 dry-run 안전 게이트는 확인됐다.
- Owner 승인 후 paper 주문 생애주기와 엔진 1회 체결 E2E를 완료했다.
- `paper 계좌 1주 체결`, `SQLite 체결 로그`, `UI 포트폴리오 반영` 기준은 충족했다.
- HTS/앱 화면은 직접 볼 수 없어 KIS paper API 잔고/체결조회로 broker-side 교차확인했다.
- TASK-023은 paper E2E 소프트웨어 경로 기준 완료로 판단한다. prod 실전 주문 전환은 별도 R3 승인 범위다.
