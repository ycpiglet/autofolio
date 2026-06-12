---
type: task
id: TASK-036
status: 완료
owner: QA
assignees: [QA, KIS API Engineer, UI/UX Designer]
priority: High
difficulty: 중
est_hours: 2
est_tokens: 35000
tags: [qa, kis, paper, transaction, ui-sync, soak]
gate: paper-only; prod 실전 주문 전환 금지
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-12-011
created: 2026-06-12
created_at: 2026-06-12T13:20:04+09:00
updated_at: 2026-06-12T21:34:23+09:00
---

# TASK-036 Paper Transaction UI Sync Soak

작업 ID: TASK-036
상태: 완료
Owner: QA
요청 시각: 2026-06-12T13:12:00+09:00
기록 시각: 2026-06-12T13:20:04+09:00

## 배경 및 목적

Owner 요청은 장중 남은 시간에 paper 거래를 계속 실행하면서 체결/미체결/취소
트랜잭션과 UI 동기화를 검증하고, 후속 재사용/분석/응용 가능한 형태로 남기는 것이다.

## 범위

- 포함:
  - KIS paper market buy/sell round-trip.
  - KIS paper below-market limit order place/status/cancel.
  - SQLite `order_logs`/`execution_logs` 기록.
  - UI backend `recent_fills()`, `list_order_logs()`, `holdings_df()`, `kis_today_orders()` sync check.
  - Streamlit home view backend holdings sync regression.
- 제외:
  - prod 실전 주문.
  - 주문 수량 확대.
  - risk/order path 정책 변경.
  - 계좌번호, token, app key, app secret, 현금 금액 기록.

## 진행 기록

### 2026-06-12T13:20:04+09:00

- 재사용 가능한 paper-only soak runner 추가:
  - `scripts/kis_paper_transaction_soak.py`
- 안전/기본 동작 테스트 추가:
  - `tests/unit/test_kis_paper_transaction_soak.py`
- 홈 화면 backend mode에서 demo holdings가 post-trade sync를 가릴 수 있는 gap 수정:
  - `app/ui/views/home.py`
  - `tests/unit/test_home_market_indices_view.py`
- 검증:
  - `python -m py_compile scripts/kis_paper_transaction_soak.py app/ui/views/home.py tests/unit/test_kis_paper_transaction_soak.py tests/unit/test_home_market_indices_view.py`
  - `pytest tests/unit/test_kis_paper_transaction_soak.py tests/unit/test_home_market_indices_view.py tests/unit/test_backend_kpis.py tests/unit/test_backend_holdings.py -q` — 21 passed

### 2026-06-12T13:29:42+09:00

- `python scripts/kis_paper_transaction_soak.py` 실행 완료.
- Paper transaction result:
  - `069500` MARKET BUY 1 share: `FILLED`, order_log_id 3, execution_log_id 3.
  - `069500` MARKET SELL 1 share: `FILLED`, order_log_id 4, execution_log_id 4.
  - `005930` LIMIT BUY 1 share: `CANCELED`, order_log_id 5.
  - `000660` LIMIT BUY 1 share: `CANCELED`, order_log_id 6.
- UI backend sync:
  - recent fills rows 2 -> 4.
  - order log rows 2 -> 6.
  - order log statuses `FILLED=4`, `CANCELED=2`.
  - KIS today orders rows 9 -> 15.
  - post-run open-like count 0.
- Streamlit AppTest backend live render:
  - home OK
  - portfolio OK
  - trade OK
- `trade.py` KIS today-orders dataframe deprecation warning fixed.
- Regression:
  - focused 24 passed.
  - generated scenarios 119 passed.

### 2026-06-12T13:36:54+09:00

- Reuse validation으로 두 번째 transaction soak 실행:
  - `python scripts/kis_paper_transaction_soak.py --fill-symbol 005930 --unfilled-symbols 069500 000660 --qty 1`
  - `005930` MARKET BUY/SELL 각 1주 FILLED, order_log_id 7/8, execution_log_id 5/6.
  - `069500`/`000660` LIMIT CANCELED, order_log_id 9/10.
  - post-run open-like count 0.
