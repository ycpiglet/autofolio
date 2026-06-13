---
type: task
id: TASK-017
status: 완료
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 낮
est_hours: 2
est_tokens: 50000
tags: [kis, dividend]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
updated_at: 2026-06-12T02:36:54+09:00
completed_at: 2026-06-12T02:36:54+09:00
---

# TASK-017 KIS 배당 정보 조회

작업 ID: TASK-017
상태: 완료
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

포트폴리오 수익 분석에서 배당 수익률은 중요한 요소이지만 현재 화면에 표시되지 않는다. KIS `inquire-dividend` 엔드포인트 또는 `inquire-daily-itemchartprice` 배당 필드를 파싱해 포트폴리오 화면에 배당 수익률을 표시한다.

## 구현 범위

- `KisClient.get_dividend_info(symbol)` 구현
- `inquire-dividend` 또는 일봉 데이터의 배당 필드 활용
- 배당 이력(지급일, 주당 배당금, 배당 수익률) 파싱
- 포트폴리오 화면 종목별 배당 수익률 컬럼 추가
- 총 포트폴리오 예상 연배당 수익률 계산 표시

## 완료 기준

- [x] `get_dividend_info()` 구현 및 단위 테스트
- [x] 포트폴리오 화면 배당 수익률 컬럼 표시 확인

## 진행 기록

- 2026-06-12T02:31:24+09:00 — 공식 KIS GitHub 샘플 기준 `ksdinfo_dividend`(`/uapi/domestic-stock/v1/ksdinfo/dividend`, `HHKDB669102C0`)를 TASK-017의 1차 endpoint로 선택. `dividend_rate`는 랭킹 API, `period_rights`는 계좌 권리 현황 API라 본 작업의 기본 종목별 포트폴리오 표에는 보조 근거로만 둔다.

## 완료 기록

완료 시각: 2026-06-12T02:36:54+09:00

## 요구사항

요청자: Owner
현재 요청: backlog에 등록된 task들 순차적으로 작업 및 마무리

KIS 배당 정보를 조회해 포트폴리오 화면에 종목별 배당 수익률과 총 예상 연배당 수익률을 표시한다.

## 완료 내용

- `KisClient.get_dividend_info(symbol, start_date=None, end_date=None)`를 구현했다.
  - endpoint: `/uapi/domestic-stock/v1/ksdinfo/dividend`
  - TR: `HHKDB669102C0`
  - params: `CTS`, `GB1=0`, `F_DT`, `T_DT`, `SHT_CD`, `HIGH_GB`
  - `output1`의 `record_date`, `per_sto_divi_amt`, `divi_rate`, `divi_pay_dt` 등을 정규화했다.
- `backend.holdings_df()`가 KIS 브로커에서 배당 정보를 조회해 `예상연배당`, `배당수익률` 컬럼을 추가하도록 연결했다.
- 포트폴리오 화면 상단에 총 `예상 연배당`과 포트폴리오 `배당수익률` metric을 추가했다.
- mock 포트폴리오 데이터에도 같은 컬럼을 추가해 데모 모드에서도 UI 표면이 유지되게 했다.
- 공식 샘플 기준 `dividend_rate`는 배당률 상위 랭킹 API라, TASK 원문의 `inquire-dividend` 후보 대신 `ksdinfo_dividend`를 정본으로 기록했다.
- `docs/KIS_API_SPEC.md`, `docs/references/kis/PROJECT-MAPPING.md`, `docs/BACKLOG.md`를 갱신했다.

## 결과

TASK-017 완료. backend/KIS 모드 포트폴리오 표에서 종목별 예상연배당과 배당수익률을 확인하고, 화면 상단에서 총 예상 연배당 수익률을 볼 수 있다.

## 검증

- `pytest tests\unit\test_kis_dividend_info.py tests\unit\test_backend_holdings.py tests\unit\test_portfolio_dividend_view.py` — 8 passed
- `pytest tests\unit\test_kis_dividend_info.py tests\unit\test_backend_holdings.py tests\unit\test_backend_kpis.py tests\unit\test_portfolio_dividend_view.py tests\unit\test_kis_client.py tests\unit\test_kis_batch_price.py tests\unit\test_backend_watchlist.py tests\unit\test_backend_market_indices.py` — 49 passed
- `python -m py_compile app\brokers\kis\kis_client.py app\ui\backend.py app\ui\views\portfolio.py app\ui\mock\data.py tests\unit\test_kis_dividend_info.py tests\unit\test_backend_holdings.py tests\unit\test_portfolio_dividend_view.py` — passed

## 남은 리스크

- 실제 KIS paper API 호출은 하지 않았다. 공식 GitHub 샘플 기반 파라미터와 fake 응답으로 검증했다.
- 배당 API는 일정/예탁원 기반 데이터라 실시간 현금흐름 확정값과 다를 수 있다. 운영 화면에서는 예상치로만 해석해야 한다.
