# KIS Project Mapping

KIS 레퍼런스를 Autofolio 코드에 적용할 때의 파일 대응표다.

## Runtime Code

| KIS topic | Autofolio file | Notes |
|-----------|----------------|-------|
| 환경별 설정 | `app/config/settings.py` | `resolve_settings(env)`가 paper/prod 키와 base URL을 해석 |
| 인증 | `app/brokers/kis/kis_auth.py` | 토큰 발급, token path, auth error 처리 |
| REST adapter | `app/brokers/kis/kis_client.py` | 현재가, 잔고, 주문, 취소, 체결조회 |
| Internal model | `app/brokers/base.py` | `PriceQuote`, `OrderRequest`, `OrderResult`, `Position` |
| Broker selection | `app/brokers/factory.py` | `KIS_ENV`와 mock/paper/prod 전환 |
| Order orchestration | `app/engine/order_flow.py` | 안전 게이트 뒤 주문 흐름. R3 surface |
| Safety gates | `app/risk/**` | 킬스위치, 거래시간, 한도, 중복 방지 |

## Tests And Smoke Scripts

| Purpose | File |
|---------|------|
| KIS adapter unit tests | `tests/unit/test_kis_client.py` |
| Token-only connectivity | `scripts/kis_token_smoke.py` |
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
| `inquire-balance` | `get_positions` | `test_get_positions_parses_and_skips_zero` |
| `order-cash` | `place_order` | `test_place_buy_limit_builds_body_and_returns_pending` |
| `order-rvsecncl` | `cancel_order` | `test_cancel_uses_cached_org_no` |
| `inquire-daily-ccld` | `get_order_status` | `test_get_order_status_filled` |
| `inquire-daily-ccld` | `get_today_orders`, `app/ui/backend.py::kis_today_orders` | `test_get_today_orders_*` 단위테스트 완료 |
| `inquire-balance` (output2) | `get_cash_balance` | 예수금. `test_get_cash_balance_*` 단위테스트 완료 |
| `inquire-daily-itemchartprice` | `get_price_history`, `app/data/data_loader.py::load_price_history` | 일봉/주봉. `test_get_price_history_*` 단위테스트 완료 |
| `inquire-psbl-rvsecncl` | `_lookup_org_no` | `test_cancel_without_org_no_and_lookup_fails_returns_failed` |