- 발견/수정:
  - 두 번째 run 후 SQLite/UI sync는 order logs 10, recent fills 6으로 증가했지만 KIS today-orders가 15행에서 멈춤.
  - `KisClient.get_today_orders()`가 pagination을 따라가지 않는 read-only bug로 확인.
  - `get_today_orders()`에 `tr_cont`/`CTX_AREA_*` pagination 보강.
  - `tests/unit/test_kis_order_history.py::test_get_today_orders_paginates` 추가.
- 검증:
  - `pytest tests/unit/test_kis_order_history.py tests/unit/test_kis_paper_transaction_soak.py tests/unit/test_home_market_indices_view.py -q` — 13 passed.
  - live KIS paper post-pagination summary: direct/backend today orders 21 rows, order logs 10, recent fills 6, open-like 0.

### 2026-06-12T13:48:13+09:00

- 고가 종목 체결 케이스까지 포함하기 위해 세 번째 transaction soak 실행:
  - `python scripts/kis_paper_transaction_soak.py --fill-symbol 000660 --unfilled-symbols 005930 069500 --qty 1`
  - `000660` MARKET BUY/SELL 각 1주 FILLED, order_log_id 11/12, execution_log_id 7/8.
  - `005930`/`069500` LIMIT CANCELED, order_log_id 13/14.
  - post-run open-like count 0.
- 재사용 분석 스크립트 추가:
  - `scripts/analyze_paper_transactions.py`
  - `tests/unit/test_analyze_paper_transactions.py`
- 재사용 UI sync 스크립트 추가:
  - `scripts/verify_paper_ui_sync.py`
  - `tests/unit/test_verify_paper_ui_sync.py`
- 분석 결과:
  - DB order rows 14, execution rows 8.
  - statuses `FILLED=8`, `CANCELED=6`.
  - KIS today orders 27, open-like 0.
  - UI order logs 14, recent fills 8, holdings 3.
- UI sync script 결과:
  - home/portfolio/trade backend views all OK.
- 검증:
  - `pytest tests/unit/test_verify_paper_ui_sync.py tests/unit/test_analyze_paper_transactions.py tests/unit/test_kis_paper_transaction_soak.py -q` — 6 passed.
  - `python scripts/analyze_paper_transactions.py` — OK.
  - `python scripts/verify_paper_ui_sync.py` — OK.

### 2026-06-12T13:57:59+09:00

- 장중 반복성 확인을 위해 네 번째 transaction soak 실행:
  - `python scripts/kis_paper_transaction_soak.py --fill-symbol 069500 --unfilled-symbols 005930 000660 --qty 1`
  - `069500` MARKET BUY/SELL 각 1주 FILLED, order_log_id 15/16, execution_log_id 9/10.
  - `005930`/`000660` LIMIT CANCELED, order_log_id 17/18.
  - post-run open-like count 0.
- 누적 분석:
  - DB order rows 18, execution rows 10.
  - statuses `FILLED=10`, `CANCELED=8`.
  - KIS today orders 33, open-like 0.
  - UI order logs 18, recent fills 10, holdings 3.
- UI sync script 결과:
  - home/portfolio/trade backend views all OK.
  - Streamlit bare-mode `ScriptRunContext` warning은 AppTest 실행 환경 경고이며 예외 없음.
- 검증:
  - `python scripts/analyze_paper_transactions.py` — OK.
  - `python scripts/verify_paper_ui_sync.py` — OK.

### 2026-06-12T14:13:22+09:00

- 타이머/반복 운용 재사용을 위해 bounded loop runner 추가:
  - `scripts/kis_paper_transaction_loop.py`
  - `tests/unit/test_kis_paper_transaction_loop.py`
  - 기본 1 cycle, 최대 12 cycles, 수량 1주 고정, paper endpoint guard.
