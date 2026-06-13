---
type: task
id: TASK-015
status: 완료
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 낮
est_hours: 1
est_tokens: 50000
tags: [kis, index]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
updated_at: 2026-06-12T02:25:16+09:00
completed_at: 2026-06-12T02:15:30+09:00
---

# TASK-015 KIS 지수 조회 (KOSPI·KOSDAQ·KOSPI200)

작업 ID: TASK-015
상태: 완료
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

홈 대시보드에 KOSPI·KOSDAQ·KRX 지수를 표시하면 시장 컨텍스트를 즉시 파악할 수 있다. `inquire-index-price` 엔드포인트로 구현 가능하며 난이도가 낮다.

## 구현 범위

- `KisClient.get_index_price(index_code: str)` 추가
- index_code: '0001'(KOSPI), '1001'(KOSDAQ), '2001'(KRX300) 등
- 홈 대시보드 상단 지수 표시 위젯 연결
- 지수 코드 상수를 `app/brokers/kis/constants.py`에 정의

## 완료 기준

- [x] `get_index_price()` 구현 및 단위 테스트
- [x] 홈 화면 지수 표시 위젯 확인 (mock 응답 기반)

## 완료 기록

완료 시각: 2026-06-12T02:15:30+09:00

## 요구사항

요청자: Owner
현재 요청: backlog에 등록된 task들 순차적으로 작업 및 마무리

KIS `inquire-index-price`로 국내 주요 지수를 조회하고 홈 대시보드에 시장 컨텍스트를 표시한다.

## 완료 내용

- `app/brokers/kis/constants.py`를 추가하고 공식 샘플에서 확인된 지수 코드를 상수화했다.
  - KOSPI `0001`
  - KOSDAQ `1001`
  - KOSPI200 `2001`
- `KisClient.get_index_price(index_code)`를 추가했다.
  - endpoint: `/uapi/domestic-stock/v1/quotations/inquire-index-price`
  - TR: `FHPUP02100000`
  - `FID_COND_MRKT_DIV_CODE=U`
  - `bstp_nmix_prpr`, `bstp_nmix_prdy_vrss`, `prdy_vrss_sign`, `bstp_nmix_prdy_ctrt`, `acml_vol` 파싱
- `app/ui/backend.py::market_indices_df()`를 추가했다.
- `app/ui/views/home.py` 상단에 backend 모드 지수 metric 위젯을 추가했다.
- 공식 샘플 기준 `2001`은 KRX300이 아니라 KOSPI200이므로, TASK 원문 표기를 정정해 기록했다.
- `docs/KIS_API_SPEC.md`, `docs/references/kis/PROJECT-MAPPING.md`, `docs/BACKLOG.md`, `STATUS.md`를 갱신했다.

## 결과

TASK-015 완료. 홈 화면 backend 모드에서 KOSPI/KOSDAQ/KOSPI200 현재 지수를 표시할 수 있다.

## 검증

- `pytest tests\unit\test_kis_index_price.py tests\unit\test_backend_market_indices.py tests\unit\test_home_market_indices_view.py` — 5 passed
- `python -m py_compile app\brokers\kis\kis_client.py app\brokers\kis\constants.py app\ui\backend.py app\ui\views\home.py tests\unit\test_kis_index_price.py tests\unit\test_backend_market_indices.py tests\unit\test_home_market_indices_view.py` — passed
- `pytest tests\unit\test_home_market_indices_view.py tests\unit\test_backend_watchlist.py` — 2 passed
- `pytest tests\unit\test_analysis_intraday_view.py tests\unit\test_home_market_indices_view.py tests\unit\test_backend_watchlist.py` — 3 passed
- `pytest tests\unit\test_kis_index_price.py tests\unit\test_backend_market_indices.py tests\unit\test_home_market_indices_view.py tests\unit\test_kis_batch_price.py tests\unit\test_backend_watchlist.py tests\unit\test_kis_ws_client.py tests\unit\test_kis_order_history.py tests\unit\test_history_kis_view.py tests\unit\test_kis_client.py tests\unit\test_kis_auth_cache.py tests\unit\test_kis_client_cash.py tests\unit\test_analysis_intraday_view.py tests\unit\test_kis_intraday.py tests\unit\test_data_loader.py tests\unit\test_run_paper_engine_once.py` — 84 passed

## 추가 수정

- `tests/unit/test_home_market_indices_view.py`와 `tests/unit/test_analysis_intraday_view.py`의 Streamlit AppTest 임시 앱이 `app.ui.backend` 함수를 전역 대입으로 덮어써 후속 테스트에 영향을 주던 문제를 `unittest.mock.patch.object` 컨텍스트로 격리했다.

## 남은 리스크

- 실제 KIS paper API 호출은 하지 않았다. 공식 샘플 기반 파라미터와 fake 응답으로 검증했다.
- KRX300 코드는 공식 샘플에 직접 나오지 않아 상수에 포함하지 않았다. 필요하면 포털 종목정보 다운로드와 대조 후 추가한다.
