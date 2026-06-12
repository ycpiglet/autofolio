---
type: task
id: TASK-018
status: 완료
owner: KIS API Engineer
assignees: [KIS API Engineer]
priority: Low
difficulty: 중
est_hours: 3
est_tokens: 50000
tags: [kis, orderbook, realtime]
trigger_meeting: 자가발생
created: 2026-06-10
created_at: 2026-06-10T23:39:38+09:00
---

# TASK-018 KIS 호가창 10단계 조회 (inquire-asking-price-exp-ccn)

작업 ID: TASK-018
상태: 완료
Owner: KIS API Engineer
요청 시각: 2026-06-10T23:39:38+09:00
기록 시각: 2026-06-10T23:39:38+09:00
완료 시각: 2026-06-12T08:20:01+09:00

## 배경 및 목적

매매 화면에서 호가창이 없으면 주문 진입 시 슬리피지 예측이 어렵다. `inquire-asking-price-exp-ccn` 엔드포인트로 매수/매도 10단계 호가와 잔량을 조회해 매매 결정 품질을 높인다.

## 구현 범위

- `KisClient.get_order_book(symbol)` 구현
- 매수 10단계·매도 10단계 호가(price) 및 잔량(qty) 파싱
- 매매 화면에 호가창 위젯 추가 (테이블 또는 시각화)
- 주문 전 슬리피지 추정 계산 헬퍼 추가 (예상 체결가 vs 현재가)
- TASK-010 WebSocket 구독(H0STASP0)과 연동 옵션

## 완료 기준

- [x] `get_order_book()` 구현 및 단위 테스트
- [x] 매매 화면 호가창 위젯 표시 확인
- [x] 슬리피지 추정 헬퍼 단위 테스트

## 완료 기록

- 원 요청: KIS `inquire-asking-price-exp-ccn` 기반 매수/매도 10단계 호가와 잔량을 매매 화면에서 확인하고 주문 전 슬리피지 추정을 가능하게 한다.
- 실제 작업:
  - `KisClient.get_order_book(symbol, market="J")` 추가.
  - `estimate_order_book_slippage(levels, side, quantity, reference_price)` 추가.
  - `app/ui/backend.py`에 `order_book_snapshot`, `order_book_levels_df`, `order_book_df` 추가.
  - `app/ui/views/trade.py` 매매 화면에 호가창/예상평균가/충족수량/미충족수량/슬리피지 metric 추가.
  - `docs/KIS_API_SPEC.md`, `docs/references/kis/PROJECT-MAPPING.md`, `docs/BACKLOG.md` 갱신.
- 결과: REST snapshot 경로는 paper/prod 공통 TR `FHKST01010200`를 사용하며, 실시간 연동 옵션은 TASK-010의 `KisWebSocketClient.subscribe_order_book()`(`H0STASP0`)과 공존한다.
- 변경 파일:
  - `app/brokers/kis/kis_client.py`
  - `app/ui/backend.py`
  - `app/ui/views/trade.py`
  - `tests/unit/test_kis_order_book.py`
  - `tests/unit/test_backend_order_book.py`
  - `tests/unit/test_trade_order_book_view.py`
  - `docs/KIS_API_SPEC.md`
  - `docs/references/kis/PROJECT-MAPPING.md`
  - `docs/BACKLOG.md`
- 검증:
  - `python -m py_compile app\brokers\kis\kis_client.py app\ui\backend.py app\ui\views\trade.py tests\unit\test_kis_order_book.py tests\unit\test_backend_order_book.py tests\unit\test_trade_order_book_view.py` — 통과
  - `pytest tests\unit\test_kis_order_book.py tests\unit\test_backend_order_book.py tests\unit\test_trade_order_book_view.py` — 9 passed
  - `pytest tests\unit\test_kis_order_book.py tests\unit\test_backend_order_book.py tests\unit\test_trade_order_book_view.py tests\unit\test_kis_ws_client.py tests\unit\test_kis_sector_price.py tests\unit\test_backend_sector_performance.py` — 24 passed
  - `pytest tests` — 356 passed
  - `python scripts\validate_task_schema.py` — OK
  - `python scripts\generate_views.py --check` — OK
  - `python scripts\check_agent_docs.py` — OK, 0 errors / 124 warnings