- loop dry-run 검증:
  - `python scripts/kis_paper_transaction_loop.py --cycles 3 --interval-sec 0 --dry-run`
  - 3개 심볼 로테이션 계획 확인.
- loop 실제 1-cycle paper 검증:
  - `python scripts/kis_paper_transaction_loop.py --cycles 1 --interval-sec 0`
  - `069500` MARKET BUY/SELL 각 1주 FILLED.
  - `005930`/`000660` LIMIT CANCELED.
  - post-run open-like count 0.
- 누적 분석:
  - DB order rows 22, execution rows 12.
  - statuses `FILLED=12`, `CANCELED=10`.
  - KIS today orders 39, open-like 0.
  - UI order logs 22, recent fills 12, holdings 3.
- UI sync script 결과:
  - 최초 재검증은 124초 timeout.
  - timeout 240초 재시도에서 home/portfolio/trade backend views all OK.
- 검증:
  - `pytest tests/unit/test_kis_paper_transaction_loop.py -q` — 6 passed.
  - `python -m py_compile scripts/kis_paper_transaction_loop.py tests/unit/test_kis_paper_transaction_loop.py` — OK.
  - `python scripts/analyze_paper_transactions.py` — OK.
  - `python scripts/verify_paper_ui_sync.py` — OK after retry.

### 2026-06-12T14:25:54+09:00

- bounded loop 반복 실행 검증:
  - `python scripts/kis_paper_transaction_loop.py --cycles 1 --interval-sec 0`
  - `069500` MARKET BUY/SELL 각 1주 FILLED.
  - `005930`/`000660` LIMIT CANCELED.
  - post-run open-like count 0.
- 발견/수정:
  - `scripts/analyze_paper_transactions.py`의 direct KIS today-orders 조회가 일시 ReadTimeout을 낼 수 있음.
  - 기존 분석은 실패를 빈 KIS 결과처럼 취급할 수 있어 `kis_available` check와 retry/warning을 추가.
  - 최종 실패는 nonzero로 드러나고, 일시 실패는 retry로 복구한다.
- 누적 분석:
  - DB order rows 26, execution rows 14.
  - statuses `FILLED=14`, `CANCELED=12`.
  - KIS today orders 45, open-like 0, warnings 0.
  - UI order logs 26, recent fills 14, holdings 3.
- UI sync script 결과:
  - home/portfolio/trade backend views all OK.
- 검증:
  - `pytest tests/unit/test_analyze_paper_transactions.py -q` — 5 passed.
  - `python -m py_compile scripts/analyze_paper_transactions.py tests/unit/test_analyze_paper_transactions.py` — OK.
  - `python scripts/analyze_paper_transactions.py --kis-retries 3 --kis-retry-sleep 2` — OK.
  - `python scripts/verify_paper_ui_sync.py` — OK.

### 2026-06-12T14:57:19+09:00

- Owner 지적 확인:
  - 이전 거래 테스트는 대부분 `BUY -> SELL` 왕복 또는 `LIMIT -> CANCEL`이라 보유종목이 원복되는 구조였다.
  - 보유 화면 변화를 만들기 위해 buy-and-hold basket을 추가 실행.
- paper-only buy-and-hold runner 추가:
  - `scripts/kis_paper_hold_basket.py`
  - `tests/unit/test_kis_paper_hold_basket.py`
  - 1주 고정, paper endpoint guard, 매도 없음.
- 실제 매수:
  - `python scripts/kis_paper_hold_basket.py --symbols 035420 035720 005380 068270 105560 055550 102110 114260 --qty 1 --min-filled 5 --attempts 10 --sleep 1 --pause-between 0.5`
  - KIS/UI holdings rows 3 -> 11.
  - holdings symbols now include `035420`, `035720`, `005380`, `068270`, `105560`, `055550`, `102110`, `114260` in addition to prior paper holdings.
  - post-run open-like count 0.
