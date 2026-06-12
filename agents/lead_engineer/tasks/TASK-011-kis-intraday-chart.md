---
type: task
id: TASK-011
status: 완료
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: High
difficulty: 중
est_hours: 3
est_tokens: 50000
tags: [kis, chart, intraday]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
updated_at: 2026-06-12T01:31:38+09:00
completed_at: 2026-06-12T01:31:38+09:00
---

# TASK-011 KIS 분봉 데이터 조회 (inquire-time-itemchartprice)

작업 ID: TASK-011
상태: 완료
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

현재 분석 화면에서 당일 분봉 차트가 없어 단기 매매 의사결정 근거가 부족하다. `/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice` 엔드포인트(TR `FHKST03010200`)를 통해 분봉·틱봉 데이터를 조회하면 분석 화면에 인트라데이 차트를 표시할 수 있다.

## 구현 범위

- `KisClient.get_intraday_chart(symbol, time_unit)` 메서드 추가
- TR ID `FHKST03010200`, 응답 output2 배열 파싱
- `time_unit` 파라미터: '1', '3', '5', '10', '30', '60' (분 단위)
- `app/data_loader.py`의 chart 데이터 경로에 연결
- 분석 화면 분봉 차트 탭 표시

## 완료 기준

- [x] `KisClient.get_intraday_chart()` 구현 및 단위 테스트
- [x] data_loader 연결 확인 (mock 응답 기반)
- [x] 분석 화면에 분봉 차트 위젯 표시 (paper 모드)

## 완료 기록

완료 시각: 2026-06-12T01:31:38+09:00

## 요구사항

요청자: Owner
현재 요청: backlog에 등록된 task들 순차적으로 작업 및 마무리

KIS `inquire-time-itemchartprice` 기반 당일 분봉 조회를 구현하고 분석 화면에서 사용할 수 있게 한다.

## 완료 내용

- `KisClient.get_intraday_chart(symbol, time_unit, count, input_time)`를 공식 KIS 샘플에 맞춰 보강했다.
  - TR `FHKST03010200`
  - `FID_INPUT_HOUR_1`
  - `FID_PW_DATA_INCU_YN=Y`
  - `output2`의 `stck_bsop_date`, `stck_cntg_hour`, `stck_prpr`, `stck_oprc`, `stck_hgpr`, `stck_lwpr`, `cntg_vol` 파싱
- 공식 샘플에는 분 단위 선택 파라미터가 없어, `time_unit` 3/5/10/30/60은 1분 원천 데이터를 클라이언트에서 OHLCV 집계하도록 구현했다.
- `app/data/data_loader.py::load_intraday_chart`와 `app/ui/backend.py::intraday_chart_df`를 추가했다.
- `app/ui/views/analysis.py`에 라이브 모드 분봉 차트 섹션을 추가했다.
- `docs/KIS_API_SPEC.md`와 `docs/references/kis/PROJECT-MAPPING.md`를 갱신했다.

## 결과

TASK-011 완료. KIS adapter, data_loader, backend, 분석 화면까지 당일 분봉 조회 경로가 연결됐다.

## 검증

- `pytest tests\unit\test_analysis_intraday_view.py tests\unit\test_kis_intraday.py tests\unit\test_data_loader.py` — 12 passed
- `python -m py_compile app\brokers\kis\kis_client.py app\data\data_loader.py app\ui\backend.py app\ui\views\analysis.py tests\unit\test_analysis_intraday_view.py tests\unit\test_kis_intraday.py tests\unit\test_data_loader.py` — passed

## 남은 리스크

- 실제 paper API 호출은 하지 않았다. 네트워크 없는 단위 테스트와 Streamlit AppTest로 요청 구성, 파싱, data_loader, UI 표시를 검증했다.
- 로컬 Streamlit 서버 foreground 기동은 확인됐으나, background 서버 유지 및 브라우저 검증은 Windows sandbox 문제로 완료하지 못했다.
