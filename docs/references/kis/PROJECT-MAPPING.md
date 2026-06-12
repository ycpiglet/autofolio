# KIS Project Mapping

KIS 레퍼런스를 Autofolio 코드에 적용할 때의 파일 대응표다.

## Runtime Code

| KIS topic | Autofolio file | Notes |
|-----------|----------------|-------|
| 환경별 설정 | `app/config/settings.py` | `resolve_settings(env)`가 paper/prod 키와 base URL을 해석 |
| 인증 | `app/brokers/kis/kis_auth.py` | 토큰 발급, token path, auth error 처리 |
| REST adapter | `app/brokers/kis/kis_client.py` | 현재가, 잔고, 주문, 취소, 체결조회 |
| WebSocket adapter | `app/brokers/kis/kis_ws_client.py` | approval key, 구독, 현재가/호가/체결통보 파싱, Notifier 연결 |
| Internal model | `app/brokers/base.py` | `PriceQuote`, `OrderRequest`, `OrderResult`, `Position` |
| Broker selection | `app/brokers/factory.py` | `KIS_ENV`와 mock/paper/prod 전환 |
| Order orchestration | `app/engine/order_flow.py` | 안전 게이트 뒤 주문 흐름. R3 surface |
| Safety gates | `app/risk/**` | 킬스위치, 거래시간, 한도, 중복 방지 |

## Tests And Smoke Scripts

| Purpose | File |
|---------|------|
| KIS adapter unit tests | `tests/unit/test_kis_client.py` |
| Token-only connectivity | `scripts/kis_token_smoke.py` |
| WebSocket unit coverage | `tests/unit/test_kis_ws_client.py` |
| Paper order lifecycle | `scripts/kis_paper_order_smoke.py` |
| Mock order integration | `tests/integration/test_mock_order_flow.py` |
| Engine E2E | `tests/integration/test_engine_e2e.py` |

## Reference Docs

| Purpose | File |
|---------|------|
| KIS implementation spec | `docs/KIS_API_SPEC.md` |
| Reference pack index | `docs/references/kis/README.md` |
| Safety boundary | `docs/references/kis/SAFETY.md` |
| Merge/R3 policy | `agents/lead_engineer/MERGE-POLICY.md` and `AGENTS.md` |

## Endpoint Mapping

| Endpoint | Client method | Test signal |
|----------|---------------|-------------|
| `inquire-price` | `get_current_price` | `test_get_current_price_parses_stck_prpr` |
| `intstock-multprice` | `get_prices_batch`, `app/ui/backend.py::watchlist`, `holdings_df` price cache | 최대 30종목 청크. `test_kis_batch_price.py`, `test_backend_watchlist.py` 완료 |
| `inquire-index-price` | `get_index_price`, `app/ui/backend.py::market_indices_df`, `app/ui/views/home.py` | KOSPI/KOSDAQ/KOSPI200. `test_kis_index_price.py`, `test_home_market_indices_view.py` 완료 |
| `inquire-index-price` + `idxcode.mst` | `get_sector_price`, `app/ui/backend.py::sector_performance_df`, `app/ui/views/analysis.py` | 주요 업종 현재지수. `test_kis_sector_price.py`, `test_analysis_intraday_view.py` 완료 |
| `ksdinfo/dividend` | `get_dividend_info`, `app/ui/backend.py::holdings_df`, `app/ui/views/portfolio.py` | 종목별 배당 일정, 예상연배당/배당수익률. `test_kis_dividend_info.py`, `test_portfolio_dividend_view.py` 완료 |
| `inquire-asking-price-exp-ccn` | `get_order_book`, `estimate_order_book_slippage`, `app/ui/backend.py::order_book_df`, `app/ui/views/trade.py` | 10단계 호가/예상체결 snapshot과 매매 화면 슬리피지 metric. `test_kis_order_book.py`, `test_trade_order_book_view.py` 완료 |
| `news-title` | `get_disclosures`, `classify_disclosure_title`, `app/ui/backend.py::refresh_disclosure_gate`, `app/ui/views/alerts.py`, `app/ui/views/trade.py` | 종합 시황/공시 제목 조회, 중대 공시 system_state 차단 플래그, 알림 smoke. `test_kis_disclosures.py`, `test_backend_disclosures.py`, `test_alerts_disclosure_view.py` 완료 |
| `inquire-price` + `finance-ratio` | `get_fundamental`, `get_finance_ratio_rank`, `app/ui/backend.py::fundamental`, `ResearchAgent.propose_price_condition`, `app/ui/views/analysis.py` | PER/PBR/EPS/HTS 시가총액 파싱, 재무비율 ranking 보조 지표, 분석 탭 재무 metric. `test_kis_fundamental.py`, `test_backend_fundamental.py`, `test_analysis_intraday_view.py` 완료 |
| `inquire-balance` | `get_positions` | `test_get_positions_parses_and_skips_zero` |
| `order-cash` | `place_order` | `test_place_buy_limit_builds_body_and_returns_pending` |
| `order-rvsecncl` | `cancel_order` | `test_cancel_uses_cached_org_no` |
| `inquire-daily-ccld` | `get_order_status` | `test_get_order_status_filled` |
| `inquire-daily-ccld` | `get_today_orders`, `app/ui/backend.py::kis_today_orders` | `test_get_today_orders_*` 단위테스트 완료 |
| `inquire-daily-ccld` recent/long | `get_order_history`, `app/ui/backend.py::kis_order_history`, `app/ui/views/history.py` | 3개월 경계 TR 분할. `test_kis_order_history.py`, `test_history_kis_view.py` 완료 |
| `inquire-balance` (output2) | `get_cash_balance` | 예수금. `test_get_cash_balance_*` 단위테스트 완료 |
| `inquire-daily-itemchartprice` | `get_price_history`, `app/data/data_loader.py::load_price_history` | 일봉/주봉. `test_get_price_history_*` 단위테스트 완료 |
| `inquire-time-itemchartprice` | `get_intraday_chart`, `app/data/data_loader.py::load_intraday_chart`, `app/ui/backend.py::intraday_chart_df` | 당일 분봉. `test_get_intraday_chart_*`, `test_load_intraday_chart_*` 단위테스트 완료 |
| `WebSocket /oauth2/Approval` + `/tryitout` | `KisWebSocketClient`, `get_approval_key`, `parse_realtime_message` | 실시간 체결가/호가/체결통보. `test_kis_ws_client.py` 단위테스트 완료 |
| `inquire-psbl-rvsecncl` | `_lookup_org_no` | `test_cancel_without_org_no_and_lookup_fails_returns_failed` |