- polling timeout reconciliation:
  - `105560`, `055550` were visible in KIS holdings/today-orders but status polling timed out before local order/execution log creation.
  - `scripts/reconcile_paper_fills.py --symbols 055550 105560` reconciled both from KIS today-orders.
  - created order_log_id 33/34 and execution_log_id 21/22.
- 추가 read-only quality fix:
  - `KisClient.get_today_orders(suppress_errors=False)` strict mode 추가.
  - `scripts/analyze_paper_transactions.py` now uses strict mode so timeout/transport failures are not treated as empty success.
  - `scripts/verify_paper_ui_sync.py` default timeout raised to 300s for larger live holdings.
- 누적 분석:
  - DB order rows 34, execution rows 22.
  - statuses `FILLED=22`, `CANCELED=12`.
  - KIS today orders 53, open-like 0, warnings 0.
  - UI holdings rows 11, order logs 34, recent fills 20.
- UI sync script 결과:
  - 120s default timeout was insufficient after holdings expanded.
  - `python scripts/verify_paper_ui_sync.py 300` rendered home/portfolio/trade backend views all OK.
- 검증:
  - `pytest tests/unit/test_kis_paper_hold_basket.py tests/unit/test_analyze_paper_transactions.py tests/unit/test_kis_client.py tests/unit/test_kis_order_history.py -q` — 36 passed.
  - `pytest tests/unit/test_reconcile_paper_fills.py tests/unit/test_kis_paper_hold_basket.py -q` — 4 passed.
  - `python scripts/analyze_paper_transactions.py --kis-retries 5 --kis-retry-sleep 3` — OK.
  - `python scripts/verify_paper_ui_sync.py 300` — OK.

### 2026-06-12T15:17:46+09:00

- Owner 지적: Autofolio UI에서 현재 보유종목/수량/손익/총합이 바로 보이지 않음.
- 수정:
  - `app/ui/views/portfolio.py`
    - 보유 현황 표를 포트폴리오 첫 화면 상단으로 이동.
    - `평가금액 합`, `총 매입금액`, `평가손익`, `총수익률`, `보유 종목` metric 추가/정리.
    - 표 컬럼을 `종목`, `티커`, `자산군`, `수량`, `평단`, `현재가`, `평가금액`, `평가손익`, `손익률`, `비중` 중심으로 재구성.
  - `app/ui/backend.py`
    - `holdings_df(include_dividends=False)` fast path 추가.
    - 포트폴리오/홈/KPI/분석 계산의 기본 보유 조회는 배당 API를 건너뛰어 렌더 지연을 줄임.
  - `app/ui/views/home.py`
    - 홈 backend holdings도 fast path 사용.
  - `scripts/verify_paper_ui_sync.py`
    - `보유 현황`/metric label 기준으로 holdings visibility 감지.
- live UI sync:
  - `python scripts/verify_paper_ui_sync.py`
  - portfolio OK, `contains_holdings=true`.
  - portfolio metrics: `평가금액 합`, `총 매입금액`, `총수익률`, `보유 종목`, `예상 연배당`, `배당수익률`.
  - home/portfolio/trade all OK.
- 누적 분석:
  - DB order rows 34, execution rows 22.
  - UI holdings rows 11.
  - KIS today orders 53, open-like 0.
- 검증:
  - `pytest tests/unit/test_backend_holdings.py tests/unit/test_backend_kpis.py tests/unit/test_portfolio_dividend_view.py tests/unit/test_home_market_indices_view.py tests/unit/test_verify_paper_ui_sync.py -q` — 22 passed.
  - `python -m py_compile app/ui/backend.py app/ui/views/portfolio.py app/ui/views/home.py scripts/verify_paper_ui_sync.py` — OK.
  - `python scripts/verify_paper_ui_sync.py` — OK.

### 2026-06-12T21:34:23+09:00

- 실제 브라우저 확인 중 추가 UI 혼선 발견:
  - 게스트 로그인 후 `라이브` 데이터 소스를 선택해도 top bar가 계속 `데모 모드 — mock 데이터`라고 표시됨.
  - 실제 포트폴리오 수치는 KIS paper/SQLite 기반으로 보였지만, 상태 문구가 사용자 판단을 흐릴 수 있음.
