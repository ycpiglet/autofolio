---
type: task
id: TASK-011
status: 대기
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
---

# TASK-011 KIS 분봉 데이터 조회 (inquire-time-itemchartprice)

작업 ID: TASK-011
상태: 대기
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

- [ ] `KisClient.get_intraday_chart()` 구현 및 단위 테스트
- [ ] data_loader 연결 확인 (mock 응답 기반)
- [ ] 분석 화면에 분봉 차트 위젯 표시 (paper 모드)
