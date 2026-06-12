---
type: task
id: TASK-019
status: 완료
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 하
est_hours: 2
est_tokens: 50000
tags: [kis, sector]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
updated_at: 2026-06-12T08:01:50+09:00
completed_at: 2026-06-12T08:01:50+09:00
---

# TASK-019 KIS 업종별 시세 조회

작업 ID: TASK-019
상태: 완료
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

분석 탭에서 업종 히트맵 또는 업종별 퍼포먼스를 보여주면 포트폴리오 섹터 노출을 시장 업종 흐름과 비교할 수 있다. `inquire-upjong-price` 엔드포인트로 업종별 시세를 수신한다.

## 구현 범위

- `KisClient.get_sector_price(sector_code: str)` 구현
- 주요 업종 코드 상수 정의 (반도체, 자동차, 금융 등)
- 업종별 등락률·거래대금 파싱
- 분석 탭에 업종 퍼포먼스 테이블 또는 히트맵 추가

## 완료 기준

- [x] `get_sector_price()` 구현 및 단위 테스트
- [x] 분석 탭 업종 퍼포먼스 표시 확인 (mock 응답 기반)

## 진행 기록

- 2026-06-12T07:55:55+09:00 — 공식 GitHub 현행 샘플 트리에는 국내 `inquire-upjong-price` 샘플이 없고, `inquire-index-price`가 "국내업종 현재지수" 정본임을 재확인. 업종 코드는 공식 `stocks_info/sector_code.py`가 내려받는 KIS `idxcode.mst` master에서 확인해 `전기·전자`, `운송장비·부품`, `금융` 등으로 매핑한다.

## 완료 기록

완료 시각: 2026-06-12T08:01:50+09:00

## 요구사항

요청자: Owner
현재 요청: backlog에 등록된 task들 순차적으로 작업 및 마무리

KIS 업종별 현재지수를 조회해 분석 탭에서 주요 업종 퍼포먼스를 비교할 수 있게 한다.

## 완료 내용

- `app/brokers/kis/constants.py`에 주요 업종 코드 상수를 추가했다.
  - 공식 master 기준 API 입력 코드는 5자리 원문에서 첫 시장구분값을 제외한 4자리다.
  - TASK 원문의 "반도체/자동차"는 공식 업종명 기준 `KOSPI 전기·전자`, `KOSPI 운송장비·부품` proxy로 기록했다.
- `KisClient.get_sector_price(sector_code)`를 추가했다.
  - 공식 endpoint: `/uapi/domestic-stock/v1/quotations/inquire-index-price`
  - TR: `FHPUP02100000`
  - params: `FID_COND_MRKT_DIV_CODE=U`, `FID_INPUT_ISCD=<업종코드>`
  - `price`, `change`, `change_rate`, `volume`, `trading_value` 파싱
- `backend.sector_performance_df()`를 추가했다.
- 분석 탭에 `업종 퍼포먼스` 표와 등락률 bar chart를 추가했다.
- `docs/KIS_API_SPEC.md`, `docs/references/kis/PROJECT-MAPPING.md`, `docs/BACKLOG.md`를 갱신했다.

## 결과

TASK-019 완료. backend/KIS 모드 분석 탭에서 주요 KOSPI/KOSDAQ/KOSPI200 업종 현재지수와 등락률을 비교할 수 있다.

## 검증

- `pytest tests\unit\test_kis_sector_price.py tests\unit\test_backend_sector_performance.py tests\unit\test_analysis_intraday_view.py tests\unit\test_kis_index_price.py tests\unit\test_backend_market_indices.py` — 9 passed

## 남은 리스크

- 실제 KIS paper API 호출은 하지 않았다. 공식 샘플과 KIS master 파일 기반 파라미터를 fake 응답으로 검증했다.
- KIS 현행 샘플에는 `inquire-upjong-price`가 없어 `inquire-index-price`로 구현했다. 향후 포털에 별도 업종 API가 확인되면 mapping만 교체하면 된다.