- 수정:
  - `app/ui/components/ui.py`
    - top bar caption을 `data_source` 기준으로 표시.
    - backend 선택 시 `라이브 데이터 — KIS paper · SQLite`, demo 선택 시 기존 mock 문구 표시.
  - `tests/unit/test_top_bar_data_source.py`
    - backend/demo data source caption 회귀 테스트 추가.
- 최신 UI 서버:
  - 기존 8501 서버는 이전 코드가 로드된 상태라, 최신 코드 검증용으로 `http://127.0.0.1:8502` 서버를 별도 기동.
  - 최초 Streamlit onboarding prompt는 빈 stdin 파일로 통과시킨 뒤 서버 health 200 확인.
- browser verification:
  - `http://127.0.0.1:8502/portfolio`
  - 게스트 로그인 -> `라이브` 데이터 소스 선택 -> 포트폴리오 진입.
  - `라이브 데이터`, `보유 현황`, `평가금액 합`, `총 매입금액`, `평가손익`, `총수익률`, `보유 종목` 모두 visible.
  - paper holdings count 11 visible.
- transient note:
  - browser 첫 시도에서 KIS `RemoteDisconnected` 1회가 발생해 demo fallback warning이 표시됐으나, 재시도에서 KIS paper holdings 11개가 정상 표시됨.
  - `analyze_paper_transactions.py --kis-retries 5 --kis-retry-sleep 3`는 같은 시점에 KIS available true, warnings 0.
- 최종 검증:
  - `pytest tests/unit/test_top_bar_data_source.py -q` — 2 passed.
  - `python scripts/analyze_paper_transactions.py --kis-retries 5 --kis-retry-sleep 3` — OK.
  - `python scripts/verify_paper_ui_sync.py` — OK.
  - browser verification on 8502 — OK.

## 완료 기록

완료 시각: 2026-06-12T21:34:23+09:00
검토자: QA + KIS API Engineer + UI/UX Designer (Codex self-review)
감사 로그: AUDIT-2026-06-12-011, AUDIT-2026-06-12-012, AUDIT-2026-06-12-013
실측 비용 (시간): 약 1.6h
실측 비용 (LLM 토큰): unknown

- 원 요청: paper 거래를 계속 실행하며 체결/미체결/트랜잭션/UI 동기화를 기록.
- 실제 작업: 재사용 runner 작성, 반복 paper transaction soak/loop/buy-and-hold 실행, DB/UI sync 확인, 포트폴리오 첫 화면 보유 현황/손익/총합 표시 개선, live data source top bar 문구 수정.
- 결과: paper holdings 11개, DB order logs 34, execution logs 22, KIS today orders 53, open-like 0. UI 포트폴리오에서 보유 현황과 핵심 metric 표시 확인.
- 최종 상태: 완료. prod 실전 주문은 명시 승인 전 계속 금지.

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-12-006-paper-transaction-ui-sync-soak.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-12-006.md`
- `agents/qa/test_cases/PAPER-TRANSACTION-UI-SYNC-SOAK.md`
- `scripts/kis_paper_transaction_soak.py`
- `scripts/kis_paper_transaction_loop.py`
- `scripts/kis_paper_hold_basket.py`
- `scripts/reconcile_paper_fills.py`
- `scripts/analyze_paper_transactions.py`
- `scripts/verify_paper_ui_sync.py`

## Done When

- paper endpoint guard is verified.
- Filled market buy/sell records are created in KIS paper and SQLite.
- Pending/canceled limit order records are created in KIS paper and SQLite.
- UI backend sees new fills/order logs without restart.
- Post-run KIS open-like orders are zero.
- Evidence and BRIEF record redacted transaction summary.

## Verification

- `python scripts/kis_paper_transaction_soak.py`
- backend sync summary in script output
- focused pytest for script/UI/backend
- task/docs/report gates
