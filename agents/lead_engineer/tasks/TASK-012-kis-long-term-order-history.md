---
type: task
id: TASK-012
status: 완료
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Medium
difficulty: 낮
est_hours: 2
est_tokens: 50000
tags: [kis, history]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
updated_at: 2026-06-12T01:59:16+09:00
completed_at: 2026-06-12T01:59:16+09:00
---

# TASK-012 KIS 장기 거래내역 조회 (3개월+, CTSC9215R)

작업 ID: TASK-012
상태: 완료
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

현재 `inquire-daily-ccld`는 최근 3개월 이내 거래내역만 제공한다. 3개월 이전 내역은 TR `CTSC9215R`(실전) / `VTSC9215R`(paper)로 별도 조회해야 한다. 장기 손익 분석 및 세금 신고 지원을 위해 필요하다.

## 구현 범위

- `KisClient.get_order_history(start_date, end_date)` 구현
- 3개월 이내: 기존 `inquire-daily-ccld` 경로 사용
- 3개월 초과: TR `CTSC9215R` / `VTSC9215R` 자동 전환
- 응답 정규화 — 두 TR의 컬럼을 동일 스키마로 매핑
- 내역·손익 탭에서 날짜 범위 선택 시 연결

## 완료 기준

- [x] `get_order_history()` 구현 및 TR 자동 전환 로직
- [x] 단위 테스트 (3개월 경계 케이스 포함)
- [x] 내역·손익 탭 날짜 범위 필터 연결 확인

## 완료 기록

완료 시각: 2026-06-12T01:59:16+09:00

## 요구사항

요청자: Owner
현재 요청: backlog에 등록된 task들 순차적으로 작업 및 마무리

KIS `inquire-daily-ccld`의 recent/long TR 차이를 처리해 3개월 이상 날짜 범위 주문내역을 조회하고, 내역·손익 화면 날짜 조회와 연결한다.

## 완료 내용

- `KisClient.get_order_history(start_date, end_date)`를 보강했다.
  - 날짜 형식과 시작/종료 순서를 검증한다.
  - KST 현재일 기준 3개월 경계를 계산한다.
  - 3개월 이내는 `TTTC0081R`/`VTTC0081R`를 사용한다.
  - 3개월 이전은 `CTSC9215R`/`VTSC9215R`를 사용한다.
  - 날짜 범위가 경계를 걸치면 long 구간과 recent 구간으로 나눠 순차 호출한다.
  - `tr_cont` 기반 페이지네이션을 처리한다.
  - UI가 사용하는 canonical 주문내역 컬럼으로 정규화한다.
- `app/ui/backend.py::kis_order_history()`와 기존 `app/ui/views/history.py` 날짜 입력/조회 버튼 연결을 AppTest로 검증했다.
- `docs/KIS_API_SPEC.md`, `docs/references/kis/PROJECT-MAPPING.md`, `docs/BACKLOG.md`, `STATUS.md`를 갱신했다.

## 결과

TASK-012 완료. Autofolio는 recent/long KIS 주문내역 TR을 자동 선택·분할해 내역 화면에서 날짜 범위 조회로 사용할 수 있다.

## 검증

- `pytest tests\unit\test_kis_order_history.py tests\unit\test_history_kis_view.py` — 9 passed
- `python -m py_compile app\brokers\kis\kis_client.py tests\unit\test_kis_order_history.py tests\unit\test_history_kis_view.py` — passed

검증 범위:
- recent TR 조회
- long-term TR 조회
- 3개월 경계 분할 조회
- 페이지네이션 `tr_cont=M/F` 처리
- date format/order validation
- 내역·손익 화면 날짜 조회 버튼이 `backend.kis_order_history()`를 호출하는지 AppTest로 확인

## 남은 리스크

- 실제 KIS paper/prod API 호출은 하지 않았다. 네트워크 없는 단위 테스트와 Streamlit AppTest로 TR 선택, 파라미터, 페이지네이션, UI 연결을 검증했다.
