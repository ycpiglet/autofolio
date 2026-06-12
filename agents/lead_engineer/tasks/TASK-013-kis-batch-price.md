---
type: task
id: TASK-013
status: 완료
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Medium
difficulty: 하
est_hours: 2
est_tokens: 50000
tags: [kis, price, performance]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
updated_at: 2026-06-12T02:07:19+09:00
completed_at: 2026-06-12T02:07:19+09:00
---

# TASK-013 KIS 복수 종목 현재가 배치 조회 (intstock-multprice)

작업 ID: TASK-013
상태: 완료
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00

## 배경 및 목적

화이트리스트 종목이 여러 개일 때 현재가를 개별 REST 호출로 조회하면 레이트리밋을 빠르게 소모하고 응답 지연이 누적된다. `inquire-price-2` 배치 API를 활용하면 한 번의 호출로 복수 종목 가격을 수신할 수 있어 성능과 안정성이 향상된다.

## 구현 범위

- `KisClient.get_prices_batch(symbols: list[str])` 구현
- 최대 배치 크기(KIS 제한) 초과 시 자동 청크 분할
- 기존 단일 종목 `get_current_price()` 호출을 배치 경로로 대체 (option)
- 엔진 및 포트폴리오 화면 가격 갱신 경로에 연결

## 완료 기준

- [x] `get_prices_batch()` 구현 및 단위 테스트
- [x] 청크 분할 경계 테스트 (1종목, 배치 한도 정확히, 한도+1)
- [x] 기존 단일 호출 대비 레이트리밋 소모 절감 확인 (batch stats 기반)

## 완료 기록

완료 시각: 2026-06-12T02:07:19+09:00

## 요구사항

요청자: Owner
현재 요청: backlog에 등록된 task들 순차적으로 작업 및 마무리

화이트리스트/포트폴리오 등 복수 종목 가격 조회에서 단건 REST 호출 수를 줄이고, KIS 공식 복수 종목 시세 API를 사용한다.

## 완료 내용

- 공식 샘플을 확인한 결과 `inquire-price-2`는 단일 종목 확장 현재가 API이며, 복수 종목 batch 정본은 `intstock-multprice`(`FHKST11300006`)임을 문서화했다.
- `KisClient.get_prices_batch(symbols, batch_size=30)`를 `intstock-multprice` 기반으로 재구현했다.
  - 중복/공백 종목 제거
  - 최대 30종목 청크 분할
  - `FID_COND_MRKT_DIV_CODE_N`, `FID_INPUT_ISCD_N` 파라미터 생성
  - `inter_shrn_iscd`, `inter2_prpr` 응답 파싱
  - chunk 실패 또는 응답 누락 종목만 기존 `get_current_price()` 단건 fallback
  - `_last_batch_price_stats`에 `symbols`, `batch_calls`, `single_fallback_calls`, `saved_calls` 기록
- `app/ui/backend.py::watchlist()`가 batch price cache를 먼저 사용하도록 연결했다.
- 기존 `holdings_df()`는 이미 `get_prices_batch()`를 우선 사용하므로 새 batch 구현이 포트폴리오 가격 경로에도 적용된다.
- `docs/KIS_API_SPEC.md`, `docs/references/kis/PROJECT-MAPPING.md`, `docs/BACKLOG.md`, `STATUS.md`를 갱신했다.

## 결과

TASK-013 완료. 복수 종목 가격 조회는 공식 KIS `intstock-multprice`로 최대 30종목씩 묶어 호출하고, 실패 종목만 단건 fallback한다.

## 검증

- `pytest tests\unit\test_kis_batch_price.py tests\unit\test_backend_watchlist.py` — 9 passed
- `python -m py_compile app\brokers\kis\kis_client.py app\ui\backend.py tests\unit\test_kis_batch_price.py` — passed

검증 범위:
- batch endpoint 파라미터/TR 검증
- partial missing response fallback
- empty list
- 1종목, 30종목, 31종목 청크 경계
- batch_size validation
- watchlist가 batch cache를 사용하고 단건 fallback을 호출하지 않는 경로

## 남은 리스크

- 실제 KIS paper API 호출은 하지 않았다. 공식 샘플 기반 파라미터/응답 형태를 fake 응답으로 검증했다.
- TASK 원문에 적힌 `inquire-price-2`는 배치 API가 아니므로, 정본 구현은 공식 batch endpoint인 `intstock-multprice`로 대체했다.
